# FlightView GUI

Welcome to the FlightView GUI repository. This project provides a user-friendly graphical interface to manage and configure Docker-based aircraft-related services, including `tar1090`, `readsb`, and `acarshub`. With this GUI, you can easily adjust basic settings, start and stop services, and enjoy real-time monitoring of ADSB and ACARS data.

## Getting Started

To use this project, follow these steps:

### Prerequisites

- A Linux system (tested on WarDragon)
- Docker Compose
- Docker installed
- Git (for cloning the repository)
- One or more RTL-SDR devices (for `readsb`, `acarshub`, and `dump978`)

### Set up Docker's apt repository

First, set up Docker's apt repository. These steps are already completed on the WarDragon. Open a terminal and run the following commands:

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install the Docker packages.
# To install the latest version, run:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Clone the Repository

You can clone this repository to any directory you prefer on your local system. If you are on WarDragon, you can also find it in `/usr/src`.

```bash
git clone https://github.com/alphafox02/flightview_gui.git
```

#### Update the Repository (Optional)

If you have already cloned the repository and want to update it, navigate to the project directory and run the following command:

```bash
git pull
```

### Using the GUI

The FlightView GUI offers an intuitive interface to configure and manage Aircraft services. It includes three tabs for the following services (for now):

- **tar1090 Configuration:**
  - Configure `docker-compose-tar1090.yml` settings such as latitude, longitude, and timezone.
  - Start and stop the `tar1090` service.
  - Real-time service status display.

- **readsb Configuration:**
  - Configure `docker-compose-readsb.yml` settings, including basic options.
  - Manually configure advanced settings such as RTL-SDR device configuration in the YAML file.
  - Start and stop the `readsb` service.
  - Real-time service status display.

- **acarshub Configuration:**
  - Configure `docker-compose-acars-vhf.yml` settings, including basic options.
  - Manually configure advanced settings such as RTL-SDR device configuration in the YAML file.
  - Start and stop the `acarshub` service.
  - Real-time service status display.

Use these tabs to set basic parameters like latitude (LAT), longitude (LONG), timezone (TZ), and feed ID (FEED_ID). For advanced settings and additional configurations, you'll need to manually edit the corresponding Docker Compose YAML files. The GUI simplifies basic configurations but may not cover all advanced options.

### Access the Web Interfaces

After configuring the services, you can access their web interfaces as follows:

- **ACARS Hub:** [http://localhost](http://localhost)
- **READSB:** [http://localhost:8080](http://localhost:8080)
- **tar1090:** [http://localhost:8078](http://localhost:8078)

Make sure that you have the required RTL-SDR devices connected and properly recognized by your system for services that use them.

### Links to Docker Repositories

The Docker Compose YAML files in this project pull in the following Docker images:

- [ACARS Hub](https://github.com/sdr-enthusiasts/docker-acarshub)
- [Readsb-protobuf](https://github.com/sdr-enthusiasts/docker-readsb-protobuf)
- [Dump978](https://github.com/sdr-enthusiasts/docker-dump978)
- [DumpVDL2](https://github.com/sdr-enthusiasts/docker-dumpvdl2)
- [Tar1090](https://github.com/sdr-enthusiasts/docker-tar1090)
- [DefliMongoDB](https://github.com/alphafox02/docker-deflimongodb)

Explore these repositories to learn more about each component and contribute to their development.

### Troubleshooting

If you encounter issues accessing the web interfaces, check your firewall settings to ensure they allow connections to the specified ports.

Enjoy using the FlightView GUI to effortlessly manage and monitor your aircraft services. If you have any questions or encounter issues, please feel free to open an issue in this repository.

### Contributing

We welcome contributions! If you have feedback, encounter issues, or want to contribute new features, please open an issue or submit a pull request.
