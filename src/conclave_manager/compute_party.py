import os
import ast
import pystache
import json
import urllib3

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import DynamicApiError
from base64 import b64encode, b64decode

urllib3.disable_warnings()


class ComputeParty:
    """
    Represents one party in a computation.
    Generates all Kubernetes objects.
    """

    def __init__(
            self, pid, all_pids, compute_id, protocol, app, protocol_config, jiff_server_ip, data_source="dataverse"
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
            "ccd-one_in1.csv": "ccd-one",
            "ccd-two_in2.csv": "ccd-two"
        }
        self.endpoints = self.get_endpoint()
        self.namespace = self.set_namespace()
        self.jiff_server_ip = jiff_server_ip

        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.name = "conclave-{0}-{1}".format(compute_id, str(pid))
        self.config_map_name = "conclave-{0}-{1}-map".format(compute_id, str(pid))

        self.protocol = protocol
        self.protocol_main = self.gen_protocol_main()
        self.protocol_for_policy = self.gen_protocol_for_policy()
        self.conclave_config = self.gen_conclave_config()
        self.config_map_body = self.define_config_map()
        self.pod_body = self.define_pod()
        self.service_body = self.define_service()
        self.oc_service_body = self.define_oc_service()
        self.route_body = self.define_route()

    def set_mpc_backend(self):

        if len(self.config["data"]["endpoints"]) == 2:
            self.app.logger.info("Using Obliv-C backend for MPC computation.\n")
            return "obliv-c"
        else:
            self.app.logger.info("Using JIFF backend for MPC computation.\n")
            return "jiff"

    def get_endpoint(self):

        return self.config["data"]["endpoints"][self.pid - 1]

    def set_namespace(self):
        """
        TODO: this is a hack lookup for resolving namespaces. need to replace
        it with a DB call to resolve dataset ownership to openshift projects
        """

        try:
            namespace = \
                self.namespace_map[
                    "{0}_{1}"
                    .format(self.endpoints["containerName"], self.endpoints["fileName"])]
        except KeyError:
            namespace = "cici"

        return namespace

    @staticmethod
    def format_protocol(protocol):

        ret = []

        for line in protocol.split("\n"):
            ret.append("\t" + line)

        return "\n".join(ret)

    def gen_protocol_for_policy(self):
        """
        Generate protocol code that gets passed to the policy engine.

        TODO: fetch policy and pass to template
        """

        if self.config['protocol']['format'] == 'b64':
            protocol_decoded = self.format_protocol(b64decode(self.protocol).decode())
        else:
            protocol_decoded = self.format_protocol(self.protocol)

        params = {
            "PROTOCOL": protocol_decoded,
            "PID": int(self.pid),
            "POLICY": dict()
        }

        data_template = open("{}/protocol_for_policy.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        self.app.logger.info("CC protocol for policy engine: \n{}\n".format(rendered))

        return b64encode(rendered.encode()).decode()

    def gen_protocol_main(self):
        """
        Generate protocol code that will be executed if the workflow passes the policy engine.
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

    # def gen_dv_conf(self):
    #     """
    #     Load DV config using my credentials mounted on the pod via a ConfigMap.
    #     Will need to be generalized in the future.
    #     """
    #
    #     params = dict()
    #
    #     params['dv_host'] = \
    #         open("/etc/config/dv_host", "r").read() if self.data_source == "dataverse" else "N/A"
    #     params['dv_token'] = \
    #         open("/etc/config/dv_token", "r").read() if self.data_source == "dataverse" else "N/A"
    #
    #     return params

    def gen_swift_output_conf(self):
        """
        Loads Swift config using either default configuration data
        or from config passed via config.swift_config, if present in the JSON.
        """

        data_template = open("{}/swift_output_config.tmpl".format(self.template_directory), 'r').read()

        params = \
            {
                "PID": self.pid,
                "AUTH_URL": open("/etc/swift-config/mine/auth_url", "r").read(),
                "PROJ_DOMAIN": open("/etc/swift-config/mine/proj_domain", "r").read(),
                "PROJ_NAME": open("/etc/swift-config/mine/proj_name", "r").read(),
                "USER_NAME": open("/etc/swift-config/mine/user_name", "r").read(),
                "PASS": open("/etc/swift-config/mine/pass", "r").read(),
                "DEST_CONTAINER_NAME": self.compute_id
            }

        rendered = pystache.render(data_template, params)

        return b64encode(rendered.encode()).decode()

    def gen_data_conf(self):

        if self.data_source == "dataverse":

            data_template = open("{}/dv_config.tmpl".format(self.template_directory), 'r').read()

            params = \
                {
                    "PID": self.pid,
                    "SOURCE_ALIAS": self.endpoints['alias'],
                    "DEST_ALIAS": self.endpoints['alias'],
                    "SOURCE_DOI": self.endpoints['doi'],
                    "DV_FILE": self.endpoints['files']
                }

            rendered = pystache.render(data_template, params)

            return b64encode(rendered.encode()).decode()

        elif self.data_source == "swift":

            """
            TODO: PROJ_NAME needs to be configurable, hardcoded now
            """

            data_template = open("{}/swift_input_config.tmpl".format(self.template_directory), 'r').read()

            params = \
                {
                    "PID": self.pid,
                    "PROJ_NAME": "ccs-musketeer-demo",
                    "SOURCE_CONTAINER_NAME": self.endpoints["containerName"],
                    "FILENAME": self.endpoints["fileName"]
                }

            rendered = pystache.render(data_template, params)

            return b64encode(rendered.encode()).decode()

        else:

            self.app.logger.warn("Data source not recognized: {}\n".format(self.data_source))

    def gen_conclave_config(self):
        """
        Generate CC Config JSON.
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
                    "0.0.0.0:8080" if self.pid == 1 else "conclave-{0}-2-route:8080".format(self.compute_id),
                "JIFF_AVAIL": int(self.mpc_backend == "jiff"),
                "PARTY_COUNT": len(self.all_pids),
                "SERVER_SERVICE": self.jiff_server_ip
            }

        data_template = open("{}/conclave_config.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        self.app.logger.info("CC JSON file:\n{}".format(rendered))

        return b64encode(rendered.encode()).decode()

    def resolve_other_party(self, i):

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
                ret_net.append(
                    {"host": "0.0.0.0", "port": 8080}
                )
            else:
                ret_net.append(
                    {"host": "conclave-{0}-{1}-route/"
                        .format(self.compute_id, str(i)), "port": 8080}
                )

        return json.dumps(ret_net)

    def define_config_map(self):
        """
        Populate ConfigMap template.
        """

        name = "conclave-{0}-{1}-map".format(self.compute_id, str(self.pid))

        try:
            in_file = self.endpoints["fileName"]
        except KeyError:
            in_file = ""

        data_params = \
            {
                "NAME": name,
                "FILENAME": in_file,
                "NAMESPACE": self.namespace,
                "PROTOCOL_MAIN": str(self.protocol_main),
                "PROTOCOL_POLICY": str(self.protocol_for_policy),
                "CC-CONF": self.conclave_config,
                "IN-CONF": self.gen_data_conf(),
                "OUT-CONF": self.gen_swift_output_conf()
            }

        data_template = open("{}configmap.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

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
                "IMAGE": "docker.io/bengetch/conclave-jiff:latest" if self.mpc_backend == "jiff"
                else "docker.io/bengetch/conclave-oc:latest"
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
                "COMPUTE_ID": self.compute_id,
                "PORT": 8080
            }

        data_template = open("{}/service.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def define_oc_service(self):
        """
        Populate Service template for CC Pods and MPC backends.
        """

        params = \
            {
                "SERVICE_NAME": "{}-oc-service".format(self.name),
                "APP_NAME": self.name,
                "COMPUTE_ID": self.compute_id,
                "PORT": 5001
            }

        data_template = open("{}/service.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def define_route(self):

        params = {
            "ROUTE_NAME": "{}-route".format(self.name),
            "SERVICE_NAME": "{}-service".format(self.name),
            "COMPUTE_ID": self.compute_id

        }

        data_template = open("{}/route.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    @staticmethod
    def get_client(**kwargs):

        conf = k_client.Configuration()

        for k, v in kwargs.items():
            setattr(conf, k, v)

        k_client.Configuration.set_default(conf)

        k8s_client = k_client.ApiClient(conf)

        return DynamicClient(k8s_client)

    def launch(self):
        """
        Launch all Kubernetes objects.
        """

        tok = open("/var/run/secrets/kubernetes.io/serviceaccount/token", 'r').read()

        token_auth = dict(
            api_key={'authorization': 'Bearer {}'.format(tok)},
            host='https://k-openshift.osh.massopen.cloud:8443',
            verify_ssl=False
        )

        os_client = self.get_client(**token_auth)

        k_config.load_incluster_config()
        kube_client = k_client.CoreV1Api()
        kube_extensions = k_client.ExtensionsV1beta1Api()

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

        # try:
        #     api_response = \
        #         kube_client.create_namespaced_service(self.namespace, body=self.oc_service_body, pretty='true')
        #     self.app.logger.info(
        #         "Service created successfully with response: \n{}\n"
        #             .format(api_response))
        # except ApiException as e:
        #     self.app.logger.error(
        #         "Error creating Service: \n{}\n"
        #             .format(e))

        # try:
        #     api_response = \
        #         kube_extensions.create_namespaced_ingress(self.namespace, body=self.route_body, pretty='true')
        #     self.app.logger.info(
        #         "Route created successfully with response: \n{}\n"
        #             .format(api_response))
        # except ApiException as e:
        #     self.app.logger.error(
        #         "Error creating Route: \n{}\n"
        #             .format(e))

        try:
            route = os_client.resources.get(api_version='v1', kind="Route")
            api_response = route.create(namespace=self.namespace, body=self.route_body)
            self.app.logger.info("Created Route: \n{} \n".format(api_response))
        except DynamicApiError as e:
            self.app.logger.info("Error creating Route: \n{} \n".format(e))

        try:
            api_response = kube_client.create_namespaced_pod(self.namespace, body=self.pod_body, pretty='true')
            self.app.logger.info(
                "Pod created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Pod: \n{}\n"
                    .format(e))

        return
