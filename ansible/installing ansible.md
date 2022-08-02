# Installing ansible

## on Debian

on Debian you can do a simple
    apt install ansible

## with pip

If you want to install with pip then you need to decide if you want to install it globally or for one single user only. The ansible documentation is not clear on that. First you need python3 and pip. On Debian you would do (as root):

    apt install python3 pip

Now you can install ansible by doing

    pip install ansible

If you do this as root, then ansible will be installed globally (e.g. in /usr/local/bin) **If you do this as non-root user, ansible will be installed under .local/bin under your home directory** and wil theerefore not be in the PATH
