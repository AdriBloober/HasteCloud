# HasteCloud
With the HasteCloud you can upload files to a hastebin server

## Installation

### With Pipenv
``
pipenv install
pipenv run run <Arguments>
``

### With pip
``
pip install -r requirements.txt
python3.8 run.py <Arguments>
``

## Configuration

In the resources/config.py you can configure the API_PATH and the maximal content (SPLITTING)

## How to use?

### Upload

``python3 run.py [Path to the input file] [Your password to encrypt]``

### Download

``python3 run.py [The hastecloud key] [Your password to decrypt] [The output file]``