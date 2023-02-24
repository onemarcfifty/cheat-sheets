#!/usr/bin/env python

# ##########################################
# duplicate file finder
# ##########################################

import os
import sys
import hashlib
import getopt
from collections import defaultdict

# ##########################################
# Global Vars
# ##########################################

# exclude paths that include a "@" (like @eaDir on the Synology)
EXCLUDE_PATH_PATTERNS = ['@']

# only treat files of a minimum size
MINIMUM_FILE_SIZE = 10000

# default to Verbose=no
VERBOSE = False

# dry run or action ?
DRY_RUN = False

# ##########################################
# Check if path is legit
# ##########################################

def path_is_legit(path):
    is_legit=True
    for xpattern in EXCLUDE_PATH_PATTERNS:
        if xpattern in path:
            is_legit=False
    return(is_legit)

# ##########################################
# Generator that reads a file in 
# chunks of bytes 
# ##########################################

def chunk_reader(fobj, chunk_size=1024):
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk

# ##########################################
# get_hash calculates a sha1 hash of a 
# file or of the first chunk of a file
# vars:
# filename:         Full path to the File
# first_chunk_only: if True, then only the
#                   first 1K is hashed
# hash_algo:        H1sh algorithm to use
# ##########################################

def get_hash(filename, first_chunk_only=False, hash_algo=hashlib.sha1):
    hashobj = hash_algo()
    with open(filename, "rb") as f:
        if first_chunk_only:
            hashobj.update(f.read(1024))
        else:
            for chunk in chunk_reader(f):
                hashobj.update(chunk)
    return hashobj.digest()

# ##########################################
# dedupe_list takes a list of files which 
# had been found to be dupes and replaces
# them with hard links
# ##########################################

# @@ TODO : check if permissions, mode, ownership are the same
# (add commandline parameter)

def dedupe_list(file_list):
    inode_list = defaultdict(list)

    files_deduped = 0
    files_error = 0

    # let's first see if all files point to the same inode
    # in which case we do not need to do anything

    for file in file_list:
        inode=os.stat(file).st_ino
        inode_list[inode].append(file)

    # all files point to the same inode
    if len(inode_list) < 2:
        return([0,0])

    #for file in file_list:
    # we use a counter loop in order to have an anchor

    anchor=file_list[len(file_list)-1]
    for i in range(len(file_list)-1):
        file=file_list[i]
        osCommand = "ln -f '%s' '%s'" % (anchor,file)
        if (VERBOSE):
            print(osCommand)
        try:
            if (not DRY_RUN):
                os.system(osCommand)
            files_deduped += 1
        except:
            files_error += 1
            continue
    return([files_deduped,files_error])

# ##########################################
# check_for_duplicates is the core routine
# it takes one or more paths as an argument
# and returns the duplicate files 
# ##########################################


def check_for_duplicates(paths):
    files_by_size = defaultdict(list)
    files_by_small_hash = defaultdict(list)
    files_by_full_hash = defaultdict(list)

    skipped_files=0
    skipped_paths=0
    scanned_paths=0
    hashed_files=0

    # ###################################################
    # Step 1 : Create a dictionary of all files with the 
    #          same size, having the size as the key
    #          in files_by_size = defaultdict(list)
    # ###################################################
   

    for path in paths:
        if (VERBOSE):
            print("\nPath: %s" % path)
            print("===== STEP 1 - hash by size")
        for dirpath, _, filenames in os.walk(path):
            if (path_is_legit(dirpath)):
                scanned_paths +=1 
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)

                    # just make sure it's not a mount or dir
                    if (os.path.isdir(full_path) or os.path.ismount(full_path)):
                        if (VERBOSE):
                            print("File skipped (Dir or Mount): %s" % full_path)
                        continue
                    try:
                        # if the target is a symlink (soft one), this will
                        # dereference it - change the value to the actual target file
                        full_path = os.path.realpath(full_path)
                        file_size = os.path.getsize(full_path)
                    except OSError:
                        # not accessible (permissions, etc) - pass on
                        continue
                    if (file_size >= MINIMUM_FILE_SIZE):
                        files_by_size[file_size].append(full_path)
                        hashed_files +=1
                    else:
                        skipped_files += 1
            else:
