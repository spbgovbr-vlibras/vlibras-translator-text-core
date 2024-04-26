<div align="center">
  <a href="http://www.vlibras.gov.br/">
    <img
      alt="VLibras"
      src="https://vlibras.gov.br/assets/imgs/IcaroGrande.png"
    />
  </a>
</div>

# VLibras Translator (Text Core)

VLibras Translation Service Core.

![Version](https://img.shields.io/badge/version-v2.3.0-blue.svg)
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

* OS: Ubuntu 22.04 LTS (Jammy Jellyfish)

### Prerequisites

Before starting the installation, you need to install some prerequisites:

##### [RabbitMQ](https://www.rabbitmq.com/)

Follow the [Quick Start script](https://www.rabbitmq.com/install-debian.html#apt-quick-start-cloudsmith) from RabbitMQ:

```sh
#!/bin/sh

sudo apt-get install curl gnupg apt-transport-https -y

## Team RabbitMQ's main signing key
curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
## Community mirror of Cloudsmith: modern Erlang repository
curl -1sLf https://ppa1.novemberain.com/gpg.E495BB49CC4BBE5B.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
## Community mirror of Cloudsmith: RabbitMQ repository
curl -1sLf https://ppa1.novemberain.com/gpg.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/rabbitmq.9F4587F226208342.gpg > /dev/null

## Add apt repositories maintained by Team RabbitMQ
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
## Provides modern Erlang/OTP releases
##
deb [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu jammy main

## Provides RabbitMQ
##
deb [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu jammy main
EOF

## Update package indices
sudo apt-get update -y

## Install Erlang packages
sudo apt-get install -y erlang-base \
                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                        erlang-runtime-tools erlang-snmp erlang-ssl \
                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

## Install rabbitmq-server and its dependencies
sudo apt-get install rabbitmq-server -y --fix-missing
```

##### Python 3.10

Can be installed using conda.
Download and run the [miniconda installer](https://docs.conda.io/en/latest/miniconda.html#linux-installers):
```sh
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
source ~/miniconda3/bin/activate
conda init
```

Relogin to finish the installation.

Create a new environment with python 3.10:
```sh
conda create -n text-core python=3.10
```

Then, activate the environment:
```sh
conda activate text-core
```


##### [Vlibras Translate](https://gitlab.lavid.ufpb.br/vlibras2019/vlibras-library/vlibras-translate)

```sh
make install
```

```sh
python -m pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-translate==1.3.1 \
&& python -m pip  install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-deeplearning==1.3.1
```



### Installing

After installing all the prerequisites, install the project by running the command:


To test the installation, simply start the Translation Core with the following command:

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
AMQP_HOST: rabbitmq
AMQP_PORT: 5672
AMQP_USER: vlibras
AMQP_PASS: vlibras
AMQP_PREFETCH_COUNT: 1
TRANSLATOR_QUEUE: "translate.to_text"
ENABLE_DL_TRANSLATION: "false"
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
