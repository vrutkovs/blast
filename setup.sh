#!/bin/bash

#UI
oc new-app \
    soltysh/lighttpd-centos7~https://github.com/vrutkovs/catcatgo.git \
    --context-dir=ui \
    --name=ui \
    --labels=app=ui

oc set probe deploymentconfig/ui --liveness --open-tcp=8080
oc set probe deploymentconfig/ui --readiness --get-url=http://:8080/

# create service account for the cron job
oc create serviceaccount scraper
oc policy add-role-to-user view -z scraper
oc run scraper --schedule="0/5 * * * *" --image=soltysh/scraper --restart=Never

# create all the templates for each component
for dir in $(find * -maxdepth 0 -type d)
do
    oc new-app ${dir}/template.yaml
done

# expose the app
oc expose service/ui
