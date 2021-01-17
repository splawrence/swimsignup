#!/bin/bash
cd /home/ubuntu/apps/swimsignup/
uwsgi --socket 0.0.0.0:8000 --protocol=http -w app:app