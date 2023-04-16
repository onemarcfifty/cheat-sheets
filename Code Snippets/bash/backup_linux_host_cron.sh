#!/bin/bash

# This script takes a full or incremental backup
# call with cron: 
# e.g. monthly : backup Full /backup
# and weeekly: backup Incremental /backup
# The script needs to be run as root!

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ $# -ne 2 ]; then
  echo "Usage: $0 [Full|Incremental] [BackupDir]"
  exit 1
fi

if [ "$1" != "Full" ] && [ "$1" != "Incremental" ]; then
  echo "Usage: $0 [Full|Incremental] [BackupDir]"
  exit 1
fi

BACKUP_DIR=$2
BACKUP_MODE=$1

# Set the date format
DATE=$(date +%Y-%m-%d)

# Set the filename for the full backup
FULL_BACKUP_FILE="full-backup-${DATE}.tar.gz"

# Set the filename for the incremental backup
INCREMENTAL_BACKUP_FILE="incremental-backup-${DATE}.tar.gz"

# Set the exclude options for Tar
EXCLUDE="--exclude=/${BACKUP_DIR} --exclude=/proc --exclude=/tmp --exclude=/mnt --exclude=/dev --exclude=/sys"

# Check if the backup directory exists, otherwise create it
if [ ! -d "${BACKUP_DIR}" ]; then
  mkdir "${BACKUP_DIR}"
fi

if [ "$BACKUP_MODE" == "Full" ]; then
  echo "Full backup selected"
  # delete an old incremental list if available
  if [ -f "${BACKUP_DIR}/backup.snar" ]; then
    rm "${BACKUP_DIR}/backup.snar"
    touch "${BACKUP_DIR}/backup.snar"
  fi
  tar -czf "${BACKUP_DIR}/${FULL_BACKUP_FILE}" ${EXCLUDE} --listed-incremental="${BACKUP_DIR}/backup.snar" /
elif [ "$BACKUP_MODE" == "Incremental" ]; then
  echo "Incremental backup selected"
  if [ ! -f "${BACKUP_DIR}/backup.snar" ]; then
    touch "${BACKUP_DIR}/backup.snar"
  fi
  tar -czf "${BACKUP_DIR}/${INCREMENTAL_BACKUP_FILE}" ${EXCLUDE} --listed-incremental="${BACKUP_DIR}/backup.snar" /
fi

