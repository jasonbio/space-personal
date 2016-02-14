#!/bin/bash
echo -e "---------------------------------------------------------------------------"
echo -e "This script will make the default directories for SpacePanel and download several ISOs for your local VMs:"
echo -e "---------------------------------------------------------------------------"
echo -e ""
echo -e "Configurations: /var/configs"
echo -e "Images: /var/images"
echo -e "Disks: /var/disks"
echo -e ""

read -p "Would you like to make the default directories? [y/N]:" response

if [[ $response =~ ^(yes|y| ) ]]; then
    mkdir /var/configs /var/images /var/disks
fi

echo -e "This script can also download several ISOs to get started with your local VMs."
echo -e " "
read -p "Would you like to download Centos 6.6? [y/N]" response1
echo -e " "

if [[ $response1 =~ ^(yes|y| ) ]]; then
    wget https://spacepanel.io/dist/disk-images/centos-6.6-x86_64.iso -P /var/images 
fi

echo -e " "
read -p "Would you like to download Centos 7.0? [y/N]" response2
echo -e  " "

if [[ $response2 =~ ^(yes|y| ) ]]; then
    wget https://spacepanel.io/dist/disk-images/centos-7.0-x86_64.iso -P /var/images
fi

echo -e " "
read -p "Would you like to download Debian 7.8? [y/N]" response3
echo -e " "

if [[ $response3 =~ ^(yes|y| ) ]]; then
    wget https://spacepanel.io/dist/disk-images/debian-7.8.0-amd64.iso -P /var/images
fi

echo -e " "
read -p "Would you like to download Ubuntu 14.04? [y/N]" response4
echo -e " "

if [[ $response4 =~ ^(yes|y| ) ]]; then
    wget https://spacepanel.io/dist/disk-images/debian-7.8.0-amd64.iso -P /var/images
fi


