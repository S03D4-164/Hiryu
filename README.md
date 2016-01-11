# Hiryu
Visualization tool for threat analysis

## Introduction
I created this tool to organize APT campaign information and to visualize relations of IOC.

There are already some great tools such as Maltego, MANTIS Framework created by siemense...
Hiryu is less powerful than these tools, however, it can store mostly schemaless node and relation on local DB, and can use Neo4j GraphDB as backend.

## Quick Start
0.  Install and Start Neo4j (Optional)

  Download Neo4j from neo4j.com and read "Installing Neo4j" carefully.

1.  Install Python Package

  Set up virtualenv and install python packages.
  
      """Create virtualenv and activate"""
      $ virtualenv venv
      $ cd venv
      $ source bin/activate
      
      """Install packages"""
      $ pip install django celery[redis] py2neo tldextract lxml stix pythonwhois ipwhois psycopg2
      $ source bin/activate

2.  Create Django Project and Install Hiryu

        """Create Django Project"""
        $ django-admin startproject myproject
        $ cd myproject
        
        # Install Hiryu
        $ git clone https://github.com/S03D4-164/Hiryu.git Hiryu
        
        Edit myproject/settings.py
        1. Add 'Hiryu' to INSTALLED_APPS
        2. Edit DATABASES (postgresql is recommended)
        3. Change ROOT_URLCONF => 'Hiryu.urls'
        4. Add line => NEO4J_AUTH="<neo4j user>:<neo4j password>" 
           (or export above NEO4J_AUTH as env)
        
        """Create Django database"""
        $ python manage.py makemigrations Hiryu
        $ python manage.py migrate

3.  Start Django and Celery in project directory

        $ celery worker -A Hiryu -l info -f hiryu.log -D
        $ python manage.py runserver
