#!/bin/bash

oc create secret generic kube-config --from-file=$HOME/.kube/config -n $1