import os

from flask import Flask
from flask import request
from flask import render_template
from kubernetes import client as k_client
from openshift import client as o_client
import yaml
import json
import os



app = Flask(__name__)



@app.route("/")
def index():
    return render_template('hello.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        content = request.json
        print content['mytext']
        name='conclavepy'
        # image='docker.io/singhp11/pyspark-python3'
        image='singhp11/python3-hello-world'

        d_job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": name
            },
            "spec": {
                "parallelism": 1,
                "completions": 1,
                "activeDeadlineSeconds": 3600,
                "template": {
                    "metadata": {
                        "name": name
                    },
                    "spec": {
                        "restartPolicy": "Never",
                        "containers": [
                            {
                                "name": name,
                                "image": image,

                                # "volumeMounts": [
                                #     {
                                #         "name": "config-volume",
                                #         "mountPath": "/etc/config"
                                #     }
                                # ]
                            }
                        ]
                    }
                }
            }
        }
        # d_job['spec']['template']['spec']['volumes'] = [
        #     {
        #         "name": "config-volume",
        #         "configMap":[
        #             {
        #                 "name": "special-config"
        #             }
        #         ]
        #     }
        # ]

        kube_client = k_client.CoreV1Api()
        kube_v1_batch_client = k_client.BatchV1Api()
        project = os.environ.get('OPENSHIFTMGR_PROJECT') or 'cici'
        print ('Namespace: ', project)
        job = kube_v1_batch_client.create_namespaced_job(namespace=project, body=d_job)


        return render_template('submit.html')





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)