# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.10-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    FUNCTIONS_WORKER_RUNTIME=python \
    FUNCTIONS_EXTENSION_VERSION=4

RUN sed -i 's/jessie/stretch/gi' /etc/apt/sources.list.d/*
RUN sed -i 's/jessie/stretch/gi' /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y libeigen3-dev \
	libgmp-dev \
	libgmpxx4ldbl \
	libmpfr-dev \
	libboost-dev \
	libboost-thread-dev \
	libtbb-dev

COPY . /home/site/wwwroot
RUN pip install -r /home/site/wwwroot/requirements.txt