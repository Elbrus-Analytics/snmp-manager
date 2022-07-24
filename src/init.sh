#!bin/bash
echo "Started setup for snmp-manager:"
while true; do
read -p "Do you want do proceed? (y/n)" yn
case $yn in
    [yY] | "yes" | "Yes" ) break;;
    [nN] | "no" | "No" ) echo "Stoping setup installation...";
            exit;;
    * ) echo "Invalid response";;
esac
done