#!/bin/bash

# ##########################################################################
# menu function
# ##########################################################################
# The menu function takes an array as parameter, e.g. ("Color" "blue" "red")
# it will then prompt "Please select a xxx" and replace xxx with the first 
# element of the array (in the above example "Please select a color")
# It then shows numbers starting from 1 and options you may chose
# ( 1 - blue, 2 - red in the example) and return the user's choice
# in the variable $choice
# ##########################################################################


menu() {
        choice=0

        while true; do
                XCHOICE=("$@")
                echo -e "\nplease select a $1"
                for (( i=1; i < ${#XCHOICE[@]} ; i++)) ; do
                        echo "$i - ${XCHOICE[$i]}"
                done
                read -n 1 -p "Your choice -> " choice
                echo -e 
                if (($choice >=1 && $choice < ${#XCHOICE[@]})); then  break ; fi
        done
}

# #### example (from the kali-linux-docker repo)

XREMOTE_ACCESS=vnc
XREMOTE_CHOICE=("vnc" "rdp" "x2go")
menu  "Remote Access Option" ${XREMOTE_CHOICE[@]}
XREMOTE_ACCESS=${XREMOTE_CHOICE[$choice-1]}