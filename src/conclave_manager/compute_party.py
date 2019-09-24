import os
import ast
import pystache
import json
import urllib3

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException
from base64 import b64encode, b64decode

urllib3.disable_warnings()


class ComputeParty:
    """
    Represents one party in a computation.
    Generates all Kubernetes objects.
    """

    def __init__(
            self, pid, all_pids, compute_id, protocol, app, protocol_config, jiff_server_ip, data_source="swift"
    ):

        self.pid = pid
        self.all_pids = all_pids
        self.compute_id = compute_id
        self.app = app
        self.data_source = data_source
        self.config = protocol_config
        self.mpc_backend = self.set_mpc_backend()
        # TODO hack that needs to be replaced with a DB
        self.namespace_map = {
            "p-test-one_in1.csv": "ccd-one",
            "p-test-two_in2.csv": "ccd-two"
        }
        self.endpoint = self.get_endpoint()
        self.data_source = self.resolve_data_source()
        self.namespace = self.set_namespace()
        self.jiff_server_ip = jiff_server_ip

        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.name = "conclave-{0}-{1}".format(compute_id, str(pid))
        self.config_map_name = "conclave-{0}-{1}-map".format(compute_id, str(pid))

        self.protocol = protocol
        self.protocol_main = self.gen_protocol_main()
        self.conclave_config = self.gen_conclave_config()
        self.config_map_body = self.define_config_map()
        self.pod_body = self.define_pod()
        self.service_body = self.define_service()
        self.network_policy_body = self.define_network_policy()

    def set_mpc_backend(self):

        if len(self.config["data"]["endpoints"]) == 2:
            self.app.logger.info("Using Obliv-C backend for MPC computation.\n")
            return "obliv-c"
        else:
            self.app.logger.info("Using JIFF backend for MPC computation.\n")
            return "jiff"

    def get_endpoint(self):

        return self.config["data"]["endpoints"][self.pid - 1]

    def resolve_data_source(self):

        if self.endpoint["backend"].lower() == "swift":
            return "swift"
        elif self.endpoint["backend"].lower() == "dataverse":
            return "dataverse"
        else:
            raise Exception("Data backend not recognized: {}\n".format(self.endpoint["backend"]))

    def set_namespace(self):
        """
        TODO: this is a hack lookup for resolving namespaces. need to replace
        it with a DB call to resolve dataset ownership to openshift projects
        """

        if self.data_source == "swift":
            map_key = "{0}_{1}".format(self.endpoint["containerName"], self.endpoint["fileName"])
        elif self.data_source == "dataverse":
            map_key = "{0}_{1}".format(self.endpoint["alias"], self.endpoint["fileName"])
        else:
            raise Exception("Data backend not recognized: {}\n".format(self.endpoint["backend"]))

        try:
            namespace = self.namespace_map[map_key]
        except KeyError:
            namespace = "cici"

        return namespace

    @staticmethod
    def format_protocol(protocol):
        """
        Format protocol code with tabs before injecting into template.
        """

        ret = []

        for line in protocol.split("\n"):
            ret.append("\t" + line)

        return "\n".join(ret)

    def gen_protocol_main(self):
        """
        Generate protocol code.
        """

        if self.config['protocol']['format'] == 'b64':
            protocol_decoded = self.format_protocol(b64decode(self.protocol).decode())
        else:
            protocol_decoded = self.format_protocol(self.protocol)

        params = {
            "PROTOCOL": protocol_decoded,
            "MPC_FRAMEWORK": self.mpc_backend
        }

        data_template = open("{}/protocol_main.tmpl".format(self.template_directory), 'r').read()
        rendered = pystache.render(data_template, params)

        self.app.logger.info("CC protocol: \n{}\n".format(rendered))

        return b64encode(rendered.encode()).decode()

    def gen_conclave_config(self):
        """
        Generate CC Config JSON.

        TODO: configurable PROJ_NAME (will probably need to resolve with a db call to the input data)
        """

        net_list = self.gen_net_config()

        params = \
            {
                "PID": self.pid,
                "ALL_PIDS": self.all_pids,
                "WORKFLOW_NAME": "conclave-{}".format(self.compute_id),
                "NET_CONFIG": net_list,
                "SPARK_AVAIL": 0,
                "SPARK_IP_PORT": "N/A",
                "OC_AVAIL": int(self.mpc_backend == "obliv-c"),
                "OC_IP_PORT":
                    "0.0.0.0:5001" if self.pid == 1 else "conclave-{0}-1-service.{1}.svc.cluster.local:5001"
                    .format(self.compute_id, self.resolve_other_party(1)),
                "JIFF_AVAIL": int(self.mpc_backend == "jiff"),
                "PARTY_COUNT": len(self.all_pids),
                "SERVER_SERVICE": self.jiff_server_ip,
                "DATA_BACKEND": self.data_source,
                "PROJ_NAME": "ccs-musketeer-demo",
                "SOURCE_CONTAINER_NAME": self.endpoint["containerName"] if self.data_source == "swift" else "",
                "FILENAME": self.endpoint["fileName"],
                "OUTPUT_AUTH_URL": open("/etc/swift-auth/auth_url", "r").read(),
                "OUTPUT_PROJ_DOMAIN": open("/etc/swift-auth/proj_domain", "r").read(),
                "OUTPUT_PROJ_NAME": open("/etc/swift-auth/proj_name", "r").read(),
                "OUTPUT_USER_NAME": open("/etc/swift-auth/username", "r").read(),
                "OUTPUT_PASS": open("/etc/swift-auth/password", "r").read(),
                "DEST_CONTAINER_NAME": self.compute_id,
                "SOURCE_ALIAS": self.endpoint["alias"] if self.data_source == "dataverse" else "",
                "SOURCE_DOI": self.endpoint["doi"] if self.data_source == "dataverse" else ""
            }

        data_template = open("{}/conclave_config.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        self.app.logger.info("CC JSON file:\n{}".format(rendered))

        return b64encode(rendered.encode()).decode()

    def resolve_other_party(self, i):
        """
        Hack to resolve namespaces for testing.
        TODO: update once net policy objects work.
        """

        file_data = self.config["data"]["endpoints"][i - 1]

        try:
            namespace_key = self.namespace_map["{0}_{1}".format(file_data["containerName"], file_data["fileName"])]
        except KeyError:
            namespace_key = "cici"

        return namespace_key

    def gen_net_config(self):
        """
        Generate CC Net Config string that gets inserted into CC Config JSON.
        """

        ret_net = []

        for i in self.all_pids:
            if i == self.pid:
                ret_net.append({"host": "0.0.0.0", "port": 5000})
            else:
                ret_net.append({"host": "conclave-{0}-{1}-service.{2}.svc.cluster.local"
                               .format(self.compute_id, str(i), self.resolve_other_party(i)), "port": 5000})

        return json.dumps(ret_net)

    def define_config_map(self):
        """
        Populate ConfigMap template.
        """

        data_params = \
            {
                "NAME": "conclave-{0}-{1}-map".format(self.compute_id, str(self.pid)),
                "NAMESPACE": self.namespace,
                "PROTOCOL_MAIN": str(self.protocol_main),
                "CC-CONF": self.conclave_config
            }

        data_template = open("{}configmap.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def setup_data_params(self):
        """
        Construct key/path values for input data configmap on pod.
        """

        if self.data_source == "swift":
            return [
                {"key": "osAuthUrl", "path": "auth_url"},
                {"key": "username", "path": "username"},
                {"key": "password", "path": "password"}
            ]

        elif self.data_source == "dataverse":
            return [
                {"key": "host", "path": "dv_host"},
                {"key": "token", "path": "dv_token"}
            ]
        else:
            raise Exception("Data backend not recognized: {}\n".format(self.data_source))

    def define_pod(self):
        """
        Populate Pod template.
        """

        params = \
            {
                "POD_NAME": self.name,
                "CONFIGMAP_NAME": self.config_map_name,
                "NAMESPACE": self.namespace,
                "COMPUTE_ID": self.compute_id,
                "IMAGE": "docker.io/bengetch/conclave:jiff" if self.mpc_backend == "jiff"
                else "docker.io/bengetch/conclave:oc",
                "BACKEND": self.data_source,
                "BACKEND_PARAMS": self.setup_data_params()
            }

        data_template = open("{}/pod.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def define_service(self):
        """
        Populate Service template for CC Pods and MPC backends.
        """

        params = \
            {
                "SERVICE_NAME": "{}-service".format(self.name),
                "APP_NAME": self.name,
                "COMPUTE_ID": self.compute_id
            }

        data_template = open("{}/service.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def define_network_policy(self):

        params = \
            {
                "NAME": self.name,
                "POD_NAME": self.name,
                "OTHER_PROJECT": "ccd-two" if self.namespace == "ccd-one" else "ccd-one"
            }

        data_template = open("{}/network_policy.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def launch(self):
        """
        Launch all Kubernetes objects.
        """

        k_config.load_incluster_config()
        kube_client = k_client.CoreV1Api()
        # kube_client_networking = k_client.NetworkingV1Api()

        try:
            api_response = \
                kube_client.create_namespaced_config_map(self.namespace, self.config_map_body, pretty='true')
            self.app.logger.info(
                "ConfigMap created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating ConfigMap: \n{}\n"
                    .format(e))

        try:
            api_response = \
                kube_client.create_namespaced_service(self.namespace, body=self.service_body, pretty='true')
            self.app.logger.info(
                "Service created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Service: \n{}\n"
                    .format(e))

        try:
            api_response = kube_client.create_namespaced_pod(self.namespace, body=self.pod_body, pretty='true')
            self.app.logger.info(
                "Pod created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Pod: \n{}\n"
                    .format(e))

        # try:
        #     api_response = kube_client_networking.create_namespaced_network_policy(
        #         self.namespace, body=self.network_policy_body, pretty='true')
        #     self.app.logger.info(
        #         "NetworkPolicy successfully created with response: \n{}\n"
        #             .format(api_response))
        # except ApiException as e:
        #     self.app.logger.error(
        #         "Error creating NetworkPolicy: \n{}\n"
        #             .format(e))

        return
