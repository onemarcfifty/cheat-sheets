#!/bin/bash

# this script installs ansible and rundeck on a
# vanilla debian 11
# RUN AS ROOT!

apt update
apt -y upgrade
apt install -y python3 pip sudo wget curl
useradd -m -G sudo -s /bin/bash rundeck
# passwd rundeck
pip install ansible

curl https://raw.githubusercontent.com/rundeck/packaging/main/scripts/deb-setup.sh 2> /dev/null | sudo bash -s rundeck
apt update
apt -y install rundeck
sed -i s/localhost/`hostname`/g /etc/rundeck/framework.properties
sed -i s/localhost/`hostname`/g /etc/rundeck/rundeck-config.properties

# optional: move to mariadb

# install mariadb
apt install -y mariadb-server
# create rundeck db
mysql -u root -e 'create database rundeck'
# create user, random pass and grant access
RANDOMPASSWORD=`date +%s | sha256sum | base64 | head -c 32`
mysql -u root -e "create user rundeck@localhost identified by '$RANDOMPASSWORD'"
mysql -u root -e 'grant ALL on rundeck.* to rundeck@localhost'
# update the rundeck config
sed -i s/^dataSource.url/\#dataSource.url/g /etc/rundeck/rundeck-config.properties
echo 'dataSource.driverClassName = org.mariadb.jdbc.Driver'>>/etc/rundeck/rundeck-config.properties
echo 'dataSource.url = jdbc:mysql://localhost/rundeck?autoReconnect=true&useSSL=false' >>/etc/rundeck/rundeck-config.properties
echo 'dataSource.username = rundeck' >>/etc/rundeck/rundeck-config.properties
echo "dataSource.password = $RANDOMPASSWORD" >>/etc/rundeck/rundeck-config.properties

# start rundeck services

/etc/init.d/rundeckd start
systemctl enable rundeckd
