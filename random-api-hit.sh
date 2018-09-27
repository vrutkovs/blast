#!/bin/bash
for i in `seq 1 100`; do
  word=$(sort -R /usr/share/dict/words | head -1)
  sudo podman run --rm -ti ecliptik/docker-siege -t 5s https://catcatgo.cloud.vrutkovs.eu/api/v1.0/search/$word
done
