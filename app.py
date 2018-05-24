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
import time
from kubernetes.client.rest import ApiException

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('hello.html')

@app.route('/login', methods=['POST'])
def login():

    config=o_config.load_kube_config(config_file='/tmp/.kube/config')
    openshift_client=o_client.OapiApi()
    kube_client=k_client.CoreV1Api()
    kube_batch_client=k_client.BatchV1Api()

    
    timestamp=str(int(round(time.time() * 1000)))
    

    if request.method == 'POST':
        jsondata = request.json
        # protocol=jsondata['protocol']
        yaml=jsondata['config']

        # Creating config map to load protocol and configurations details on conclave job pod.
        namespace='cici'
        protocol=jsondata['protocol']
        protocol_string=''
        for item in protocol:
            protocol_string+=item+'\n'

        print protocol_string



        data={
            "protocol.py":  protocol_string,
            "yaml.yaml" : "This is some yaml"
        } 

        configmap_name=''.join(['conclaveweb','-',timestamp])
        configmap_metadata=k_client.V1ObjectMeta(name=configmap_name)
        configmap_body=k_client.V1ConfigMap(data=data,metadata=configmap_metadata)

        pretty='pretty_example'

        try:
            api_response=kube_client.create_namespaced_config_map(namespace,configmap_body,pretty=pretty)
            print("api_response: ",api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_config_map: %s\n" % e)


        name=''.join(['conclave-web-hw','-',timestamp])
        image='docker.io/singhp11/python3-hello-world'
        # image='docker.io/bengetch/conclave:v3'

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
                                    "/app/app.py"
                                ],
                                "volumeMounts": [

                                    {
                                        "name": "kubecfg-volume",
                                        "mountPath": "/tmp/.kube/",
                                        "readOnly": True
                                    },
                                    {
                                        "name": "config-volume",
                                        "mountPath": "/etc/config",
                                        "readOnly": True
        
                                    }
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
            },
            {
                "name": "config-volume",
                "configMap":{
                    "name": configmap_name
                }
            
            }
        ]
        job = kube_batch_client.create_namespaced_job(namespace='cici', body=d_job)


        return jsonify(protocol)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)