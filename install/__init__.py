import os
import json
import ast
import pystache

from kubernetes import config as k_config
from kubernetes import client as k_client
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import DynamicApiError
from subprocess import call


class ChamberlainInstaller:
    """
    Defines and launches all objects associated with C2D.
    """

    def __init__(self, with_swift=True, with_dv=True, with_vol=False, minishift=False):

        self.config = self.load_config()
        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))

        self.with_swift = with_swift
        self.with_dv = with_dv
        self.with_vol = with_vol
        self.minishift = minishift

        self.sa_body = None
        self.swift_config_map_body = None
        self.dv_config_map_body = None
        self.deployment_body = None
        self.service_body = None
        self.route_body = None
        self.db_body = None

    def define_all_server_objects(self):
        """
        Define all objects for a Chamberlain server install.
        """

        self.sa_body = self.define_service_account()
        self.swift_config_map_body = self.define_swift_config_map()
        self.dv_config_map_body = self.define_dv_config_map()
        self.deployment_body = self.define_deployment_config()
        self.service_body = self.define_service()
        self.route_body = self.define_route()
        self.db_body = self.define_db()

        return self

    def define_all_client_objects(self):
        """
        Define configmaps for a Chamberlain client install.
        """

        if self.with_swift:
            self.swift_config_map_body = self.define_swift_config_map()
        if self.with_dv:
            self.dv_config_map_body = self.define_dv_config_map()

        return self

    @staticmethod
    def load_config():
        """
        Load config file
        """

        with open("{}/conf/conf.json".format(os.path.dirname(os.path.realpath(__file__))), 'r') as f:
            conf = json.load(f)

        return conf

    @staticmethod
    def define_service_account():
        """
        Create Service Account body
        """

        sa_body = k_client.V1ServiceAccount(metadata={"name": "cw-svc", "labels": {"app": "chamberlain"}})

        return sa_body

    def define_swift_config_map(self):
        """
        Populate Swift ConfigMap template
        """

        data_params = {
            "NAMESPACE": self.config["namespace"],
            "OSAUTHURL": self.config["swift_conf"]["osAuthUrl"],
            "OSPROJDOMAIN": self.config["swift_conf"]["osProjectDomain"],
            "OSPROJNAME": self.config["swift_conf"]["osProjectName"],
            "USERNAME": self.config["swift_conf"]["username"],
            "PASSWORD": self.config["swift_conf"]["password"]
        }

        data_template = open("{}swift_cfg_map.tmpl".format(self.template_directory), 'r').read()
        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def define_dv_config_map(self):
        """
        Populate Dataverse ConfigMap template
        """

        data_params = {
            "NAMESPACE": self.config["namespace"],
            "HOST": self.config["dataverse_conf"]["host"],
            "TOKEN": self.config["dataverse_conf"]["token"]
        }

        data_template = open("{}dv_cfg_map.tmpl".format(self.template_directory), 'r').read()
        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def define_service(self):
        """
        Load Service JSON
        """

        data = open("{}service.tmpl".format(self.template_directory), 'r').read()

        return ast.literal_eval(data)

    def define_route(self):
        """
        Load Route JSON
        """

        data_params = {
            "API_VERSION": "route.openshift.io/v1" if self.minishift else "v1"
        }

        data_template = open("{}route.tmpl".format(self.template_directory), 'r').read()
        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def define_db(self):
        """
        Load PersistentVolumeClaim
        """

        data = open("{}db_vol.tmpl".format(self.template_directory), 'r').read()

        return ast.literal_eval(data)

    def define_deployment_config(self):
        """
        Populate DeploymentConfig template
        """

        data_params = {
            "NAMESPACE": self.config["namespace"],
            "API_VERSION": "apps.openshift.io/v1" if self.minishift else "v1"
        }

        if self.with_vol:
            if self.with_swift and self.with_dv:
                data_template = open(
                    "{}/deployments/with_vol/deployment_config_all.tmpl".format(self.template_directory), 'r').read()
            elif self.with_swift:
                data_template = open(
                    "{}/deployments/with_vol/deployment_config_swift_only.tmpl"
                    .format(self.template_directory), 'r').read()
            elif self.with_dv:
                data_template = open(
                    "{}/deployments/with_vol/deployment_config_dv_only.tmpl".format(self.template_directory), 'r').read()
            else:
                raise Exception("No backend storage data provided. Please provide either Swift or Dataverse config.\n")
        else:
            if self.with_swift and self.with_dv:
                data_template = open(
                    "{}/deployments/without_vol/deployment_config_all.tmpl".format(self.template_directory), 'r').read()
            elif self.with_swift:
                data_template = open(
                    "{}/deployments/without_vol/deployment_config_swift_only.tmpl"
                    .format(self.template_directory), 'r').read()
            elif self.with_dv:
                data_template = open(
                    "{}/deployments/without_vol/deployment_config_dv_only.tmpl"
                    .format(self.template_directory), 'r').read()
            else:
                raise Exception("No backend storage data provided. Please provide either Swift or Dataverse config.\n")
        rendered = pystache.render(data_template, data_params)

        return ast.literal_eval(rendered)

    def build_chamberlain_client(self):
        """
        Build configmaps for chamberlain client.
        """

        self.define_all_client_objects()

        kube_client = k_config.new_client_from_config()
        os_client = DynamicClient(kube_client)

        if self.with_dv:
            try:
                config_map = os_client.resources.get(api_version='v1', kind="ConfigMap")
                api_response = config_map.create(namespace=self.config['namespace'], body=self.dv_config_map_body)
                print("Created Dataverse ConfigMap: \n{} \n".format(api_response))
            except DynamicApiError as e:
                print("Error creating Dataverse ConfigMap: \n{} \n".format(e))

        if self.with_swift:
            try:
                config_map = os_client.resources.get(api_version='v1', kind="ConfigMap")
                api_response = config_map.create(namespace=self.config['namespace'], body=self.swift_config_map_body)
                print("Created Swift ConfigMap: \n{} \n".format(api_response))
            except DynamicApiError as e:
                print("Error creating Swift ConfigMap: \n{} \n".format(e))

    def build_chamberlain_server(self):
        """
        Build all objects for chamberlain server.
        """

        self.define_all_server_objects()

        kube_client = k_config.new_client_from_config()
        os_client = DynamicClient(kube_client)

        if self.with_vol:
            try:
                vol = os_client.resources.get(api_version='v1', kind="PersistentVolumeClaim")
                api_response = vol.create(namespace=self.config['namespace'], body=self.db_body)
                print("Created DB: \n {}\n".format(api_response))
            except DynamicApiError as e:
                print("Error creating DB: \n{} \n".format(e))

        try:
            sa = os_client.resources.get(api_version='v1', kind="ServiceAccount")
            api_response = sa.create(namespace=self.config['namespace'], body=self.sa_body)
            print("Created Service Account: \n{} \n".format(api_response))
            call(["/bin/bash", 'configure_sa.sh', self.config['namespace']])
        except DynamicApiError as e:
            print("Error creating Service Account: \n{} \n".format(e))

        if self.with_swift:
            try:
                config_map = os_client.resources.get(api_version='v1', kind="ConfigMap")
                api_response = config_map.create(namespace=self.config['namespace'], body=self.swift_config_map_body)
                print("Created Swift ConfigMap: \n{} \n".format(api_response))
            except DynamicApiError as e:
                print("Error creating Swift ConfigMap: \n{} \n".format(e))

        if self.with_dv:
            try:
                config_map = os_client.resources.get(api_version='v1', kind="ConfigMap")
                api_response = config_map.create(namespace=self.config['namespace'], body=self.dv_config_map_body)
                print("Created Dataverse ConfigMap: \n{} \n".format(api_response))
            except DynamicApiError as e:
                print("Error creating Dataverse ConfigMap: \n{} \n".format(e))

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
