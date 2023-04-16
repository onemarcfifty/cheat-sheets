#!/bin/bash

# This script takes a monthly full backup and a weekly incremental backup

# Set the backup directory
BACKUP_DIR="/backup"

# Set the date format
DATE=$(date +%Y-%m-%d)

# Set the day of the week for the incremental backup
DAY=$(date +%A)

# Set the filename for the full backup
FULL_BACKUP_FILE="full-backup-${DATE}.tar.gz"

# Set the filename for the incremental backup
INCREMENTAL_BACKUP_FILE="incremental-backup-${DAY}-${DATE}.tar.gz"

# Set the exclude options for Tar
EXCLUDE="--exclude=/backup --exclude=/proc --exclude=/tmp --exclude=/mnt --exclude=/dev --exclude=/sys"

# Check if the backup directory exists, otherwise create it
if [ ! -d "${BACKUP_DIR}" ]; then
  mkdir "${BACKUP_DIR}"
fi

# Take a monthly full backup on the first day of the month
if [ $(date +%d) -eq 1 ]; then
  tar -czf "${BACKUP_DIR}/${FULL_BACKUP_FILE}" ${EXCLUDE} /
fi

# Take a weekly incremental backup on a specified day of the week
if [ "${DAY}" = "Sunday" ]; then
  # Check if the snapshot file exists, otherwise create it
  if [ ! -f "${BACKUP_DIR}/backup.snar" ]; then
    touch "${BACKUP_DIR}/backup.snar"
  fi
  tar -czf "${BACKUP_DIR}/${INCREMENTAL_BACKUP_FILE}" ${EXCLUDE} --listed-incremental="${BACKUP_DIR}/backup.snar" /
fi
