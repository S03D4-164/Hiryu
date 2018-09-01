from py2neo import watch, Graph, authenticate
from django.conf import settings

def graph_init():
    watch("httpstream")
    watch("py2neo.cypher")
    watch("py2neo.batch")
    if hasattr(settings, "NEO4J_AUTH"):
        host = settings.NEO4J_AUTH["HOST"]
        port = settings.NEO4J_AUTH["PORT"]
        user = settings.NEO4J_AUTH["USER"]
        password = settings.NEO4J_AUTH["PASS"]
        authenticate("{}:{}".format(host,port), user, password)
    graph = Graph()
    return graph

        

