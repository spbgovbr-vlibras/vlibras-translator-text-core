# STT Worker

![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)
![Python-Version](https://img.shields.io/badge/Python-3.10-green)

Repository for the VLibras translation worker

## Table of Contents
- **[Development](#development)**
- **[Deployment](#deployment)**
- **[Author](#author)**


## Development

To run the worker locally, the steps are as follows:
- Install a modern version of Python (personally, I have developed and tested the server on 3.10);
- Optionally, create and activate a virtualenv:
  ```bash
  $ virtualenv venv && source venv/bin/activate

  # or, if you don't want to install `virtualenv`:
  $ python3 -m venv venv && source venv/bin/activate
  ```
- Install the required dependencies:
  ```bash
  $ pip install -r requirements.txt
  ```
- Run the worker in debug mode by calling the main source file:
  ```bash
  $ python stt_service/worker.py
  ```

During development, it is also useful to run code-style and linting tools before commiting and/or creating a merge request:
- Install dev dependencies:
  ```bash
  $ pip install -r requirements-dev.txt
  ```
- Enable linter and formatting before commiting:
  ```bash
  $ pre-commit install
  ```

## Deployment

### Set enviroment variables

- Copy the .env.host example to .env and edit the variables according to host setup
```bash
$ cp .env.example .env
```


### Author

* Diego Silva - <diego.silva@lavid.ufpb.br>