import time
import logging
import os

import conclave_manager

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


def create_config_map(kube_client, config_data):
    """
    Construct ConfigMap
    """

    timestamp = str(int(round(time.time() * 1000)))

    configmap_name = "conclaveweb-{}".format(timestamp)
    configmap_metadata = k_client.V1ObjectMeta(name=configmap_name)
    configmap_body = k_client.V1ConfigMap(data=config_data, metadata=configmap_metadata)
    app.logger.info("ConfigMap: {}".format(configmap_body))

    try:
        api_response = kube_client.create_namespaced_config_map('cici', configmap_body, pretty='true')
        app.logger.info("Namespace created successfully with response {}\n".format(api_response))
    except ApiException as e:
        app.logger.error("Error creating config map: {}\n".format(e))

    return configmap_name


@app.route('/api/submit', methods=['POST'])
def submit():
    """
    On Compute, construct ConfigMap and Job objects and dispatch.
    """

    template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
    mock_data_directory = "{}/mock_data".format(os.path.dirname(os.path.realpath(__file__)))

    k_config.load_incluster_config()
    kube_client = k_client.CoreV1Api()
    kube_batch_client = k_client.BatchV1Api()

    if request.method == 'POST':

        # will replace this hardcoding with request.response.dataRows && request.response.protocol
        protocol = open("{}/protocol.py".format(mock_data_directory)).read()

        data_one = open("{}/in1.csv".format(mock_data_directory)).read()
        conf_one = open("{}/conf-one.yaml".format(mock_data_directory)).read()

        data_two = open("{}/in2.csv".format(mock_data_directory)).read()
        conf_two = open("{}/conf-two.yaml".format(mock_data_directory)).read()


        config_map_one = create_config_map(kube_client, config_data_one)
        config_map_two = create_config_map(kube_client, config_data_two)

        name = "{}-pod".format(config_map_one)

        try:
            api_response = kube_batch_client.create_namespaced_job(namespace='cici', body=d_job)
            app.logger.info("Job created with response: {}".format(api_response))
        except ApiException as e:
            app.logger.error("Exception when calling BatchV1Api->create_namespaced_job: {}\n".format(e))

        return jsonify(protocol)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
