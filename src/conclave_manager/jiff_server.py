import os
import ast
import pystache
import socket

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException


class JiffServer:
    """
    Generates and launches a Jiff server.
    """

    def __init__(self, app, compute_id, protocol_config):

        self.app = app
        self.compute_id = compute_id
        self.namespace = self.set_namespace(protocol_config)

        self.name = "jiff-server-{0}".format(compute_id)
        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))

        self.pod_body = self.define_pod()
        self.service_body = self.define_service()

        self.launch_server()

    @staticmethod
    def set_namespace(config):

        try:
            namespace = config["namespace"]
        except KeyError:
            namespace = 'cici'

        return namespace

    def query_server_ip(self):
        """
        Attempt to query IP address of server.

        <http>://<IP address> string is necessary for http.Server.listen() function in Jiff server.js file.
        """

        self.app.logger.info("Querying IP address of Jiff Server")

        try:
            ip = socket.gethostbyname("{}-service".format(self.name))
        except socket.gaierror:
            ip = None

        return ip

    def launch_server(self):
        """
        Launch JiffServer objects.
        """

        if self.pod_body is None:
            self.define_pod()

        if self.service_body is None:
            self.define_service()

        k_config.load_incluster_config()
        kube_client = k_client.CoreV1Api()

        try:
            api_response = kube_client.create_namespaced_service(self.namespace, body=self.service_body, pretty='true')
            self.app.logger.info(
                "Jiff Server Service created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Jiff Server Service: \n{}\n"
                    .format(e))

        try:
            api_response = kube_client.create_namespaced_pod(self.namespace, body=self.pod_body, pretty='true')
            self.app.logger.info(
                "Jiff Server Pod created successfully with response: \n{}\n"
                    .format(api_response))
        except ApiException as e:
            self.app.logger.error(
                "Error creating Jiff Server Pod: \n{}\n"
                    .format(e))

        return

    def define_pod(self):
        """
        Populate JiffServer Pod template.
        """

        params = \
            {
                "POD_NAME": self.name,
                "NAMESPACE": self.namespace
            }

        data_template = open("{}/jiff_server_pod.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)

    def define_service(self):
        """
        Populate Service template for JiffServer Service
        """

        params = \
            {
                "SERVICE_NAME": "{}-service".format(self.name),
                "APP_NAME": self.name,
                "PORT": 9000
            }

        data_template = open("{}/service.tmpl".format(self.template_directory), 'r').read()

        rendered = pystache.render(data_template, params)

        return ast.literal_eval(rendered)
