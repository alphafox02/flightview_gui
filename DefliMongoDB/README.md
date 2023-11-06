#### *A huge thank you goes out to @BigMaxi! His countless hours to improve and test these scripts have been invaluable!*

# Defli Installation and Update Scripts
These shell scripts help to install the Defli ground station. One script installs the base Defli ground station on a new device. Another script installs the new Defli MongoDB Connector on new or existing ground stations. A third script removes the old SOCAT connector from a ground station. These scripts are compatible with the 64-bit version of Ubuntu 20.04, 22.04, and 23.04 as well as Rasberry Pi OS. The current recommended OS from Defli Networks is Ubuntu 22.04. 

## MongoDB Connector Installation Script
Use this script to install the new MongoDB connector on your new or existing Defli Ground station.

### Usage
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/dealcracker/DefliMongoDB/master/installMongo.sh)"
```
	
## Defli Ground Station Installation Script
Use this script to install the base Defli ground station on a new device. This script also installs the graphs package. You will be prompted to enter the latitude and longitude of your ground station. Note that this script will reboot your device at the end of the installation. 

After rebooting (at the end of the installation), please run 'sudo autogain1090' and then run the MongoDB Connector install script.

### Usage
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/dealcracker/DefliMongoDB/master/installDefli.sh)"
```

## Defli MongoDB Connector Service Update Script
Use this script if you have previously installed he MongoDB connector using the manual instructions. This script will update the service configuration for better reliability. 

### Usage
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/dealcracker/DefliMongoDB/master/updateService.sh)"
```


## SOCAT Removal Script
Use this script to remove the old obsolete SOCAT connector from your existing ground station device.

### Usage
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/dealcracker/DefliMongoDB/master/removeSOCAT.sh)"
```

## Troubleshooting

### Service Failed To Start
If the MongoBD service does not start at the end of the MongoBD install script, try restarting the service.
```
sudo systemctl start adsb_collector
```
If the service still does not run, try rebooting the device. 
```
sudo reboot
```
Then check the service status again
```
sudo systemctl status adsb_collector
```

### Update your OS
If you are seeing errors while running the scripts, it may be helpful to update your device OS. 

```
sudo apt update -y
sudo apt upgrade -y
```


### Purple Screen

If during the installation you see a purple screen that asks "Which services should be restarted?", please hit enter to continue.

![alt text](https://github.com/dealcracker/DefliMongoDB/blob/main/purpleScreen.png?raw=true)
