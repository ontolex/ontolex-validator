FROM php:8.5-apache
LABEL maintainer="John McCrae <john@mccr.ae>"

# Official PHP image tracks upstream PHP releases (including security fixes),
# so rebuild with --pull to pick up the latest 8.5.x.
RUN apt-get update && apt-get -y upgrade && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    python3 python3-rdflib && rm -rf /var/lib/apt/lists/*

COPY src/ /var/www/html/
