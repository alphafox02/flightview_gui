# Defli MongoDB Connector

This Docker container runs a MongoDB connector for Defli, facilitating data collection from aircraft ADS-B receivers.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

## Steps to Build and Run the Docker Container

1. **Build the Docker Image**

    Use the following command to build the Docker image from the provided Dockerfile:

    ```bash
    docker build -t deflimongodb .
    ```

    Ensure that the image name (`deflimongodb`) suits your naming convention.

2. **Run the Docker Container**

    Start a new container from the built image:

    ```bash
    docker run -d deflimongodb
    ```

    This will launch the MongoDB connector within a Docker container.

3. **Verify Container Status**

    Check the running container and its status:

    ```bash
    docker ps -a
    ```

    You should see the newly created container listed.

4. **Access the Container (if needed)**

    To access the running container for inspection or to run additional commands:

    ```bash
    docker exec -it <container_name_or_id> bash
    ```

    Replace `<container_name_or_id>` with the actual name or ID of the running container.
