#!/bin/bash

images=(linuxserver/sonarr)
containers=(sonarr)
services=(docker-sonarr)

for ((i=0; i<${#images[*]}; i++)); do
    echo "Pulling docker image: ${images[i]}"
    docker pull ${images[i]}
    if [[ $(docker inspect --type=image --format='{{.Id}}' ${images[i]}) != $(docker inspect --type=container --format='{{.Image}}' ${containers[i]}) ]]; then
        echo "Restarting service: ${services[i]}"
        systemctl restart ${services[i]}
    fi
done
