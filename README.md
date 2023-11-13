# ACARS Hub GUI

Welcome to the ACARS Hub GUI repository. This project provides a user-friendly graphical interface to manage and configure Docker-based ACARS services, including `tar1090`, `readsb`, and `acarshub`. With this GUI, you can easily adjust basic settings, start and stop services, and enjoy real-time monitoring of ADSB and ACARS data.

![ACARS Hub GUI](acars_hub_gui.png)

## Getting Started

To use this project, follow these steps:

### Prerequisites

- A Linux system (tested on WarDragon)
- `docker-compose` installed
- Git (for cloning the repository)
- One or more RTL-SDR devices (for `readsb` , `acarshub` and `dump978`)

### Clone the Repository

You can clone this repository to any directory you prefer on your local system. If you are on WarDragon, you can also find it in `/usr/src`.

```bash
git clone https://github.com/alphafox02/acars_hub_gui.git
```
Update the Repository (Optional)

If you have already cloned the repository and want to update it, navigate to the project directory and run the following command:

```bash
git pull
```

### Using the GUI

The FlightView GUI offers an intuitive interface to configure and manage Aircraft services. It includes three tabs for the following services:

    tar1090 Configuration
        Configure docker-compose-tar1090.yml settings such as latitude, longitude, and timezone.
        Start and stop the tar1090 service.
        Real-time service status display.

    readsb Configuration
        Configure docker-compose-readsb.yml settings, including basic options.
        Manually configure advanced settings such as RTL-SDR device configuration in the YAML file.
        Start and stop the readsb service.
        Real-time service status display.

    acarshub Configuration
        Configure docker-compose-acars-vhf.yml settings, including basic options.
        Manually configure advanced settings such as RTL-SDR device configuration in the YAML file.
        Start and stop the acarshub service.
        Real-time service status display.

Use these tabs to set basic parameters like latitude (LAT), longitude (LONG), timezone (TZ), and feed ID (FEED_ID). For advanced settings and additional configurations, you'll need to manually edit the corresponding Docker Compose YAML files. The GUI simplifies basic configurations but may not cover all advanced options.

### Access the Web Interfaces

After configuring the services, you can access their web interfaces as follows:

    ACARS Hub: http://localhost
    READSB: http://localhost:8080
    tar1090: http://localhost:8078

Make sure that you have the required RTL-SDR devices connected and properly recognized by your system for services that use them.

Enjoy using the FlightView GUI to effortlessly manage and monitor your aircraft services. If you have any questions or encounter issues, please feel free to open an issue in this repository.
