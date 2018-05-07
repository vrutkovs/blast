#!/bin/bash

oc new-project catcatgo

oc create -f is-lighttpd-centos7.yml
oc create -f is-backend.yml
oc create -f is-scraper.yml
oc create -f is-ui.yml

oc create -f confimap-db.yml
oc create -f confimap-scraper.yml
oc create -f rolebinding-edit.yml

oc create -f bc-backend.yml
oc create -f bc-scraper.yml
oc create -f bc-ui.yml

oc create -f pvc-database.yml
oc create -f dc-database.yml
oc create -f svc-database.yml

oc create -f dc-backend.yml
oc create -f svc-backend.yml
oc create -f route-backend.yml

oc create -f dc-ui.yml
oc create -f svc-ui.yml
oc create -f route-ui.yml

oc create -f cronjob-scraper.yml
