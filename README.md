# Hiryu
Visualize tool for mainly threat analysis.

## Quick Start
1.  Install and Start Neo4j

  Please read "Installing Neo4j" on neo4j.com.

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
        
        # Please edit myproject/settings.py
        # 1. Add hiryu to INSTALLED_APPS
        # 2. Edit DATABASES (postgresql is recommended)
        # 3. Add line => NEO4J_AUTH="<neo4j user>:<neo4j password>" 
        
        # Install Hiryu
        $ git clone https://github.com/S03D4-164/Hiryu.git hiryu
      
        # Create Django database
        $ python manage.py makemigrations hiryu
        $ python manage.py migrate
      
4.  Start Django and Celery

        $ celery -A hiryu worker -l info
        $ python manage.py runserver
