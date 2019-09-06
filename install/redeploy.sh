#!/bin/bash

oc delete all -l app=chamberlain
oc delete cm swift-cfg-mine
oc delete sa cw-svc

python3 install_script.py --swift=True