#!/bin/bash
# install the Defli MongoDB connector
# Copyright (c) 2023 dealcracker
#
# last modified: 2020-Oct-05


#enforce sudo
if ! [[ $EUID = 0 ]]; then
    echo "Please run this script with 'sudo'..."
    exit 1
fi

#change to user's home dir
user_dir=$(getent passwd ${SUDO_USER:-$USER} | cut -d: -f6)
cd $user_dir

#get the user name
user_name=sudo who am i | awk '{print $1}'

echo "============ MongoDB Connector =============I=="
echo "Installing the MongoDB connector for Defli." 

#Determine IP address to use in config.py
#test if localhost is reachable
  echo "Determining local IP address..."
  ping -c 3 localhost > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    ip_address="localhost"
    echo "Using localhost instead of fixed IP address"
  else
    # get the eth0 ip address
    ip_address=$(ip addr show eth0 | awk '/inet / {print $2}' | cut -d'/' -f1)
    #Check if eth0 is up and has an IP address
    if [ -n "$ip_address" ]; then
      echo "Using wired ethernet IP address: $ip_address"
    else
      # Get the IP address of the Wi-Fi interface using ip command
      ip_address=$(ip addr show wlan0 | awk '/inet / {print $2}' | cut -d'/' -f1)
      if [ -n "$ip_address" ]; then
        echo "Using wifi IP address: $ip_address"
      else
        echo "Unable to determine your device IP address"
        echo "No IP address. Installation Failed."
        exit 1
      fi
    fi
  fi

echo ""
echo "Updating package list..."
# Update the package list
apt update -y

echo ""
echo "Cloning ABS-D data collector for MongoDB..."
#clone adsb-data-collector-mongodb
git clone https://github.com/dbsoft42/adsb-data-collector-mongodb.git

echo ""
echo "Installing Python..."
# Install python3-pip
apt install -y python3-pip

#patch coroutines if needed (experimental)
#Attempt 1
if [ -e "/usr/lib/python3.10/asyncio/coroutines.py" ]; then
  mv /usr/lib/python3.11/asyncio/coroutines.py /usr/lib/python3.11/asyncio/coroutines.py20230927 > /dev/null 2>&1
  cp /usr/lib/python3.10/asyncio/coroutines.py /usr/lib/python3.11/asyncio/coroutines.py > /dev/null 2>&1
fi
#Attempt 2
if [ -e "/snap/core22/867/usr/lib/python3.10/asyncio/coroutines.py" ]; then
  mv /usr/lib/python3.11/asyncio/coroutines.py /usr/lib/python3.11/asyncio/coroutines.py20230927 > /dev/null 2>&1
  cp /snap/core22/867/usr/lib/python3.10/asyncio/coroutines.py /usr/lib/python3.11/asyncio/coroutines.py > /dev/null 2>&1
fi

# Istall modules
echo ""
echo "Installing Modules..."
#No longer using pip to install modules
# pip3 install aiohttp motor pymongo python-dateutil dnspython
apt install python3-aiohttp -y # BM - Changed to this code section to fix ubuntu
apt install python3-motor -y
# apt install python3-pymongo -y not needed as installed as dependency in motor install
# read -p "Press Enter to resume ..."
apt install python3-dateutil -y
apt install python3-dnspython -y

echo ""
echo "Preparing the connector config.py file..."
# copy the default config.py template
cd adsb-data-collector-mongodb
rm -f config.py 
cp config_template.py config.py

# replace text in config.py
original_line1="username:password@url.mongodb.net/myFirstDatabase"
new_line1="team:kaPAIYJz1EhpWtTO@defli1.snqvy.mongodb.net/"

original_line2=": 'adsb'"
new_line2=": 'defli1'"

original_line3="http://localhost/dump1090/data/aircraft.json"
new_line3="http://"$ip_address":8078/data/aircraft.json"

sed -i "s|$original_line1|$new_line1|g" "config.py"
sed -i "s|$original_line2|$new_line2|g" "config.py"
sed -i "s|$original_line3|$new_line3|g" "config.py"

echo "Preparing the adsb_collector service..."
#get the working directory
current_dir=$(pwd)
chown -R $user_name:$user_name $current_dir

#compose the exec start line
exec_start_line="ExecStart=/usr/bin/python3 $current_dir/adsb-data-collector.py"

service_file_path="/lib/systemd/system/adsb_collector.service"

#remove any existing adsb_collector.service file
if [ -e "$service_file_path" ]; then
	echo "Disable and removing exiting service file..."
  systemctl stop adsb_collector
  systemctl disable adsb_collector 
	rm -f /lib/systemd/system/adsb_collector.service
fi

# Create the service file and add the first line of text
echo "Create new service file..."
touch touch $service_file_path

# Check if the file exists
if [ ! -e "$service_file_path" ]; then
  echo "Error: Could not create service file."
  echo "Aborting installation"
  exit 1
fi

# Add needed lines ot service file
echo "[Unit]" >> $service_file_path
echo "Description=adsb_collector" >> $service_file_path
echo "After=multi-user.target" >> $service_file_path
echo "[Service]" >> $service_file_path
echo "Type=simple" >> $service_file_path
echo "$exec_start_line" >> $service_file_path
echo "Restart=always" >> $service_file_path
echo "RestartSec=30" >> $service_file_path
echo "StartLimitInterval=1" >> $service_file_path
echo "StartLimitBurst=100" >> $service_file_path
echo "[Install]" >> $service_file_path
echo "WantedBy=multi-user.target" >> $service_file_path

#enable and start the adsb colletor service
systemctl enable adsb_collector 
systemctl start adsb_collector

echo "Waiting for service to start..."
sleep 3

public_ip=$(curl -s https://ipinfo.io/ip)

#get the service status
service_name="adsb_collector"
status=$(systemctl is-active "$service_name")

# Check the status
echo ""
case "$status" in
  "active")
    echo "************************************"
    echo "Installation Completed Successfully!" 
    echo "$service_name is running properly."
    echo 
    echo "Your public IP addess is: $public_ip  Be sure to enter this address in Defli-Wallet."
    echo "You can enter 'sudo systemctl status adsb_collector' anytime to check the connector status."

    ;;
  "inactive")
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Installation Finished with a warning." 
    echo "Warning: $service_name is not running."
    echo ""
    echo "Try entering 'sudo systemctl start adsb_collector' to start the service."
    echo "Then enter 'sudo systemctl status adsb_collector' to check the status."
    ;;
  "failed")
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Installation Finished but failed to start." 
    echo "Error: $service_name is in a failed state."
    echo ""
    echo "Try entering 'sudo systemctl start adsb_collector' to start the service."
    echo "Then enter 'sudo systemctl status adsb_collector' to check the status."
    ;;
  *)
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Installation Complete." 
    echo "Status of $service_name: $status"
    echo "You can enter 'sudo systemctl status adsb_collector' to check the status."
    ;;
esac
