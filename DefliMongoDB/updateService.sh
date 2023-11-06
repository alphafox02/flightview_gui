#!/bin/bash
# Update the Defli MongoDB connector service
# Copyright (c) 2023 dealcracker
#
# last modified: 2023-Oct-06

echo
echo "================ Connector Service Update =================="
echo "Updating the MongoDB connector serice to improve reliability" 

#enforce sudo
if ! [[ $EUID = 0 ]]; then
    echo
    echo "Please run this script with 'sudo'..."
    exit 1
fi

service_file_path="/lib/systemd/system/adsb_collector.service"

#check to see if a connector file exists
if [ ! -e "$service_file_path" ]; then
    echo
    echo "Error: There doesn't appear to be a connector service installed"
    exit 1
fi

#copy the exec_start line from the existing file
exec_start_pattern="ExecStart"
exec_start_line=$(grep -m 1 "^$exec_start_pattern" "$service_file_path")

#check if a line was copied
if [ ! -n "$exec_start_line" ]; then
    echo
    echo "Error: The ExecStart line is missing from the serviee file"
    exit 1
fi

echo
echo "Stopping the adsb_collector service..."

#remove existing adsb_collector.service file
systemctl stop adsb_collector
systemctl disable adsb_collector 
rm -f $service_file_path

echo
echo "Updateing the adsb_collector service..."

# Create the service file and add the first line of text
touch $service_file_path

# Check if the file exists
if [ ! -e "$service_file_path" ]; then
  echo
  echo "Error: Could not create the new service file."
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

echo
echo "Waiting for updated service to start..."
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
    echo "Service Update Completed Successfully!" 
    echo "$service_name is running properly."
    echo 
    echo "Your public IP addess is: $public_ip  Be sure this matches the address in Defli-Wallet."
    echo "You can enter 'sudo systemctl status adsb_collector' anytime to check the connector status."
    ;;
  "inactive")
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Service Update Finished with a warning." 
    echo "Warning: $service_name is not running."
    echo ""
    echo "Try entering 'sudo systemctl start adsb_collector' to start the service."
    echo "Then enter 'sudo systemctl status adsb_collector' to check the status."
    ;;
  "failed")
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Service Update Finished but failed to start." 
    echo "Error: $service_name is in a failed state."
    echo ""
    echo "Try entering 'sudo systemctl start adsb_collector' to start the service."
    echo "Then enter 'sudo systemctl status adsb_collector' to check the status."
    ;;
  *)
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Service Update Complete." 
    echo "Status of $service_name: $status"
    echo "You can enter 'sudo systemctl status adsb_collector' to check the status."
    ;;
esac
