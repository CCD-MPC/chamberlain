import logging
import os

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask_cors import CORS

from conclave_manager import ConclaveManager
from conclave_manager.status import CheckStatus

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


@app.route('/api/job_status', methods=['POST'])
def job_status():
    """
    After querying status of Conclave job, send response to frontend.
    TODO: make status response meaningful

    OUTLINE:
        When user hits 'Compute', they'll be given an ID that they can use to query the status of
        Jobs. The ConclaveManager class will be instantiated with an ID.

    """

    msg = request.get_json(force=True)

    if msg:
        status = CheckStatus(app, msg["ID"])
    else:
        status = "You do not have a Compute ID. Submit a job to obtain one."

    response = \
        {
            'status': status
        }

    return jsonify(response)


@app.route('/api/submit', methods=['POST'])
def submit():

    if request.method == 'POST':

        config = request.get_json(force=True)
        compute_id = config["ID"]

        app.logger.info("JSON received: {}".format(config))

        cc_manager = ConclaveManager(request.get_json(force=True), app, compute_id)
        cc_manager.run()

        response = \
            {
                "ID": compute_id
            }

        return jsonify(response)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
