#!/bin/bash

# EDITABLE VARIABLES ##################
PROJECT_NAME=openreader
SERVER_NAME=openreader.local
#######################################

PWD=`pwd`
APACHE_SITE_DIR=/etc/apache2/sites-available
APACHE_MOD_DIR=/etc/apache2/mods-available
PID_DIR=/var/run/apache2
PROJECT_DIR=`dirname $PWD`

install_required_packages() {
	# Check installed modules
	wsgi_installed=false
	xsendfile_installed=false
	installed_mods=`ls /usr/lib/apache2/modules`
	for mod in $installed_mods; do
		if [ "$mod" == 'mod_wsgi.so' ]; then
			wsgi_installed=true
		elif [ "$mod" == 'mod_xsendfile.so' ]; then
			xsendfile_installed=true
		fi
	done

	# Install mod_wsgi
	if ! $wsgi_installed; then
		apt-get install -y build-essential python-dev apache2-prefork-dev
		tar -C /tmp -zxf mod_wsgi-3.3.tar.gz
		cd /tmp/mod_wsgi-3.3
		./configure && make && make install
		echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > $APACHE_MOD_DIR/wsgi.load
		a2enmod wsgi
		apache2ctl restart
		cd -
	fi

	# Install mod_xsendfile
	if ! $xsendfile_installed; then
		if ! which apxs2; then
			apt-get install -y apache2-prefork-dev
		fi
		tar -C /tmp -zxf mod_xsendfile-0.12.tar.gz
		apxs2 -cia /tmp/mod_xsendfile-0.12/mod_xsendfile.c
		apache2ctl restart
	fi
}

install_django_and_required_modules() {
	# Install Django
	if ! which django-admin.py; then
		pip install django
	fi
	pip install django-registration
	pip install django-private-files
}

deploy_configuration_files() {
	sed "s|PROJECT_DIR|$PROJECT_DIR|g; s|PROJECT_NAME|$PROJECT_NAME|g; s|SERVER_NAME|$SERVER_NAME|g; s|PID_DIR|$PID_DIR|g" <apache_vhost.template >$APACHE_SITE_DIR/$PROJECT_NAME
	sed "s|PROJECT_NAME|$PROJECT_NAME|g; s|PROJECT_DIR|$PROJECT_DIR|g" <django.wsgi.template >$PID_DIR/django.wsgi
	if [ ! -d ../logs ]; then
		mkdir ../logs
		chown www-data:www-data ../logs
	fi
	a2ensite $PROJECT_NAME
	apache2ctl restart
}

build_django_environment() {
	python ../manage.py syncdb
	python ../manage.py collectstatic --noinput
}

install_required_packages
install_django_and_required_modules
deploy_configuration_files
build_django_environment
