<div align="center">
  <a href="https://www.vlibras.gov.br/">
    <img
      alt="VLibras"
      src="https://vlibras.gov.br/assets/imgs/IcaroGrande.png"
    />
  </a>
</div>

# VLibras Translator (Video Core)

VLibras Video Generation Service Core.

![Version](https://img.shields.io/badge/version-v2.3.1-blue.svg)
![License](https://img.shields.io/badge/license-LGPLv3-blue.svg)
![VLibras](https://img.shields.io/badge/vlibras%20suite-2019-green.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAUCAYAAAC9BQwsAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH4wIHCiw3NwjjIgAAAQ9JREFUOMuNkjErhWEYhq/nOBmkDNLJaFGyyyYsZzIZKJwfcH6AhcFqtCvFDzD5CQaTFINSlJJBZHI6J5flU5/P937fube357m63+d+nqBEagNYA9pAExgABxHxktU3882hjqtd9d7/+lCPsvpDZNA+MAXsABNU6xHYQ912ON2qC2qQ/X+J4XQXEVe/jwawCzwNAZp/NCLiDVgHejXgKIkVdGpm/FKXU/BJDfytbpWBLfWzAjxVx1Kuxwno5k84Jex0IpyzdN46qfYSjq18bzMHzQHXudifgQtgBuhHxGvKbaPg0Klaan7GdqE2W39LOq8OCo6X6kgdeJ4IZKUKWq1Y+GHVjF3gveTIe8BiCvwBEZmRAXuH6mYAAAAASUVORK5CYII=)

## Table of Contents

- **[Getting Started](#getting-started)**
  - [System Requirements](#system-requirements)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- **[Deployment](#deployment)**
  - [Deployment Tools](#deployment-tools)
  - [Deploying](#deploying)
- **[Contributors](#contributors)**
- **[License](#license)**


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### System Requirements

* OS: Ubuntu 18.04.3 LTS (Bionic Beaver)

### Prerequisites

Before starting the installation, you need to install some prerequisites:


##### [MongoDB](https://www.mongodb.com/)

Update local package database.

```sh
sudo apt update
```

Install required libraries.

```sh
sudo apt install -y wget gnupg
```

Import the public key used by the package management system.

```sh
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
```

Create a list file for MongoDB.

```sh
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
```

Reload local package database.

```sh
sudo apt update
```

Install the MongoDB packages.

```sh
sudo apt install -y mongodb-org
```


##### [RabbitMQ](https://www.rabbitmq.com/)

Update package indices.

```sh
sudo apt update
```

Install prerequisites.

```sh
sudo apt install -y curl gnupg apt-transport-https
```

Install RabbitMQ signing key.

```sh
curl -fsSL https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc | sudo apt-key add -
```

Add Bintray repositories that provision latest RabbitMQ and Erlang 21.x releases.

```sh
echo "deb https://dl.bintray.com/rabbitmq-erlang/debian bionic erlang-21.x" | tee /etc/apt/sources.list.d/bintray.rabbitmq.list
```

```sh
echo "deb https://dl.bintray.com/rabbitmq/debian bionic main" | tee -a /etc/apt/sources.list.d/bintray.rabbitmq.list
```

Update package indices.

```sh
sudo apt update
```

Install rabbitmq-server and its dependencies.

```sh
sudo apt install rabbitmq-server -y --fix-missing
```

##### [VLibras Player](http://www.vlibras.gov.br)

The player executable is already versioned with the project, extract it in your own folder.

```sh
tar -xvf src/player/vlibras-video-player.tar.xz -C src/player/
```

### Installing

After installing all the prerequisites, install the project by running the command:

```sh
sudo make install
```

To test the installation, simply start the Video Generation Core with the following command:

```sh
make dev start
```

## Deployment

These instructions will get you a copy of the project up and running on a live System.

### Deployment Tools

To fully deployment of this project its necessary to have installed and configured the Docker Engine and Docker Compose.

##### [Docker](https://www.docker.com/)

Download get-docker script.

```sh
curl -fsSL https://get.docker.com -o get-docker.sh
```

Install the latest version of Docker.

```sh
sudo sh get-docker.sh
```

##### [Docker Compose](https://docs.docker.com/compose/)

Download the current stable release of Docker Compose.

```sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

Apply executable permissions to the binary.

```sh
sudo chmod +x /usr/local/bin/docker-compose
```

### Deploying

Before deploying the project, check the [docker-compose.yml](docker-compose.yml) file and review the following environment variables:

```yml
DB_HOST: mongo
DB_PORT: 27017
DB_NAME: "vlibras-db"
AMQP_HOST: rabbitmq
AMQP_PORT: 5672
AMQP_USER: vlibras
AMQP_PASS: vlibras
AMQP_PREFETCH_COUNT: 1
VIDEOMAKER_QUEUE: "translate.to_video"
VIDEOMAKER_TMP_DIR: /tmp/vlibras-files
VIDEOMAKER_BUNDLES_DIR: /tmp/vlibras-bundles
```

Finally, deploy the project by running:

```sh
sudo docker-compose up
```

## Contributors

* Jonathan Brilhante - <jonathan.brilhante@lavid.ufpb.br>
* Wesnydy Ribeiro - <wesnydy@lavid.ufpb.br>

## License

This project is licensed under the LGPLv3 License - see the [LICENSE](LICENSE) file for details.