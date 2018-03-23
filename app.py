import os

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
import yaml
import json
import os
from openshift import config as o_config
from openshift import client as o_client
from kubernetes import client as k_client

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('hello.html')

@app.route('/login', methods=['POST'])
def login():

    print ('THIS IS POST LOGINS')
    content=''
    config=o_config.load_kube_config(config_file='/tmp/.kube/config')
    openshift_client=o_client.OapiApi()
    kube_client=k_client.CoreV1Api()
    kube_batch_client=k_client.BatchV1Api()

    if request.method == 'POST':
        content = request.json
        name='conclave-web-hw'
        image='docker.io/singhp11/python3-hello-world'

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
                                "env": [

                                    {
                                        "name": "KUBECFG_PATH",
                                        "value": "/tmp/.kube/config"
                                    },
                                    {
                                        "name": "OPENSHIFTMGR_PROJECT",
                                        "value": "cici"
                                    }
                                ],
                                "command": [
                                    "python",
                                    "/opt/app-root/app.py"
                                ],
                                "volumeMounts": [

                                    {
                                        "name": "kubecfg-volume",
                                        "mountPath": "/tmp/.kube/",
                                        "readOnly": True
                                    },
                                ]

                            }
                        ]
                    }
                }
            }
        }
        d_job['spec']['template']['spec']['volumes'] = [

            {
                "name": "kubecfg-volume",
                "secret": {
                    "secretName": "kubecfg"
                }
            }
        ]
    job = kube_batch_client.create_namespaced_job(namespace='cici', body=d_job)


    return jsonify(content)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)