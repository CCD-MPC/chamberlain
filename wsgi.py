import time
import logging
import os
import pystache
import ast

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException
from flask_cors import CORS

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")

# CORS to allow status calls from backend to frontend
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


if __name__ != "__main__":
    """
    Bind Python logs to gunicorn logger.
    """
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Redirect arbitrary pages to homepage.
    """
    return render_template("index.html")


@app.route('/api/job_status')
def job_status(status=None):
    """
    After querying status of Conclave job, send response to frontend.
    TODO: make status response meaningful
    """

    if status is None:
        status = 'everything ok'

    response = \
        {
            'status': status
        }

    return jsonify(response)


def build_conclave_config_template(conf):
    '''
    After Conclave pods are defined, generate configuration data
    for each pod.
    '''

    data = {
        "PID": conf["pid"],
        "ALL_PIDS": (pid for pid in conf["all_pids"]),
        "WORKFLOW_NAME": conf["workflow_name"],


    }

    return


def build_config_map_data(protocol, input_data, conf, template_directory):
    """
    Construct ConfigMap JSON from protocol & config.
    """

    data_template = open("{}/configmap_data.tmpl".format(template_directory)).read()

    # these two values will be populated from user input in the future
    conf_filename = "conf-one.yaml"
    input_filename = "in1.csv"

    data_params = \
        {
            "PROTOCOL": protocol,
            "INPUT_DATA": input_data,
            "CONF": conf,
            "IN_FILE": input_filename,
            "CONF_FILE": conf_filename
        }

    return ast.literal_eval(pystache.render(data_template, data_params))


def build_pod_json(name, configmap_name, template_directory):
    """
    Construct JSON for CC Pod with configMap.
    """

    pod_template = open("{}/pod.tmpl".format(template_directory), 'r').read()

    params = \
        {
            "POD_NAME": name,
            "CONFIGMAP_NAME": configmap_name
        }

    return ast.literal_eval(pystache.render(pod_template, params))


def build_service_json(name, template_directory):
    """
    Construct JSON for CC Service
    """

    svc_template = open("{}/service.tmpl".format(template_directory), 'r').read()

    params = \
        {
            "SERVICE_NAME": name
        }

    return ast.literal_eval(pystache.render(svc_template, params))


@app.route('/api/submit', methods=['POST'])
def submit():
    """
    On Compute, construct ConfigMap and Job objects and dispatch.
    """

    template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
    mock_data_directory = "{}/mock_data".format(os.path.dirname(os.path.realpath(__file__)))
    timestamp = str(int(round(time.time() * 1000)))

    k_config.load_incluster_config()
    kube_client = k_client.CoreV1Api()
    kube_batch_client = k_client.BatchV1Api()

    if request.method == 'POST':

        # these three values will be populated by user data
        protocol = open("{}/protocol.py".format(mock_data_directory)).read()
        data = open("{}/in1.csv".format(mock_data_directory)).read()
        conf = open("{}/conf-one.yaml".format(mock_data_directory)).read()

        data = build_config_map_data(protocol, data, conf, template_directory)

        configmap_name = "conclaveweb-{}".format(timestamp)
        configmap_metadata = k_client.V1ObjectMeta(name=configmap_name)
        configmap_body = k_client.V1ConfigMap(data=data, metadata=configmap_metadata)
        app.logger.info("ConfigMap: {}".format(configmap_body))

        try:
            api_response = kube_client.create_namespaced_config_map('cici', configmap_body, pretty='true')
            app.logger.info("Namespace created successfully with response {}\n".format(api_response))
        except ApiException as e:
            app.logger.error("Error creating config map: {}\n".format(e))

        name = ''.join(['conclave-web-hw', '-', timestamp])
        d_job = build_job_data(name, configmap_name, template_directory)

        try:
            api_response = kube_batch_client.create_namespaced_job(namespace='cici', body=d_job)
            app.logger.info("Job created with response: {}".format(api_response))
        except ApiException as e:
            app.logger.error("Exception when calling BatchV1Api->create_namespaced_job: {}\n".format(e))

        return jsonify(protocol)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
