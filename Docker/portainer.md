**portainer run command**

    docker volume create portainer_data
    docker run -d -p 8000:8000 -p 9443:9443 -p 9000:9000 --name portainer \
        --restart=always \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v portainer_data:/data \
        portainer/portainer-ce

**portainer install with ansible**

    - name: Create Portainer Volume
      community.docker.docker_volume:
        name: portainer-data

    - name: Deploy Portainer
      community.docker.docker_container:
        name: portainer
        image: "docker.io/portainer/portainer-ce"
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
          - portainer-data:/data
        ports:
          - "9443:9443"
          - "9000:9000"
          - "8000:8000"
        restart_policy: always
