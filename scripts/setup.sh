#!/bin/bash

# Pretty Colors
OK='\033[92m'
WARNING='\033[93m'
FAIL='\033[91m'
ENDC='\033[0m'

# Determine Distribution
if [ -f /etc/debian_version ]
  then
    ver=`cat /etc/*release | grep ^ID= | cut -d "=" -f 2`
    if [ $ver == "ubuntu" ]
      then OS="ubuntu"
    elif [ $ver == 'debian' ]
      then OS="debian"
    else
      echo -e $FAIL "Your System is Not Supported" $ENDC
      exit 1
    fi
elif [ -f /etc/redhat-release ]
  then OS="centos"
else
  echo -e $FAIL "Your System is Not Supported" $ENDC
  exit 1
fi

echo -e "Welcome to Space!"
echo -e "---------------------------------------------"
echo -e "This script will attempt to start and install all system services necessary to run space."
echo -n
echo -e $OK "Updating $OS packages..." $ENDC

if [ $OS == "centos" ]
  then
    yum update -y
    yum install -y python-setuptools
else
  apt-get update
  apt-get install -y python-setuptools
fi

easy_install pip


echo -n
echo -e $OK "Adding MongoDB repo, your server is about to become #webscale" $ENDC

if [ $OS == "centos" ]
  then
    cp /srv/space/conf.d/mongodb.repo /etc/yum.repos.d/mongodb.repo
    yum update -y
elif [ $OS == "debian" ]
  then
    apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list
    apt-get update
else
  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
  echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list
  apt-get update
fi


echo -n
echo -e $OK "Getting package for RabbitMQ..." $ENDC

if [ $OS == "centos" ]
  then
    rpm -Uvh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
    yum update -y
    yum install -y erlang
    rpm --import http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
    rpm -Uvh http://www.rabbitmq.com/releases/rabbitmq-server/v3.1.4/rabbitmq-server-3.1.4-1.noarch.rpm
    yum update -y
else
  echo 'deb http://www.rabbitmq.com/debian/ testing main' | tee /etc/apt/sources.list.d/rabbitmq.list
  wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
  apt-key add rabbitmq-signing-key-public.asc
  apt-get update
  apt-get install -y erlang
fi

echo -n
echo -e $OK "Installing mongodb-org rabbitmq-server qemu-kvm qemu-img virt-manager libvirt libvirt-python python virtinst libvirt-client virt-install virt-viewer dhcp" $ENDC

if [ $OS == "centos" ]
  then
    for package in gcc mongodb-org rabbitmq-server qemu-kvm qemu-img virt-manager libvirt libvirt-python python virtinst libvirt-client virt-install virt-viewer dhcp python-devel
    do

    echo -n
    echo -e $OK "Processing ${package}..." $ENDC

    yum install -y $package

    echo -n
    echo -e $OK "Done." $ENDC

    done
else
  for package in gcc python-dev mongodb-org rabbitmq-server kvm qemu-utils virt-manager libvirt libvirt-python python virtinst libvirt-client virt-install virt-viewer isc-dhcp-server python-devel
  do

  echo -n
  echo -e $OK "Processing ${package}..." $ENDC

  apt-get install -y $package

  echo -n
  echo -e $OK "Done." $ENDC

  done

fi



echo -n
echo -e $OK "Creating symlink for init.d file..." $ENDC

ln -s /srv/space/scripts/space.sh /etc/init.d/space

echo -n
echo -e $OK "Done." $ENDC

echo -n
echo -e $OK "Installing python requirements from requirements.txt..." $ENDC

pip install -r /srv/space/requirements.txt

echo -n
echo -e $OK "Done." $ENDC

echo -n
echo -e $OK "Finished installing packages..." $ENDC

echo -n
echo -e $OK "Starting rabbitmq..." $ENDC

service rabbitmq-server start

echo -n
echo -e $OK "Starting DHCPD..." $ENDC

pkill dnsmasq
service dhcpd start

echo -n
echo -e $OK "Starting MongoDB..." $ENDC

service mongod start

echo -n
echo -e $OK "Starting libvirtd..." $ENDC

service libvirtd start

echo -n
echo -e $OK "Starting RabbitMQ..." $ENDC

service rabbitmq-server start

echo -n
echo -e $OK "Starting Space..." $ENDC

mkdir /var/log/space

service space start

echo -n
echo -e $OK "Starting celery worker..." $ENDC

export C_FORCE_ROOT="true"
sh /srv/space/scripts/celery.sh

echo -n
echo -e "Starting disk configuration script..." $ENDC 

echo -n
echo -e "----------------------------------------"
echo -e $OK "All done, enjoy!" $ENDC
echo -e "Consider running ./scripts/setup_diskimages.sh to make default directories and download disk images."
