#!/bin/sh

./bin/migrate

gunicorn --config gunicorn.config.py realty_scoring.app:application
