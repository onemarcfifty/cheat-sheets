#!/bin/bash

# ########################################
# creates a snapshot of the last x backups
# using hard links
# plain bash, cp, rm, no rsync or
# rsnapshot.
# ########################################

BACKUPDIR=/mnt/HD/HD_a2/backup
SNAPDIR=/mnt/HD/HD_a2/backup.snap
NUMSNAPS=15

# create dir for the snapshots if it doesn't exist
if [ ! -e $SNAPDIR ] ; then 
    echo creating $SNAPDIR
    mkdir -p $SNAPDIR  
fi

# move the snapshots up one layer in the chain

# first delete the oldest
if [ -e $SNAPDIR/$NUMSNAPS ] ; then 
    echo "removing ${SNAPDIR}/${NUMSNAPS}"
    rm -rf "${SNAPDIR}/${NUMSNAPS}"
fi


# now move everything up one level
echo "moving old snaps"
for i in `seq $NUMSNAPS -1 1` ; do
   PREVIOUS=$(($i-1))
   mv "${SNAPDIR}/${PREVIOUS}" "${SNAPDIR}/${i}" 
done

# last but not least create the new snapshot
echo "creating new snapshots"
cp -al $BACKUPDIR "$SNAPDIR/0"

