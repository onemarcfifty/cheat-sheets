#!/bin/ash

# see if files have changed between two
# identical trees
# from the test_extroot.sh repo

cd "$MTDMOUNTLOCATION/upper/etc"

FILESHAVECHANGED=NO

for i in $(/usr/bin/find *) ; do 
	if [ -f $i ] ; then 
		/usr/bin/cmp "$i" "/overlay/upper/etc/$i"
		rc=$?
		if [[ $rc != 0 ]]; then 
			FILESHAVECHANGED=YES
		fi
	fi
done