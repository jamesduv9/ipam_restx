#Use somewhat recent NGINX image
FROM nginx:1.25.3

#Accept the MASTER_APIKEY passed in as --build-arg
ARG MASTER_APIKEY

#Copy the flask app to the /ipam_restx directory
COPY . /ipam_restx
WORKDIR /ipam_restx

#Install needed packages
RUN apt-get update -y && \
    apt-get install -y \
    python3 \
    openssl \
    curl \
    python3-pip

#Create IPAM_RESTX user and assign permissions
RUN useradd -m IPAM_RESTX

RUN chown -R IPAM_RESTX:IPAM_RESTX /ipam_restx && \
    chmod 755 /ipam_restx/entrypoint.sh

USER IPAM_RESTX

ENV MASTER_APIKEY=$MASTER_APIKEY

#Install python requirements
#Using --break-system-packages , not using a venv as this is a single purpose container
#ref - https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3
RUN pip install -r requirements.txt --break-system-packages

#entrypoint script, checks if this is running as apart of a ci pipeline, or live
ENTRYPOINT ["/bin/sh", "/ipam_restx/entrypoint.sh"]