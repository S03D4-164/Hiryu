# Hiryu
Visualization tool for mainly threat analysis

## Introduction
I created this tool to organize APT campaign information and to visualize relations of IOC.

There are already some great tools such as Maltego, MANTIS Framework created by siemense...

Hiryu is less powerful than these tools, however, it can store mostly schemaless node and relation on local DB, and can use Neo4j GraphDB as backend.

## Quick Start
1.  Install and Start Neo4j

  Download Neo4j from neo4j.com and read "Installing Neo4j" carefully.

2.  Install Python Package

  Set up virtualenv and install python packages.
  
      # Create virtualenv and activate
      $ virtualenv venv
      $ cd venv
      $ source bin/activate
      
      # Install packages
      $ pip install django celery[redis] py2neo tldextract lxml stix pythonwhois ipwhois psycopg2
      $ source bin/activate

3.  Create Django Project and Install Hiryu

        # Create Django Project
        $ django-admin startproject myproject
        $ cd myproject
        
        # Install Hiryu
        $ git clone https://github.com/S03D4-164/Hiryu.git hiryu
        
        # Edit myproject/settings.py
        # 1. Add hiryu to INSTALLED_APPS
        # 2. Edit DATABASES (postgresql is recommended)
        # 3. Add line => NEO4J_AUTH="<neo4j user>:<neo4j password>" 
        
        # Edit myproject/urls.py
        # 1. Add import => from hiryu import urls
        # 2. Add urlpatterns => url(r'^', include(urls)),
        
        # Create Django database
        $ python manage.py makemigrations hiryu
        $ python manage.py migrate

4.  Put JavaScript Library into hiryu/static

         $ cd hiryu/static
         # Download following JavaScript Library and put files into above directory.
         # bootstrap
         # Datatables
         # vis.js

5.  Start Django and Celery in project directory

        $ celery -A hiryu.tasks worker -l info -f hiryu.log -D
        $ python manage.py runserver
