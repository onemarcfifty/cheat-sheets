# rundeck installation

## on Debian

The “Official” Installation instructions don’t work, see github issue https://github.com/rundeck/rundeck/issues/7098

You can add the rundeck repo like this:

    curl https://raw.githubusercontent.com/rundeck/packaging/main/scripts/deb-setup.sh 2> /dev/null | sudo bash -s rundeck
    apt update
    apt install rundeck

Next edit `/etc/rundeck/framework.properties` and `/etc/rundeck/rundeck-config.properties` and replace occurences of localhost with the hostname (unless you intent to access rundeck only from the localhost)

    sed -i s/localhost/`hostname`/g /etc/rundeck/framework.properties
    sed -i s/localhost/`hostname`/g /etc/rundeck/rundeck-config.properties

Now you can start rundeck:

    /etc/init.d/rundeckd start
    systemctl enable rundeckd
