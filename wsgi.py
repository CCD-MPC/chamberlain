import logging
import os
import ast
import sys

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from src.conclave_manager import ConclaveManager
from src.conclave_manager.status import check_pod_status

WITH_VOL = os.getenv("WITH_VOL")

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")
app.config.from_pyfile('src/db/db.cfg')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)


class ConclaveJob(db.Model):
    """
    Extends SQLAlchemy Model class, represents a running Conclave Job.
    """

    __tablename__ = 'Jobs'
    job_id = db.Column('job_id', db.Integer, primary_key=True)
    parties = db.Column('parties', db.Integer)
    pub_date = db.Column('pub_date', db.DateTime)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Redirect arbitrary pages to homepage.
    """
    return render_template("index.html")


def check_status(msg):

    job = ConclaveJob.query.filter_by(job_id=msg["ID"]).first()

    if job is not None:
        status = check_pod_status(job.id, job.parties, app)
    else:
        status = "No CC Jobs found for this ID."

    app.logger.info(status)

    return status


@app.route('/api/job_status', methods=['POST'])
def job_status():
    """
    Query status of Conclave job, send response to frontend.
    """

    msg = request.get_json(force=True)

    app.logger.info("Status request received for Job with ID {}".format(msg["ID"]))

    if msg:
        if ast.literal_eval(WITH_VOL):
            status = check_status(msg)
        else:
            status = "No DB present, can't check job status."
    else:
        status = "You do not have a Compute ID. Submit a job to obtain one."

    response = \
        {
            'status': status
        }

    return jsonify(response)


@app.route('/api/submit', methods=['POST'])
def submit():
    """
    Enter CC Job data into DB & submit CC Job.
    """

    if request.method == 'POST':

        config = request.get_json(force=True)

        app.logger.info("JSON received: {}".format(config))

        if ast.literal_eval(WITH_VOL):
            try:
                backend = config["config"]["backend"]
                if backend == "swift":
                    cc_job = ConclaveJob(
                        job_id=config["config"]["ID"],
                        parties=len(config["swift"]["endpoints"]),
                        pub_date=datetime.utcnow()
                    )
                    db.session.add(cc_job)
                    db.session.commit()
                elif backend == "dataverse":
                    cc_job = ConclaveJob(
                        job_id=config["config"]["ID"],
                        parties=len(config["dataverse"]["endpoints"]),
                        pub_date=datetime.utcnow()
                    )
                    db.session.add(cc_job)
                    db.session.commit()
                else:
                    app.logger.error("Backend {} not recognized. Exiting computation.\n".format(backend))
                    sys.exit(1)
            except KeyError:
                app.logger.error("No data storage backend passed in request. Exiting computation.\n")
                sys.exit(1)

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

    if ast.literal_eval(WITH_VOL):
        db.create_all()

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
