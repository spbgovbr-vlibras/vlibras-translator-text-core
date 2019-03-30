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

### Prerequisites

To fully deployment this application its necessary to have instaled and configurated the Docker Engine (https://www.docker.com/) and Kubernetes Container Orchestration (https://kubernetes.io/)
Accomplishing this task change to datacenter to another. Acess all links above to fullfil your needs. 

### Instalation


If you already MongoDB and RabbitMQ running on your cluster, skip those steps.

Once kubectl is installed and set, run the following commands:

```sh
kubectl apply -f kubernetes/mongo.yaml 
kubectl expose rc mongo-controller --type=ClusterIP
```
These commands will start the MongoDB pods. You must configure a volume set to be used by it. By default it set to be used in a Google Cloud Plataform (GCP)

```sh
kubectl apply -f kubernetes/rabbitmq.yaml
kubectl expose deployment rabbitmq --type=ClusterIP
```
Following, this line starts up the RabbitMQ pod. As it happened to MongoDB, you must configure a volume set or use the default of a GCP.

Then , open the file server.yaml and edit these enviroment variables to match yours.

```sh
- name: AMQP_HOST
  value: "RabbitMQ-ClusterIP"
- name: AMQP_PORT
  value: "RabbitMQ-Port"
- name: DB_HOST
  value: "MongoDB-ClusterIP"
- name: DB_PORT
  value: "MongoDB-Port"
```

Finally, starting the service is made by :

```sh
kubectl apply -f kubernetes/server.yaml
```

## Contributors

* Jonathan Brilhante - <jonathan.brilhante@lavid.ufpb.br>
* Wesnydy Ribeiro - <wesnydy@lavid.ufpb.br>

## License

This project is licensed under the LGPLv3 License - see the [LICENSE](LICENSE) file for details.




