# rundeck installation

rundeck is a great GUI for Docker and other automation software (e.g. hashicorp terraform) and also a remote execution software itself!

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

You can now log in to http://(hostname):4440 with user **admin** and pass **admin**

### Database migration to mySQL / mariadb

1. export all projects (Project settings - Export Archive)
2. stop rundeck: `service rundeckd stop`
3. backup H2 database in (rundeckhome)/data
4. install mariadb `apt install mariadb-server`
5. create the rundeck db:

type the following:

    mysql -u root -p
    create database rundeck;
    grant ALL on rundeck.* to rundeck@localhost identified by 'YOURPASSWORDHERE';
    quit

6. edit `/etc/rundeck/rundeck-config.properties`

put the following content in the file:

    dataSource.driverClassName = org.mariadb.jdbc.Driver
    dataSource.url = jdbc:mysql://localhost/rundeck?autoReconnect=true&useSSL=false
    dataSource.username = rundeck
    dataSource.password = YOURPASSWORDHERE