#                if (VERBOSE):
#                    print("Path excluded : %s" % dirpath)
                skipped_paths +=1

        if (VERBOSE):
            print("Paths scanned                   : %s" % scanned_paths)
            print("Paths skipped (excluded)        : %s" % skipped_paths)
            print("Files hashed (size)             : %s" % hashed_files)
            print("Files skipped (Min Size not met): %s" % skipped_files)

    # ########################################################
    # Step 2 : For all files with the same size Create 
    #          a dictionary of the hashes of the first 1K
    #          chunk, having the hash and file size as key
    #          in files_by_small_hash[(file_size, small_hash)]
    # ########################################################

    hashed_files=0
    skipped_files=0
    unique_files=0

    if (VERBOSE):
        print("\n===== STEP 2 - hash 1K chunk ")


    # For all files with the same file size, get their hash on the first 1024 bytes
    for file_size, files in files_by_size.items():
        if len(files) < 2:
            unique_files +=1
            continue  # this file size is unique, no need to spend cpu cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                hashed_files +=1
            except OSError:
                # the file access might've changed till the exec point got here
                if (VERBOSE):
                    print("Problem accessing File %s" % filename)
                skipped_files +=1 
                continue

            # The hash of the first chunk might be identical for files
            # with different sizes. Therefore we also use the file_size
            # as a key here

            files_by_small_hash[(file_size, small_hash)].append(filename)

    if (VERBOSE):
        print("Files hashed (1K chunk)     : %s" % hashed_files)
        print("Files skipped (unique size) : %s" % unique_files)
        print("Files skipped (problems)    : %s" % skipped_files)
        print("\n===== STEP 3 - full hash %s files" % hashed_files)

    skipped_files = 0
    hashed_files = 0
    unique_files = 0

    # ########################################################
    # Step 3 : For all files with the same hash on the first 
    #          1024 bytes get their hash on the full file
    #          having the hash as key
    #          in files_by_full_hash[full_hash]
    # ########################################################


    for files in files_by_small_hash.values():
        if len(files) < 2:
            # the hash of the first 1k bytes is unique -> skip this file
            unique_files += 1
            continue

        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
                hashed_files += 1
            except OSError:
                # the file access might've changed till the exec point got here
                skipped_files += 1
                continue
            
            # Add this file to the list of others sharing the same full hash
            files_by_full_hash[full_hash].append(filename)

    if (VERBOSE):
        print("Files hashed (full)               : %s" % hashed_files)
        print("Files skipped (unique chunk hash) : %s" % unique_files)
        print("Files skipped (problems)          : %s" % skipped_files)
        print("\n===== STEP 4 - decount %s potential duplicates" % hashed_files)

    # ########################################################
    # Step 4 : Now go through the list of all files with
    #          the same hash
    # ########################################################

    hashed_files = 0
    unique_files = 0
    skipped_files = 0
    deduped_files = 0
    error_files = 0
    unique_inodes=0

    # Now, print a summary of all files that share a full hash
    for file_list in files_by_full_hash.values():
        if len(file_list) < 2:
            # Only one file, it's unique
            unique_files += 1
            continue
        else:
            hashed_files += 1
            [d,e] = dedupe_list(file_list)
            if (DRY_RUN):
                skipped_files += d
            else:
                deduped_files += d
            error_files += e
            if ((d<1) and (e<1)):
                unique_inodes += 1


    if (VERBOSE):
        print("Duplicate File lists:            %s" % hashed_files)
        print("Files skipped (unique hash):     %s" % unique_files)
        print("Files skipped (dry-run):         %s" % skipped_files)
        print("Files de-duped (linked):         %s" % deduped_files)
        print("File sets skipped (unique inode) %s" % unique_inodes)
        print("Files skipped (error):           %s" % error_files)

# ##########################################
# print usage and exit - called if no args
# given or -h, --help specified
# ##########################################

def print_usage_and_exit():
    print ("\nUsage: %s [OPTIONS] <path> [<path>...]\n" % sys.argv[0])
    print ('path:          Path to dedupe\n')
    print ('-d, --dryrun:  no action, just dry run')
    print ('-h, --help:    show help')
    print ('-v, --verbose: Show what is happening\n')
    print ('-m, --minsize: Output What-if but do not take action\n')
    sys.exit()

# ##########################################
# checkargs checks command line arguments
# ##########################################

def checkargs(argv):
    global EXCLUDE_PATH_PATTERNS
    global VERBOSE
    global DRY_RUN
    global MINIMUM_FILE_SIZE
    opts, args = getopt.getopt(argv,"hvdm:",["help","verbose","dryrun","minsize="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage_and_exit()
        elif opt in ("-v", "--verbose"):
            VERBOSE=True
        elif opt in ("-d", "--dryrun"):
            DRY_RUN=True
        elif opt in ("-m", "--minsize"):
            MINIMUM_FILE_SIZE = int(arg)
    path = args
    return(path)

# ##########################################
# Main entry point
# ##########################################

if __name__ == "__main__":
    if sys.argv[1:]:
        path=checkargs(sys.argv[1:])
        if (VERBOSE):
            print("Verbose mode on")
        if (DRY_RUN):
            print("Dry Run mode on")
        print("minimum File Size = %s" % MINIMUM_FILE_SIZE)
        print("Scanning path(s) %s for duplicates" % path)
        check_for_duplicates(path)
    else:
        print_usage_and_exit()
