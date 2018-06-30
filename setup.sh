#!/bin/bash
set -eux

# Create catcatgo app bits
oc new-project catcatgo || oc project catcatgo

oc create serviceaccount scraper

oc apply -f openshift/is-lighttpd-centos7.yml
oc apply -f openshift/is-backend.yml
oc apply -f openshift/is-scraper.yml
oc apply -f openshift/is-ui.yml

oc apply -f openshift/confimap-db.yml
oc apply -f openshift/confimap-scraper.yml
oc apply -f openshift/rolebinding-edit.yml

oc apply -f openshift/bc-backend.yml
oc apply -f openshift/bc-scraper.yml
oc apply -f openshift/bc-ui.yml

oc adm policy add-scc-to-user anyuid -z default
oc adm policy add-scc-to-user privileged -z default

oc apply -f openshift/pvc-database.yml
oc apply -f <(istioctl kube-inject -f openshift/dc-database.yml)
oc apply -f openshift/svc-database.yml

oc apply -f <(istioctl kube-inject -f openshift/dc-backend.yml)
oc apply -f openshift/svc-backend.yml

oc apply -f <(istioctl kube-inject -f openshift/dc-ui.yml)
oc apply -f openshift/svc-ui.yml

oc apply -f openshift/cronjob-scraper.yml

# Add istio rules
oc apply -f istio/route-rules.yml
oc apply -f istio/gateway.yml

oc delete route istio-ingressgateway -n istio-system
oc create route edge --service=istio-ingressgateway --hostname=catcatgo.cloud.vrutkovs.eu -n istio-system
