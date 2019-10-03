#!/bin/bash

oc policy add-role-to-user edit system:serviceaccount:cici:cw-svc
oc policy add-role-to-user edit system:serviceaccount:cici:cw-svc -n ccd-one
oc policy add-role-to-user edit system:serviceaccount:cici:cw-svc -n ccd-two