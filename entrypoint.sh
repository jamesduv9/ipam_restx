#!/bin/sh

if [ "$TEST_ENV" != "true" ]; then
    exec python3 app.py
fi