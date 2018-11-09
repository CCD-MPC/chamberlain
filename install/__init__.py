import os
import json

from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException


class ConclaveWebInstall:
    """
    TODO:
        - create DB vol (pending persistent volume creation on DC)
        - create service account
        - create kubecfg secret
        - create CW from template
    """

    def __init__(self):

        self.config = json.load("{}/config/conf.json".format(os.path.dirname(os.path.realpath(__file__))))
        self.template_dir = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))