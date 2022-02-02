#!/bin/sh
sam build && sam local start-api --docker-network=lambda-local
