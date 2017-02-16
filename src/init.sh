#!/bin/bash
touch var/database/messenger.db
touch var/logs.log
mkdir -p var/messages
mkdir -p var/blacklists
mkdir -p var/tokens

python db_init.py
