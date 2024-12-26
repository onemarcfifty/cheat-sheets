## Pull default setup from gitea

An alternative to using deployment tools, ansible-pull etc. is to just put a git pull into the `/etc/rc.local`file which gets executed at startup. One could pull a script from a local gitea server (or even a public github repo) and execute it at startup, e.g. to set VLANs or SSIDs etc:

```
logger "@@@@@@@@ rc.local started"

# check if wget is available
# We will not use git to pull the scripts but
# rather simple wget

if (which wget) ; then
    logger "wget is installed"
else
    opkg update
    opkg install wget
fi

BASEURL=https://gitea.exammple.com/marc/ap-settings/raw/branch/master
(wget --no-check-certificate $BASEURL/launch.sh -O -) | ash

logger "@@@@@@@@ rc.local ends"
exit 0
```
