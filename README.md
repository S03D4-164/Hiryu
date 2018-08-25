# Hiryu
Visualization tool for threat analysis

## Introduction
I created this tool to organize APT campaign information and to visualize relations of IOC.

There are already some great tools such as Maltego, MANTIS Framework created by siemense...
Hiryu is less powerful than these tools, however, it can store mostly schemaless node and relation on local DB, and can use Neo4j GraphDB as backend.

## Quick Start

0.  Install and Start Neo4j (Optional)

  Download Neo4j from neo4j.com and read "Installing Neo4j" carefully.

1.  Set up virtualenv and install python packages.

        $ mkdir venv
        $ virtualenv venv
        $ cd venv
        $ source bin/activate
        $ pip install django celery[redis] py2neo tldextract lxml pythonwhois ipwhois psycopg2 ioc_writer django_datatables_view cybox==2.1.0.12 stix=1.2.0.0
        $ source bin/activate

2.  Create Django Project and Install Hiryu

        $ django-admin startproject myproject
        $ cd myproject        
        $ git clone https://github.com/S03D4-164/Hiryu.git
        
3.  Edit myproject/settings.py

        1) Add 'Hiryu' to INSTALLED_APPS as follows:        
        INSTALLED_APPS = [
          ...
          'Hiryu',
        ]
        
        2) Edit DATABASES (e.g. postgresql)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',     
                'NAME': '<DB name>',
                'USER': '<DB user>',
                'PASSWORD': '<DB password>',
                'HOST': 'localhost',
                'PORT': '',
            }
        }

        If you'd like to use postgresql as backend, create DB for app.
        $ sudo -u postgres createuser -d -P <DB user>
        $ sudo -u postgres createdb -O <DB user> <DB name>
        
        Next, add following line to /etc/postgresql/xx/main/pg_hba.conf:

        local   <DB name>        <DB user>                              md5
        # the line must be prior to local all setting.
        local   all             all                                     peer
        
        Please confirm you can password login to the DB as the user.
        $ psql -U <DB user> <DB name>

        3) Change ROOT_URLCONF as follows:
        ROOT_URLCONF = 'Hiryu.urls'

        4) Add line NEO4J_AUTH as follows:
        NEO4J_AUTH="<neo4j user>:<neo4j password>" 

        or set environment variable NEO4J_AUTH. 
        $ export NEO4J_AUTH="<neo4j user>:<neo4j password>" 
        
4. Create Django database

        (You can use Hiryu/createdb.sh, but please edit the script to be suitable for your environment.)
        $ python manage.py makemigrations Hiryu
        $ python manage.py migrate
        $ python manage.py loaddata Hiryu/fixtures/*

5.  Start Django and Celery in project directory

        $ DJANGO_SETTINGS_MODULE='myproject.settings' celery worker -A Hiryu -l info -f hiryu.log -D
        $ python manage.py runserver
