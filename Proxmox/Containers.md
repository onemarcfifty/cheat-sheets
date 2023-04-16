## container stuff (LXC)


### LXC not reachable any more over the network

Root cause: Network interface had been removed but config is still stuck in /etc/network/interfaces - when the container has a DHCP address, it doesn't renew.

Steps to verify:

do `ip addr` - one or more interfaces without IP Address ?
do `vi /etc/network/interfaces` - are there interfaces which do not exist any more ?

Remediation: remove rogue interface entries from /etc/network/interfaces

### Convert Docker Container to Proxmox LXC

1. Export the Container
```bash
docker export CONTAINERNAME | gzip > TEMPLATENAME.tar.gz
```
2. copy the template to the Proxmox Template dir
3. Create an LXC container from the template

To be solved : 
- Volumes
- Network
- Entrypoint

More info:

https://discuss.linuxcontainers.org/t/simple-script-to-convert-any-gnu-linux-machine-into-a-proxmox-lxc-container/10339
https://github.com/my5t3ry/machine-to-proxmox-lxc-ct-converter (origin)
https://github.com/ftrojahn/machine-to-proxmox-lxc-ct-converter (fork, 10 commits ahead)

