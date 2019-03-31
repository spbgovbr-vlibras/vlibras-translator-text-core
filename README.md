<div align="center">
  <a href="http://www.vlibras.gov.br/">
    <img
      alt="VLibras"
      src="http://www.vlibras.gov.br/assets/imgs/IcaroGrande.png"
    />
  </a>
</div>

# VLibras Translator (Core)

VLibras Translation Service Core.

![Version](https://img.shields.io/badge/version-v0.0.0-blue.svg)
![License](https://img.shields.io/badge/license-LGPLv3-blue.svg)
![VLibras](https://img.shields.io/badge/vlibras%20suite-2019-green.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAUCAYAAAC9BQwsAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH4wIHCiw3NwjjIgAAAQ9JREFUOMuNkjErhWEYhq/nOBmkDNLJaFGyyyYsZzIZKJwfcH6AhcFqtCvFDzD5CQaTFINSlJJBZHI6J5flU5/P937fube357m63+d+nqBEagNYA9pAExgABxHxktU3882hjqtd9d7/+lCPsvpDZNA+MAXsABNU6xHYQ912ON2qC2qQ/X+J4XQXEVe/jwawCzwNAZp/NCLiDVgHejXgKIkVdGpm/FKXU/BJDfytbpWBLfWzAjxVx1Kuxwno5k84Jex0IpyzdN46qfYSjq18bzMHzQHXudifgQtgBuhHxGvKbaPg0Klaan7GdqE2W39LOq8OCo6X6kgdeJ4IZKUKWq1Y+GHVjF3gveTIe8BiCvwBEZmRAXuH6mYAAAAASUVORK5CYII=)

## Table of Contents

- **[Getting Started](#getting-started)**
  - [System Requirements](#system-requirements)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- **[Running the Tests](#running-the-tests)**
- **[Deployment](#deployment)**
  - [Deploy Tools](#deploy-tools)
  - [Deploying](#deploying)
- **[Contributors](#contributors)**
- **[License](#license)**


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### System Requirements

* OS: Ubuntu 18.04.2 LTS (Bionic Beaver)   
* Processor: -  
* Memory: -  
* Storage: -

### Prerequisites

Before starting the installation, you need to install some prerequisites:

[Translator Lib]()
> Waiting for intallation guide

<br/>

[RabbitMQ](https://www.rabbitmq.com/)

```sh
wget -O - "https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc" | sudo apt-key add -
```

```sh
sudo apt install apt-transport-https
```

```sh
echo "deb https://dl.bintray.com/rabbitmq/debian bionic main" | sudo tee /etc/apt/sources.list.d/bintray.rabbitmq.list
```

```sh
sudo apt update
```

```sh
sudo apt install -y rabbitmq-server
```

### Installing

After installing all the prerequisites, install the project by running the command:

```sh
cd worker/
```

```sh
sudo make install
```

To test the installation, simply start the translation Core with the following command:

```sh
cd worker/
```

```sh
make dev start
```

## Running the Tests

> In writing process.

## Deployment

These instructions will get you a copy of the project up and running on a live System.

### Deploy Tools

To fully deployment of this project its necessary to have installed and configured the Docker Engine and Kubernetes Container Orchestration.

[Docker](https://www.docker.com/)

Update the apt package index:

```sh
sudo apt update
```

Install packages to allow apt to use a repository over HTTPS:

```sh
sudo apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
```

Add Docker’s official GPG key:

```sh
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

Use the following command to set up the stable repository:

```sh
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

Update the apt package index:

```sh
sudo apt update
```

Install the latest version of Docker and containerd:

```sh
sudo apt install -y docker-ce docker-ce-cli containerd.io
```

<br/>

[Kubernetes](https://kubernetes.io/)

Update the apt package index:

```sh
sudo apt update
```

Install packages to allow apt to use a repository over HTTPS:

```sh
sudo apt install -y apt-transport-https
```

Add Kubernetes’s official GPG key:

```sh
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
```

Use the following command to set up the main repository:

```sh
echo "deb https://apt.kubernetes.io/ kubernetes-bionic main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
```

Update the apt package index:

```sh
sudo apt update
```

Install the kubectl:

```sh
sudo apt install -y kubectl
```

### Deploying

> Note: if you already have RabbitMQ running on your cluster, skip to the server configuration.

Once kubectl is installed and set, run the following commands:

```sh
kubectl apply -f kubernetes/rabbitmq.yaml
```

```sh
kubectl expose deployment rabbitmq --type=ClusterIP
```

The commands above will start the RabbitMQ pods. You must configure a volume set to be used by it. By default it set to be used in a Google Cloud Platform (GCP).

Then, open the server.yaml file and edit the environment variable below to match your settings.

```sh
- name: AMQP_HOST
  value: "RabbitMQ-ClusterIP"
```

Finally, starting the server by running the commands:

```sh
kubectl apply -f kubernetes/server.yaml
```

```sh
kubectl expose deployment translatorcore --port=80 --type=LoadBalancer
```

## Contributors

* Jonathan Brilhante - <jonathan.brilhante@lavid.ufpb.br>
* Wesnydy Ribeiro - <wesnydy@lavid.ufpb.br>

## License

This project is licensed under the LGPLv3 License - see the [LICENSE](LICENSE) file for details.