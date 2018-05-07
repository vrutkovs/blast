#!/bin/bash
set -eux

export PATH=$PATH:~/bin/istio-0.7.1/bin

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

oc create -f istio/route-rules.yml
oc create -f istio/ingress.yml
oc create -f istio/egress.yml

oc delete route istio-ingress -n istio-system
oc create route edge --service=istio-ingress --hostname=catcatgo.cloud.vrutkovs.eu -n istio-system
