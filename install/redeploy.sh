#!/bin/bash

oc delete all -l app=conclave-web
oc delete cm swift-cfg-mine
oc delete sa cw-svc

python3 install_script.py --swift=True --mini=True