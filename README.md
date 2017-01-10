**STILL UNDER DEVELOPMENT. NOT FOR PRODUCTION USE.**

# Overview

Zenmai is a Bug Tracking System (BTS). Inspired by [Kagemai](https://osdn.net/projects/kagemai/)

# Concept

Simple and Minimum.

# Develop

To start web application:

```sh
# you need python3

# install Flask
pip install Flask
pip install Flask-SQLAlchemy
pip install bcrypt

# create your own config
cp web/zenmai.config.sample.py web/zenmai.config.py
# edit 'web/zenmai.config.py' as you like.

# create database
python dbutil.py create

# start web application in debug mode
FLASK_APP=web/zenmai.py FLASK_DEBUG=1 flask run
```

To run unit test:

```sh
python runtest.py
```
