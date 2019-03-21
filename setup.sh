#!/bin/bash

oc new-project catcatgo

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

oc create -f openshift/pvc-database.yml
oc create -f openshift/dc-database.yml
oc create -f openshift/svc-database.yml

oc create -f openshift/dc-backend.yml
oc create -f openshift/svc-backend.yml
oc create -f openshift/route-backend.yml

oc create -f openshift/dc-ui.yml
oc create -f openshift/svc-ui.yml
oc create -f openshift/route-ui.yml

oc create -f openshift/cronjob-scraper.yml
