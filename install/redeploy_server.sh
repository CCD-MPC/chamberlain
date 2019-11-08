#!/bin/bash

oc delete all -l app=chamberlain
oc delete cm swift-auth
oc delete cm dataverse-auth
oc delete sa cw-svc

python3 install_script.py --swift=True --dv=True