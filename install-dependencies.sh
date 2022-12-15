#!/bin/bash

source /opt/supervisorRC/crawler-icts-zerorisk/venv/bin/activate

pip install -r requirements.txt
python -m playwright install
