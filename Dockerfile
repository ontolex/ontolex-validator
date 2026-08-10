FROM ubuntu:latest
MAINTAINER John McCrae <john@mccr.ae>

# Install apache, PHP, and supplimentary programs. openssh-server, curl, and lynx-cur are for debugging the container.
RUN apt-get update && apt-get -y upgrade && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    apache2 php php-mysql libapache2-mod-php python3 python3-rdflib

# Enable apache mods. (The installed PHP version tracks whatever ships
# with the base image, so enable whichever php module got installed
# rather than a hardcoded version.)
RUN a2enmod "$(basename "$(ls /etc/apache2/mods-available/php*.load)" .load)"
COPY src/ /var/www/html/

CMD /usr/sbin/apache2ctl -D FOREGROUND
