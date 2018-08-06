import os
import ast
import time
import pystache

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException


class ComputeParty:

    def __init__(self, pid, all_pids, timestamp, protocol, app):

        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.pid = pid
        self.all_pids = all_pids
        self.timestamp = timestamp
        self.app = app

        self.name = "conclave-{0}-{1}".format(timestamp, str(pid))
        self.config_map_name = "conclave-{0}-{1}-map".format(timestamp, str(pid))

        self.protocol = protocol
        self.conclave_config = self.gen_net_config()
        self.config_map_body = self.define_config_map()
        self.pod_body = self.define_pod()
        self.service_body = self.define_service()

    def gen_conclave_config(self):
        """
        Generate CC Config yaml.
        """

        net_str = self.gen_net_config()

        params = \
            {
                "PID": self.pid,
                "ALL_PIDS": ", ".join(i for i in self.all_pids),
                "WORKFLOW_NAME": "conclave-{}".format(self.timestamp),
                "NET_CONFIG": net_str
            }

        data_template = open("{}/conclave_config.tmpl".format(self.template_directory), 'r').read()

        return pystache.render(data_template, params)

    def gen_net_config(self):
        """
        Generate CC Net Config string that gets inserted into CC Concfig yaml.
        """

        net_str = ""

        for i in self.all_pids:
            if i == self.pid:
                net_str += "\t\t-host: 0.0.0.0\n\t\tport: 5000\n"
            else:
                net_str += "\t\t-host: {0}-{1}\n\t\tport: 5000\n"\
                    .format(self.timestamp, str(i))

        return net_str

    def define_config_map(self):
        """
        Populate ConfigMap template.
        """

        name = "conclave-{0}-{1}-map".format(self.timestamp, str(self.pid))
        namespace = "cici"

        data_params = \
            {
                "NAME": name,
                "NAMESPACE": namespace,
                "PROTOCOL": self.protocol,
                "CONF": self.conclave_config
            }

        data_template = "{}/configmap.tmpl".format(self.template_directory)

        return ast.literal_eval(pystache.render(data_template, data_params))

    def define_pod(self):
        """
        Populate Pod template.
        """

        params = \
            {
                "POD_NAME": self.name,
                "CONFIGMAP_NAME": self.config_map_name
            }

        data_template = open("{}/pod.tmpl".format(self.template_directory), 'r').read()

        self.pod_body = ast.literal_eval(pystache.render(data_template, params))

        return self

    def define_service(self):
        """
        Populate Service template.
        """

        params = \
            {
                "SERVICE_NAME": self.name
            }

        data_template = open("{}/service.tmpl".format(self.template_directory), 'r').read()

        self.service_body = ast.literal_eval(pystache.render(data_template, params))

        return self

    def launch(self):
        """
        Launch all Kubernetes objects.
        """

        k_config.load_incluster_config()
        kube_client = k_client.CoreV1Api()

        try:
            api_response = kube_client.create_namespaced_config_map('cici', self.config_map_body, pretty='true')
            self.app.logger.info(
                "ConfigMap created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating ConfigMap: \n{}\n"
                    .format(e))

        try:
            api_response = kube_client.create_namespaced_service('cici', body=self.service_body, pretty='true')
            self.app.logger.info(
                "Service created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Service: \n{}\n"
                    .format(e))

        try:
            api_response = kube_client.create_namespaced_pod('cici', body=self.pod_body, pretty='true')
            self.app.logger.info(
                "Pod created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Pod: \n{}\n"
                    .format(e))

        return


class ConclaveManager:

    def __init__(self, json_data, app):

        self.app = app
        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.protocol_config = json_data

        self.protocol = self.load_protocol()
        self.compute_parties = self.create_compute_parties()

    def load_protocol(self):
        """
        TODO: Will later load this from self.protocol_config.protocol
        """

        mock_data_directory = "{}/mock_data".format(os.path.dirname(os.path.realpath(__file__)))
        self.protocol = open("{}/protocol.py".format(mock_data_directory)).read()

        return self

    def create_compute_parties(self):
        """
        Init all compute parties.
        """

        timestamp = str(int(round(time.time() * 1000)))
        all_pids = list(range(1, len(self.protocol_config['config']['dataRows']) + 1))
        compute_parties = []

        self.app.logger.info(
            "Creating Conclave job templates for {} parties"
                .format(str(len(all_pids))))

        # TODO: will need to pass swift endpoints here
        for i in all_pids:
            compute_parties.append(ComputeParty(i, all_pids, timestamp, self.protocol, self.app))

        return compute_parties

    def launch_all_parties(self):
        """
        Create ConfigMap, Services, and Pod for each compute party & launch.
        """

        if self.compute_parties is None:
            self.create_compute_parties()

        self.app.logger.info(
            "Launching Conclave pods for the following compute parties:\n{}"
                .format("\n".join(job.name for job in self.compute_parties)))

        for party in self.compute_parties:
            party.launch()

    def run(self):
        """
        Wraps main class methods.
        """

        self.create_compute_parties()
        self.launch_all_parties()





