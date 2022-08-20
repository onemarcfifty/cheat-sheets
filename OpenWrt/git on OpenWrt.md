**using git with ssh on OpenWrt**

git can use various protocols to connect to a git server. If you want to use ssh from a system running busybox/dropbear then you will need to tell it how to connect. There are two ways to solve this:

1. use dbclient instead of ssh
2. convert the keys and use ssh

Both methods will read the environment variable `GIT_SSH_COMMAND`
Assuming that your git key is in `~/.ssh/id_git` :


=ssh -y -i ~/.ssh/id_git

**Method 1: using dbclient**

    echo "#!/bin/sh" > ~/.gitssh.sh
    echo "dbclient -y -i ~/.ssh/id_git \$*" >> ~/.gitssh.sh
    chmod +x ~/.gitssh.sh
    export GIT_SSH=~/.gitssh.sh

**Method 2: convert the keys**

    # convert key to PEM on OpenWrt hosts
    ssh-keygen -p -N "" -m PEM -f ~/.ssh/id_git
    # convert PEM key to dropbear on OpenWrt hosts
    dropbearconvert openssh dropbear ~/.ssh/id_git ~/.ssh/id_git_dropbear
    rm ~/.ssh/id_git
    mv ~/.ssh/id_git_dropbear ~/.ssh/id_git
    export GIT_SSH_COMMAND=ssh -y -i ~/.ssh/id_git

Now you can git clone, pull etc. using ssh