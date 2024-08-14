#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
import yaml
import os
import sys
import time

# Function to check for sudo privileges
def check_sudo():
    if os.geteuid() != 0:
        return False
    return True

# Function to check if a Docker service is running
def is_service_running(service_name):
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], stdout=subprocess.PIPE)
    return service_name in result.stdout.decode().splitlines()

# Function to update the running indicator
def update_running_indicator(service_name, running_label):
    time.sleep(1)  # Adding a small delay to allow Docker to update the service status
    if is_service_running(service_name):
        running_label.config(text="Running", foreground="green")
    else:
        running_label.config(text="Not Running", foreground="red")

# Check for sudo privileges before running the script
if not check_sudo():
    print("This script requires sudo privileges. Please run it with sudo.")
    sys.exit(1)

# Function to start a Docker service
def start_service(file_path, lat_entry, lon_entry, tz_entry, running_label):
    apply_temporary_changes(file_path, lat_entry.get(), lon_entry.get(), tz_entry.get())
    subprocess.Popen(["docker", "compose", "--file", file_path, "up", "-d"])
    time.sleep(1)  # Adding a small delay to allow Docker to start the service
    update_running_indicator(file_path.split('-')[2].split('.')[0], running_label)

# Function to stop a Docker service
def stop_service(file_path, running_label):
    subprocess.Popen(["docker", "compose", "--file", file_path, "down"])
    time.sleep(1)  # Adding a small delay to allow Docker to stop the service
    update_running_indicator(file_path.split('-')[2].split('.')[0], running_label)

# Function to start the airspy_adsb service
def start_airspy_service(file_path, running_label):
    subprocess.Popen(["docker", "compose", "--file", file_path, "up", "-d"])
    time.sleep(1)  # Adding a small delay to allow Docker to start the service
    update_running_indicator("airspy_adsb", running_label)

# Function to stop the airspy_adsb service
def stop_airspy_service(file_path, running_label):
    subprocess.Popen(["docker", "compose", "--file", file_path, "down"])
    time.sleep(1)  # Adding a small delay to allow Docker to stop the service
    update_running_indicator("airspy_adsb", running_label)

# Function to load the current configuration values for the airspy_adsb service
def load_airspy_adsb_config(file_path):
    pass  # No environment variables to load for airspy_adsb

# Create the main window
window = tk.Tk()
window.title("FlightView GUI")

# Create a notebook for split view
notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Create a tab for each Docker service
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="Service 1 (airspy_adsb)")
notebook.add(tab2, text="Service 2 (tar1090)")

# Create and configure widgets for Service 1 (airspy_adsb)
start_button_1 = tk.Button(tab1, text="Start airspy_adsb Service", command=lambda: start_airspy_service("docker-compose-airspy-adsb.yml", running_label_1))
stop_button_1 = tk.Button(tab1, text="Stop airspy_adsb Service", command=lambda: stop_airspy_service("docker-compose-airspy-adsb.yml", running_label_1))
running_label_1 = tk.Label(tab1, text="Not Running", foreground="red")

# Load and display the current configuration values for Service 1 (airspy_adsb)
load_airspy_adsb_config("docker-compose-airspy-adsb.yml")
update_running_indicator("airspy_adsb", running_label_1)

# Arrange widgets for Service 1 (airspy_adsb)
start_button_1.grid(row=0, column=0, padx=10, pady=10)
stop_button_1.grid(row=0, column=1, padx=10, pady=10)
running_label_1.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Create and configure widgets for Service 2 (tar1090)
start_button_2 = tk.Button(tab2, text="Start tar1090 Service", command=lambda: start_service("docker-compose-tar1090.yml", lat_entry, lon_entry, tz_entry, running_label_2))
stop_button_2 = tk.Button(tab2, text="Stop tar1090 Service", command=lambda: stop_service("docker-compose-tar1090.yml", running_label_2))
save_button_2 = tk.Button(tab2, text="Save Changes", command=lambda: save_changes("docker-compose-tar1090.yml", lat_entry.get(), lon_entry.get(), tz_entry.get()))
lat_label_2 = tk.Label(tab2, text="Latitude:")
lon_label_2 = tk.Label(tab2, text="Longitude:")
tz_label_2 = tk.Label(tab2, text="Timezone:")
lat_entry = tk.Entry(tab2)
lon_entry = tk.Entry(tab2)
tz_entry = tk.Entry(tab2)
running_label_2 = tk.Label(tab2, text="Not Running", foreground="red")

# Load and display the current configuration values for Service 2 (tar1090)
load_current_config("docker-compose-tar1090.yml", lat_entry, lon_entry, tz_entry)
update_running_indicator("tar1090", running_label_2)

# Arrange widgets for Service 2 (tar1090)
start_button_2.grid(row=0, column=0, padx=10, pady=10)
stop_button_2.grid(row=0, column=1, padx=10, pady=10)
save_button_2.grid(row=4, column=0, padx=10, pady=10)
lat_label_2.grid(row=1, column=0, padx=10, pady=10)
lat_entry.grid(row=1, column=1, padx=10, pady=10)
lon_label_2.grid(row=2, column=0, padx=10, pady=10)
lon_entry.grid(row=2, column=1, padx=10, pady=10)
tz_label_2.grid(row=3, column=0, padx=10, pady=10)
tz_entry.grid(row=3, column=1, padx=10, pady=10)
running_label_2.grid(row=4, column=1, padx=10, pady=10)

# Start the GUI event loop
window.mainloop()

