import os
import ast
import pystache
import json
import sys

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException
from base64 import b64encode


class ComputeParty:
    """
    Represents one party in a computation.
    Generates all Kubernetes objects.
    """

    def __init__(self, pid, all_pids, timestamp, protocol, app, protocol_config, jiff_server_ip, data_source="dataverse"):

        self.pid = pid
        self.all_pids = all_pids
        self.timestamp = timestamp
        self.app = app
        self.config = protocol_config
        self.namespace = self.set_namespace(protocol_config)
        self.endpoints = self.get_endpoints(data_source)
        self.jiff_server_ip = jiff_server_ip
        self.data_source = data_source

        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.name = "conclave-{0}-{1}".format(timestamp, str(pid))
        self.config_map_name = "conclave-{0}-{1}-map".format(timestamp, str(pid))

        self.protocol = protocol
        self.protocol_for_policy = self.gen_protocol_for_policy(self.protocol)
        self.protocol_main = self.gen_protocol_main(self.protocol)
        self.conclave_config = self.gen_conclave_config()
        self.config_map_body = self.define_config_map()
        self.pod_body = self.define_pod()
        self.service_body = self.define_service()

    def get_endpoints(self, data_source):

        if data_source == "swift":
            return self.config["swift"]["endpoints"][self.pid - 1]
        elif data_source == "dataverse":
            return self.config["dataverse"]["endpoints"][self.pid - 1]
        else:
            self.app.logger.info("Data source not recognized: {}\n".format(data_source))
            sys.exit(1)

    @staticmethod
    def set_namespace(config):

        try:
            namespace = config["namespace"]
        except KeyError:
            namespace = 'cici'

        return namespace

    def gen_protocol_for_policy(self, protocol):
        """
        Generate protocol code that gets passed to the policy engine.

        TODO: fetch policy and pass to template
        """

        params = {
            "PROTOCOL": protocol,
            "PID": int(self.pid),
            "POLICY": dict()
        }

        data_template = open("{}/protocol_for_policy.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return b64encode(rendered.encode()).decode()

    def gen_protocol_main(self, protocol):
        """
        Generate protocol code that will be executed if the workflow passes the policy engine.
        """

        params = {
            "PROTOCOL": protocol
        }

        # TODO: change to different protocol template once we decide on how we want to pass workflows
        # data_template = open("{}/protocol_main.tmpl".format(self.template_directory), 'r').read()
        data_template = open("{}/protocol.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        self.app.logger.info("CC protocol: \n{}".format(rendered))

        return b64encode(rendered.encode()).decode()

    def gen_swift_conf(self):
        """
        Loads Swift config using either default configuration data
        or from config passed via config.swift_config, if present in the JSON.
        """

        params = dict()

        try:
            params["auth_url"] = self.config["swift"]["authUrl"]
            params["proj_domain"] = self.config["swift"]["projDomain"]
            params["proj_name"] = self.config["swift"]["projName"]
            params["user_name"] = self.config["swift"]["username"]
            params["pass"] = self.config["swift"]["password"]
        except KeyError:
            self.app.logger.info(
                "No Swift Authorization config passed. Reading Swift project info from default configuration.\n"
            )
            params["auth_url"] = \
                open("/etc/config/auth_url", "r").read() if self.data_source == 'swift' else 'N/A'
            params["proj_domain"] = \
                open("/etc/config/proj_domain", "r").read() if self.data_source == 'swift' else 'N/A'
            params["proj_name"] = \
                open("/etc/config/proj_name", "r").read() if self.data_source == 'swift' else 'N/A'
            params["user_name"] = \
                open("/etc/config/user_name", "r").read() if self.data_source == 'swift' else 'N/A'
            params["pass"] = \
                open("/etc/config/pass", "r").read() if self.data_source == 'swift' else 'N/A'

        params["container_name"] = \
            self.endpoints["containerName"] if self.data_source == 'swift' else "N/A"
        params["swift_file"] = \
            self.endpoints["file"] if self.data_source == 'swift' else 'N/A'

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

    def gen_conclave_config(self):
        """
        Generate CC Config yaml.
        """

        net_list = self.gen_net_config()
        swift_params = self.gen_swift_conf()
        dv_params = self.gen_dv_conf()

        params = \
            {
                "PID": self.pid,
                "ALL_PIDS": self.all_pids,
                "WORKFLOW_NAME": "conclave-{}".format(self.timestamp),
                "NET_CONFIG": net_list,
                "SPARK_AVAIL": 0,
                "SPARK_IP_PORT": "N/A",
                "OC_AVAIL": 0,
                "OC_IP_PORT": "N/A",
                "JIFF_AVAIL": 1,
                "PARTY_COUNT": len(self.all_pids),
                "SERVER_SERVICE": self.jiff_server_ip,
                "DATA_BACKEND": self.data_source,
                "OS_AUTH": swift_params["auth_url"],
                "USERNAME": swift_params["user_name"],
                "PASSWORD": swift_params["pass"],
                "PROJ_DOMAIN": swift_params["proj_domain"],
                "PROJ_NAME": swift_params["proj_name"],
                "SOURCE_CONTAINER_NAME": swift_params["container_name"],
                "SWIFT_FILE": swift_params["swift_file"],
                "DEST_CONTAINER_NAME": swift_params["container_name"],
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
                ret_net.append({"host": "conclave-{0}-{1}-service".format(self.timestamp, str(i)), "port": 5000})

        return json.dumps(ret_net)

    def define_config_map(self):
        """
        Populate ConfigMap template.
        """

        name = "conclave-{0}-{1}-map".format(self.timestamp, str(self.pid))

        data_params = \
            {
                "NAME": name,
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
                "NAMESPACE": self.namespace
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
                "PORT": port
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
