from py2neo import watch, Graph, authenticate

def graph_init():
    watch("httpstream")
    watch("py2neo.cypher")
    watch("py2neo.batch")
    graph = Graph()
    return graph

