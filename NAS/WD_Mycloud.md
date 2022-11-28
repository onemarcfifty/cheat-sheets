# WD myCloud Tips & Scripts

The WD mycloud is quite locked down w/r to what you can do with it. It can serve as a NAS drive and run some plugins. That's pretty much it. If you want to access it directly (i.e. via ssh for ansible and the like or via nfs) then you will have to tweak a couple of things.

## accessing the NAS via ssh

The ssh user is hard coded. Use the credentials `sshd` as a user and the password that you define in the Web GUI. If you want to use public/private key authentication for ssh, then we will need to do a couple of loops.

## Executing a script at startup

Taken from <a href=https://community.wd.com/t/how-to-run-a-user-boot-script-at-mycloud-gen2-2-11-xx-devices/169822> this article </a>

add the following node under `crond/stime` in `/usr/local/config/config.xml` :

				<count>1</count>
				<item id="1">
					<method>3</method>
					<1>*</1>
					<2>*</2>
					<3>*</3>
					<4>*</4>
					<5>*</5>
					<run>/usr/local/config/boot-script &amp;</run>
				</item>

The `/usr/local/config/boot-script` will be executed within the first 5 minutes after boot

Basically the `/usr/local/config` directory is persistent and can contain anything that you want to survive a reboot, e.g.

- scripts
- ssh keys
- config files

etc.

## Bootscript example

This example bootscript does the following:

- It replaces the no root squash entry for NFS (see next section)
- it copies an ssh key file to the sshd user
- it kills some processes that I don't use (mainly mdns related)

test

	! /bin/sh

	CRONTAB=/var/spool/cron/crontabs/root
	CONFIG=/usr/local/config
	BOOTRUN=/tmp/bootscript-run

	# Remove boot-script from crontab and
	# recover crontab
	cd $CONFIG
	cp crontab.orig $CRONTAB

	# don't run twice
	if [ -f $BOOTRUN ]; then exit 0
	fi
	touch $BOOTRUN


	# ###################################
	# wait until all services are up
	# ###################################

	sleep 120

	# ###################################
	# remove root_squash from nfs exports
	# ###################################

	sed -i s/all_squash/no_root_squash/ /etc/exports
	/usr/sbin/exportfs -ra

	# ###################################
	# copy ssh keys to root profile
	# ###################################
	mkdir $HOME/.ssh
	cp -a id_rsa.pub $HOME/.ssh/authorized_keys


	# ###################################
	# stop unnecessary processes
	# ###################################
	/usr/sbin/smb stop
	/usr/sbin/otaclient.sh stop
	/usr/sbin/restsdk.sh stop
	/usr/sbin/upnpnas.sh stop
	killall avahi-daemon


## NFS root squash

If you want to export NFS shares without root squashing (i.e. mount them as a file system on a linux system, then you will have to modify the /etc/exports). the following Ansible playbook replaces the necessary arguments:

	---

	- name: prepare WD
	  hosts: WD_mycloud

	  tasks:

		- name: change squash to no root squash
		  replace:  
			path: /etc/exports
			regexp: 'all_squash'
			replace: 'no_root_squash'    

		- name: apply exports changes
		  command: /usr/sbin/exportfs -ra

## shutting down the NAS and Wake On LAN

The NAS can be shut down with the `/usr/sbin/shutdown.sh` script and can be woken up with WOL. However, if you would just call the shutdown script from ansible, then the ssh connection is disconnected and your job will always show as failed. Again we can use cron to schedule the shutdown in a minute. Put the following in `/usr/local/config/do_shutdown.sh`

	#!/bin/sh
	#
	# Script to schedule shutdown in the next minute
	# Can be called by ansible to shutdown the NAS with return code 0
	# (calling shutdown.sh directly would break the ssh connection and result in an error)

	# sh does not know the &disown parameter, hence we can not
	# just call the script with an ampersand (&)

	# the workaround is to add a cronjob that will be executed every minute
	echo "*/1 * * * * /usr/sbin/shutdown.sh" >>/var/spool/cron/crontabs/root

	# now we kill and re-spawn crond
	kill `pidof crond`
	sleep 3
	crond -b

## putting it together in Ansible

Now you can wake up the NAS with WOL, do some stuff (e.g. backup to the NAS) and shut it down:

    ---

    - name: Wake up WD MyCloud
      hosts: WD_myCloud
      gather_facts: no

      tasks:
        - name: Send WOL
          community.general.wakeonlan:
            mac: "{{MAC_ADDR}}"
            broadcast: "{{IP_ADDR}}"
          delegate_to: localhost

      # use IP addr 255.255.255.255 and the MAC of the WD MyCloud as variables


    - name: wait 5 minutes
      hosts: all
      gather_facts: no

      tasks:
        - name: sleep300
          shell: "sleep 300"
          delegate_to: localhost


    - name: Synology NAS to WD MyCloud NAS backup
      hosts: synologynas
      become: yes

      tasks:

        - name: Mount NFS1 on WD Mycloud
          ansible.posix.mount:
            path: /mnt/disk1
            src: {{WDMYCLOUD_IP_ADDRESS}}:/nfs/backup
            fstype: nfs
            state: mounted
    
        - name: Sync Archive
          command: rsync -a -H --delete-before --delete-excluded --exclude cloud.transfer --exclude \@eaDir /volume1/archive /mnt/disk1/backup/

        - name: Sync photos
          command: rsync -a --delete-before --delete-excluded --exclude \@eaDir /volume1/photo /mnt/disk1/backup/

        - name: Sync videos
          command: rsync -a --delete-before --delete-excluded --exclude public --exclude \@eaDir /volume1/video /mnt/disk1/backup/

        - name: Unmount the NFS1 volume
          ansible.posix.mount:
            path: /mnt/disk1
            state: absent

    - name: shutdown WD
      hosts: WD_mycloud

      tasks:

        - name: ethtool
          command: "ethtool -s egiga0 wol g"

        - name: shutdown
          command: "/usr/local/config/do_shutdown.sh"
