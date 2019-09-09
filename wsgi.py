import logging
import os
import shutil

from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from base64 import b64encode

from src.conclave_manager import ConclaveManager
from src.conclave_manager.status import check_pod_status
from src.swift import SwiftData

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Redirect arbitrary pages to homepage.
    """
    return "we gotta help the pope"


@app.route('/')
@app.route('/index')
def index():

    return "we gotta help the pope"


def pull_swift_data(compute_id, cfg):
    """
    pull data from an associated swift container, b64 encode, and return it
    """

    ret = {}

    container = compute_id
    swift_data = SwiftData(cfg)

    os.mkdir("/tmp/{}".format(compute_id))
    swift_data.get_all_data(container, "/tmp/{}".format(compute_id))

    for subdir, dirs, files in os.walk("/tmp/{}".format(compute_id)):
        for file in files:
            f = open("/tmp/{0}/{1}".format(compute_id, file))
            data = f.read()
            data_encoded = b64encode(data.encode()).decode()
            ret[file] = data_encoded
            f.close()

    # cleanup pulled data
    shutil.rmtree("/tmp/{}".format(compute_id))

    return ret


@app.route('/api/return_output', methods=['POST'])
def return_output():
    """
    TODO: if job isnt completed then dont pull the data
    """

    msg = request.get_json(force=True)

    app.logger.info("Request for output received for Job with ID {}".format(msg["ID"]))

    swift_cfg = {
        "auth": {
            "osAuthUrl": open("/etc/swift-config/mine/auth_url", "r").read(),
            "username": open("/etc/swift-config/mine/user_name", "r").read(),
            "password": open("/etc/swift-config/mine/pass", "r").read()
        },
        "project": {
            "osProjectDomain": open("/etc/swift-config/mine/proj_domain", "r").read(),
            "osProjectName": open("/etc/swift-config/mine/proj_name", "r").read()
        }
    }

    data = pull_swift_data(msg["ID"], swift_cfg)

    response = \
        {
            "job_id": msg["ID"],
            "files": data
        }

    return jsonify(response)


@app.route('/api/job_status', methods=['POST'])
def job_status():
    """
    Query status of Conclave job, send response to frontend.
    """

    msg = request.get_json(force=True)

    app.logger.info("Status request received for Job with ID {}".format(msg["ID"]))

    if msg:
        status = check_pod_status(msg, app)
    else:
        status = "You do not have a Compute ID. Submit a job to obtain one."

    response = \
        {
            'job_id': msg["ID"],
            'status': status
        }

    return jsonify(response)


@app.route('/api/submit', methods=['POST'])
def submit():
    """
    submit CC Job.
    """

    if request.method == 'POST':

        config = request.get_json(force=True)

        app.logger.info("JSON received: {}".format(config))

        cc_manager = ConclaveManager(config, app)
        cc_manager.run()

        response = \
            {
                "ID": config["config"]["ID"]
            }

        return jsonify(response)


if __name__ != "__main__":
    """
    Bind Python logs to gunicorn logger.
    """

    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
