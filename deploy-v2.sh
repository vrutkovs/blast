#!/bin/bash
set -eux

oc apply -f openshift/bc-ui-v2.yml
oc apply -f <(istioctl kube-inject -f openshift/dc-ui-v2.yml)
