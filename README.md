<div align="center">
  <a href="http://www.vlibras.gov.br/">
    <img
      alt="VLibras"
      src="http://www.vlibras.gov.br/assets/imgs/IcaroGrande.png"
    />
  </a>
</div>

# VLibras Translator (Core)

One Paragraph of project description goes here.

![Version](https://img.shields.io/badge/version-v0.0.0-blue.svg)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![VLibras](https://img.shields.io/badge/vlibras%20suite-2019-green.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAUCAYAAAC9BQwsAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH4wIHCiw3NwjjIgAAAQ9JREFUOMuNkjErhWEYhq/nOBmkDNLJaFGyyyYsZzIZKJwfcH6AhcFqtCvFDzD5CQaTFINSlJJBZHI6J5flU5/P937fube357m63+d+nqBEagNYA9pAExgABxHxktU3882hjqtd9d7/+lCPsvpDZNA+MAXsABNU6xHYQ912ON2qC2qQ/X+J4XQXEVe/jwawCzwNAZp/NCLiDVgHejXgKIkVdGpm/FKXU/BJDfytbpWBLfWzAjxVx1Kuxwno5k84Jex0IpyzdN46qfYSjq18bzMHzQHXudifgQtgBuhHxGvKbaPg0Klaan7GdqE2W39LOq8OCo6X6kgdeJ4IZKUKWq1Y+GHVjF3gveTIe8BiCvwBEZmRAXuH6mYAAAAASUVORK5CYII=)

## Table of Contents

- [Getting Started](#getting-started)
  - [System Requirements](#system-requirements)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- [Running the Tests](#running-the-tests)
- [Deployment](#deployment)
- [Contributors](#contributors)
- [License](#license)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### System Requirements

* OS: -  
* Processor: -  
* Memory: -  
* Graphics: - (remove if it is not a requirement)  
* Storage: -

For some projects, there may be more system requirements, be sure to add them.

### Prerequisites

What things you need to install the software and how to install them.

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running.

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo.

## Running the Tests

Explain how to run the automated tests for this system.

## Deployment

### Prerequisites

To fully deployment this application its necessary to have instaled and configurated the Docker Engine (https://www.docker.com/) and Kubernetes Container Orchestration (https://kubernetes.io/)
Accomplishing this task change to datacenter to another. Acess all links above to fullfil your needs. 

### Instalation


If you already RabbitMQ running on your cluster, skip the next steps.

Once kubectl is installed and set, run the following commands:

```sh
kubectl apply -f kubernetes/rabbitmq.yaml
kubectl expose deployment rabbitmq --type=ClusterIP
```
Following, this line starts up the RabbitMQ pod. You must configure a volume set to be used by it. By default it set to be used in a Google Cloud Plataform (GCP)

Then , open the file server.yaml and edit these enviroment variables to match yours.

```sh
- name: AMQP_HOST
  value: "RabbitMQ-ClusterIP"
```

Finally, starting the service is made by :

```sh
kubectl apply -f kubernetes/server.yaml
kubectl expose deployment translatorapi --port=80 --type=LoadBalancer
```

## Contributors

* Jhon Doe - <johndoe@lavid.ufpb.br>

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.




