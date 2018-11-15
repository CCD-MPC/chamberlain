import os
import json
import ast
import pystache

from kubernetes import config as k_config
from kubernetes import client as k_client
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import DynamicApiError
from subprocess import call


class ConclaveWebInstaller:
    """
    Defines and launches all objects associated with C2D.

    TODO:
        - create DB vol (pending persistent volume creation on DC)
    """

    def __init__(self, with_swift=True):

        self.config = self.load_config()
        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))

        self.with_swift = with_swift

        self.sa_body = self.define_service_account()
        self.swift_config_map_body = self.define_swift_config_map()
        self.deployment_body = self.define_deployment_config()
        self.service_body = self.define_service()
        self.route_body = self.define_route()

    @staticmethod
    def load_config():

        with open("{}/conf/conf.json".format(os.path.dirname(os.path.realpath(__file__))), 'r') as f:
            conf = json.load(f)

        return conf

    def create_secret(self):
        """
        Create generic secret from Kube config file
        """

        call(["/bin/bash", 'create_secret.sh', self.config['namespace']])


    @staticmethod
    def define_service_account():
        """
        Create Service Account body
        """

        sa_body = k_client.V1ServiceAccount(metadata={"name": "cw-svc"})

        return sa_body

    def define_swift_config_map(self):
        """
        Populate ConfigMap template
        """

        data_params = {
            "NAMESPACE": self.config["namespace"],
            "OSAUTHURL": self.config["swift_conf"]["osAuthUrl"],
            "OSPROJDOMAIN": self.config["swift_conf"]["osProjectDomain"],
            "OSPROJNAME": self.config["swift_conf"]["osProjectName"],
            "USERNAME": self.config["swift_conf"]["username"],
            "PASSWORD": self.config["swift_conf"]["password"]
        }

        data_template = open("{}configmap.tmpl".format(self.template_directory), 'r').read()
        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def define_service(self):

        data = open("{}service.tmpl".format(self.template_directory), 'r').read()

        return ast.literal_eval(data)

    def define_route(self):

        data = open("{}route.tmpl".format(self.template_directory), 'r').read()

        return ast.literal_eval(data)

    def define_deployment_config(self):
        """
        Populate DeploymentConfig template
        """

        data_params = {
            "NAMESPACE": self.config["namespace"]
        }

        data_template = open("{}deployment_config.tmpl".format(self.template_directory), 'r').read()
        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def launch_all(self):
        """
        Launch all objects
        """

        self.create_secret()

        kube_client = k_config.new_client_from_config()
        os_client = DynamicClient(kube_client)

        try:
            sa = os_client.resources.get(api_version='v1', kind="ServiceAccount")
            api_response = sa.create(namespace=self.config['namespace'], body=self.sa_body)
            print("Created Service Account: \n{} \n".format(api_response))
        except DynamicApiError as e:
            print("Error creating Service Account: \n{} \n".format(e))

        try:
            config_map = os_client.resources.get(api_version='v1', kind="ConfigMap")
            api_response = config_map.create(namespace=self.config['namespace'], body=self.swift_config_map_body)
            print("Created Swift ConfigMap: \n{} \n".format(api_response))
        except DynamicApiError as e:
            print("Error creating Swift ConfigMap: \n{} \n".format(e))

        try:
            depl = os_client.resources.get(api_version='v1', kind="DeploymentConfig")
            api_response = depl.create(namespace=self.config['namespace'], body=self.deployment_body)
            print("Created DeploymentConfig: \n{} \n".format(api_response))
        except DynamicApiError as e:
            print("Error creating DeploymentConifg: \n{} \n".format(e))

        try:
            service = os_client.resources.get(api_version='v1', kind="Service")
            api_response = service.create(namespace=self.config['namespace'], body=self.service_body)
            print("Created Service: \n{} \n".format(api_response))
        except DynamicApiError as e:
            print("Error creating Service: \n{} \n".format(e))

        try:
            route = os_client.resources.get(api_version='v1', kind="Route")
            api_response = route.create(namespace=self.config['namespace'], body=self.route_body)
            print("Created Route: \n{} \n".format(api_response))
        except DynamicApiError as e:
            print("Error creating Route: \n{} \n".format(e))

        return










