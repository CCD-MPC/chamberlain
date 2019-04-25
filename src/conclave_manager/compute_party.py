import os
import ast
import pystache
import json

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException
from base64 import b64encode, b64decode


class ComputeParty:
    """
    Represents one party in a computation.
    Generates all Kubernetes objects.
    """

    def __init__(self, pid, all_pids, compute_id, protocol, app, protocol_config, jiff_server_ip, data_source="dataverse"):

        self.pid = pid
        self.all_pids = all_pids
        self.compute_id = compute_id
        self.app = app
        self.data_source = data_source
        self.config = protocol_config
        self.mpc_backend = self.set_mpc_backend()
        self.namespace = self.set_namespace(protocol_config)
        self.endpoints = self.get_endpoint()
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

    def set_mpc_backend(self):

        if len(self.config["data"]["endpoints"]) == 2:
            self.app.logger.info("Using Obliv-C backend for MPC computation.\n")
            return "obliv-c"
        else:
            self.app.logger.info("Using JIFF backend for MPC computation.\n")
            return "jiff"

    def get_endpoint(self):

        return self.config["data"]["endpoints"][self.pid - 1]

    @staticmethod
    def set_namespace(config):

        try:
            namespace = config["namespace"]
        except KeyError:
            namespace = 'cici'

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

    def gen_swift_conf(self):
        """
        Loads Swift config using either default configuration data
        or from config passed via config.swift_config, if present in the JSON.
        """

        params = dict()

        try:
            party_id = self.endpoints["partyId"]
        except KeyError:
            party_id = "mine"

        self.app.logger.info(
            "Loading Swift credentials for user {}.\n".format(party_id)
        )
        params["auth_url"] = \
            open("/etc/swift-config/{}/auth_url".format(party_id), "r").read() if self.data_source == 'swift' else 'N/A'
        params["proj_domain"] = \
            open("/etc/swift-config/{}/proj_domain".format(party_id), "r").read() if self.data_source == 'swift' else 'N/A'
        params["proj_name"] = \
            open("/etc/swift-config/{}/proj_name".format(party_id), "r").read() if self.data_source == 'swift' else 'N/A'
        params["user_name"] = \
            open("/etc/swift-config/{}/user_name".format(party_id), "r").read() if self.data_source == 'swift' else 'N/A'
        params["pass"] = \
            open("/etc/swift-config/{}/pass".format(party_id), "r").read() if self.data_source == 'swift' else 'N/A'

        params["container_name"] = \
            self.endpoints["containerName"] if self.data_source == 'swift' else "N/A"
        params["swift_files"] = \
            self.endpoints["files"] if self.data_source == 'swift' else 'N/A'
        params["filename"] = self.endpoints["fileName"] if self.data_source == 'swift' else 'N/A'

        return params

    def gen_dv_conf(self):
        """
        Load DV config using my credentials mounted on the pod via a ConfigMap.
        Will need to be generalized in the future.
        """

        params = dict()

        params['dv_host'] = \
            open("/etc/config/dv_host", "r").read() if self.data_source == "dataverse" else "N/A"
        params['dv_token'] = \
            open("/etc/config/dv_token", "r").read() if self.data_source == "dataverse" else "N/A"
        params['dv_alias'] = \
            self.endpoints['alias'] if self.data_source == "dataverse" else "N/A"
        params["doi"] = \
            self.endpoints["doi"] if self.data_source == "dataverse" else "N/A"
        params['dv_file'] = \
            self.endpoints["files"] if self.data_source == "dataverse" else "N/A"

        return params

    def set_oc_conf(self):

        if self.mpc_backend == "obliv-c":
            if self.pid == 1:
                return "conclave-{0}-2-service:5000".format(self.compute_id)
            else:
                return "conclave-{0}-1-service:5000".format(self.compute_id)
        else:
            return "N/A"

    def gen_conclave_config(self):
        """
        Generate CC Config JSON.
        """

        net_list = self.gen_net_config()
        swift_params = self.gen_swift_conf()
        dv_params = self.gen_dv_conf()
        oc_conf = self.set_oc_conf()

        params = \
            {
                "PID": self.pid,
                "ALL_PIDS": self.all_pids,
                "WORKFLOW_NAME": "conclave-{}".format(self.compute_id),
                "NET_CONFIG": net_list,
                "SPARK_AVAIL": 0,
                "SPARK_IP_PORT": "N/A",
                "OC_AVAIL": int(self.mpc_backend == "obliv-c"),
                "OC_IP_PORT": oc_conf,
                "JIFF_AVAIL": int(self.mpc_backend == "jiff"),
                "PARTY_COUNT": len(self.all_pids),
                "SERVER_SERVICE": self.jiff_server_ip,
                "DATA_BACKEND": self.data_source,
                "OS_AUTH": swift_params["auth_url"],
                "USERNAME": swift_params["user_name"],
                "PASSWORD": swift_params["pass"],
                "PROJ_DOMAIN": swift_params["proj_domain"],
                "PROJ_NAME": swift_params["proj_name"],
                "SOURCE_CONTAINER_NAME": swift_params["container_name"],
                "SWIFT_FILES": swift_params["swift_files"],
                "FILENAME": swift_params["filename"],
                "DEST_CONTAINER_NAME": self.compute_id,
                "DV_HOST": dv_params["dv_host"],
                "DV_TOKEN": dv_params["dv_token"],
                "SOURCE_ALIAS": dv_params["dv_alias"],
                "SOURCE_DOI": dv_params["doi"],
                "DV_FILE": dv_params["dv_file"],
                "OUTPUT_AUTHOR": "test author",
                "DEST_ALIAS": dv_params["dv_alias"]
            }

        data_template = open("{}/conclave_config.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        self.app.logger.info("CC JSON file:\n{}".format(rendered))

        return b64encode(rendered.encode()).decode()

    def gen_net_config(self):
        """
        Generate CC Net Config string that gets inserted into CC Config JSON.
        """

        ret_net = []

        for i in self.all_pids:
            if i == self.pid:
                ret_net.append({"host": "0.0.0.0", "port": 5000})
            else:
                ret_net.append({"host": "conclave-{0}-{1}-service".format(self.compute_id, str(i)), "port": 5000})

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
                "CONF": self.conclave_config
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

        svc = "{}-service".format(self.name)
        port = 5000

        params = \
            {
                "SERVICE_NAME": svc,
                "APP_NAME": self.name,
                "PORT": port,
                "COMPUTE_ID": self.compute_id
            }

        data_template = open("{}/service.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def launch(self):
        """
        Launch all Kubernetes objects.
        """

        k_config.load_incluster_config()
        kube_client = k_client.CoreV1Api()

        try:
            api_response = kube_client.create_namespaced_config_map(self.namespace, self.config_map_body, pretty='true')
            self.app.logger.info(
                "ConfigMap created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating ConfigMap: \n{}\n"
                    .format(e))

        try:
            api_response = kube_client.create_namespaced_service(self.namespace, body=self.service_body, pretty='true')
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

        return
