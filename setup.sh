#!/bin/bash
set -eux

# Create catcatgo app bits
oc new-project catcatgo || oc project catcatgo

oc create -f openshift/is-lighttpd-centos7.yml
oc create -f openshift/is-backend.yml
oc create -f openshift/is-scraper.yml
oc create -f openshift/is-ui.yml

oc create -f openshift/confimap-db.yml
oc create -f openshift/confimap-scraper.yml
oc create -f openshift/rolebinding-edit.yml

oc create -f openshift/bc-backend.yml
oc create -f openshift/bc-scraper.yml
oc create -f openshift/bc-ui.yml

oc adm policy add-scc-to-user anyuid -z default
oc adm policy add-scc-to-user privileged -z default

oc create -f openshift/pvc-database.yml
oc apply -f <(istioctl kube-inject -f openshift/dc-database.yml)
oc create -f openshift/svc-database.yml

oc apply -f <(istioctl kube-inject -f openshift/dc-backend.yml)
oc create -f openshift/svc-backend.yml

oc apply -f <(istioctl kube-inject -f openshift/dc-ui.yml)
oc create -f openshift/svc-ui.yml

oc create -f openshift/cronjob-scraper.yml

# Add istio rules
oc create -f istio/route-rules.yml
oc create -f istio/gateway.yml

oc delete route istio-ingressgateway -n istio-system
oc create route edge --service=istio-ingressgateway --hostname=catcatgo.cloud.vrutkovs.eu -n istio-system
