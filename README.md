# Preparations

## Install the libgl1 before installing requirements.txt in EC2
- sudo apt-get update
- sudo apt-get install -y libgl1

## Install gevent in the venv-camhosting environment
- pip install gevent gevent-websocket

## Run
- authbind python -u camserver.py
