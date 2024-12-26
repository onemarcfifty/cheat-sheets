# Installing ansible

## on Debian

on Debian you can do a simple
    apt install ansible

## with pip

If you want to install with pip then you need to decide if you want to install it globally or for one single user only. The ansible documentation is not clear on that. First you need python3 and pip. On Debian you would do (as root):

    apt install python3 pip

Now you can install ansible by doing

    pip install ansible

If you do this as root, then ansible will be installed globally (e.g. in /usr/local/bin) **If you do this as non-root user, ansible will be installed under .local/bin under your home directory** and will therefore not be in the PATH

## recommendation

1. Create non-root user for ansible
2. put ansible config into .ansible.cfg in the user's home (advantage: can easily be changed with Filezilla / Editor without root ssh access)
3. point inventory to directory rather than file (advantage: have multiple inventory sources)

## More Info on config and inventory

### Config files

Config Files ([https://www.redhat.com/sysadmin/configuring-ansible](https://www.redhat.com/sysadmin/configuring-ansible))
Ansible searches the following order:

1. `$ANSIBLE_CONFIG` if the environment variable is set.
2. `ansible.cfg` if it’s in the current directory.
3. `~/.ansible.cfg` if it’s in the user’s home directory.
4. `/etc/ansible/ansible.cfg`, the default config file.
    
Suggestion: Put ansible config into ~/.ansible.cfg (Solution 3)

### Ansible inventory

Add line to .ansible.cfg for inventory to be loaded:

```
[defaults]
# some basic default values...
inventory = ~/.ansible/inventory
```

if inventory entry is a file then ansible loads inventory from that file but you have to decide if static or plugin. **If the entry is directory then it will scan all files in the dir by alphabetical order.**
