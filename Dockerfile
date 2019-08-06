FROM ubuntu:latest
MAINTAINER John McCrae <john@mccr.ae>

# Install apache, PHP, and supplimentary programs. openssh-server, curl, and lynx-cur are for debugging the container.
RUN apt-get update && apt-get -y upgrade && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    apache2 php php-mysql libapache2-mod-php python python-pip

# Enable apache mods.
RUN a2enmod php7.2
COPY src/ /var/www/html/

RUN pip install rdflib

CMD /usr/sbin/apache2ctl -D FOREGROUND
