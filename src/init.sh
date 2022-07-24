#!/bin/bash
while true; do
read -p "Do you want to proceed with setup of the 'snmp-manager'? (y/n) " yn
case $yn in
    [yY] | "yes" | "Yes" ) break;;
    [nN] | "no" | "No" ) echo exiting...;
            exit;;
    * ) echo invalid response;;
esac
done
echo
sleep 0.25

SHAREDCONFIG=/var/elbrus/shared/.config
LOGPATH=/var/elbrus/shared/log
read -p "Where should the log be stored (dir) [$LOGPATH]: " LOGPATH
read -p "Where is the shared config stored [$SHAREDCONFIG]: " SHAREDCONFIG
SHAREDCONFIG=${SHAREDCONFIG:-/var/elbrus/shared/.config}
LOGPATH=${LOGPATH:-/var/elbrus/shared/log}


while true; do
echo 
echo "Should the log be stored at '$LOGPATH' ?"
read -p "Is the shared config stored at '$SHAREDCONFIG' ? (y/n/exit) " confirm
case $confirm in
    [yY] | "yes" | "Yes" ) break;;
    [nN] | "no" | "No" ) clear;
            read -p "Where should the log be stored (dir) [/var/elbrus/capture/]: " LOGPATH;
            read -p "Where is the shared config stored [$SHAREDCONFIG]: " SHAREDCONFIG;
            SHAREDCONFIG=${SHAREDCONFIG:-/var/elbrus/shared/.config};
            LOGPATH=${LOGPATH:-/var/elbrus/capture/};;
    [eE] | "exit" | "Exit" ) echo exiting...;
            exit;;
    * ) echo invalid response;;
esac
done

mkdir -p $LOGPATH

tee .env <<EOL
#global
SHAREDCONFIG=$SHAREDCONFIG

#paths
LOGFILEDIR=$LOGPATH
EOL

#returns src
SCRIPTDIR=$(dirname $(readlink -f "${BASH_SOURCE:-$0}"))

echo "Install dependencies ..."
pip3 install -r "$SCRIPTDIR/../requirements.txt"

echo "Cleaning up..."
rm -rf $(readlink -f "${BASH_SOURCE:-$0}")