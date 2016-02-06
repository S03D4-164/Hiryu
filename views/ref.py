from ..models import *
from django.shortcuts import redirect

from django.contrib import messages

def ref_view(request, model, id):
    if model == "node":
        try:
            n = Node.objects.get(ref=id)
            return redirect("/node/" + str(n.id))
        except Exception as e:
            messages.add_message(request, messages.WARNING, str(type(e)) + ": "+ str(e))
    elif model == "relation":
        try:
	    r = Relation.objects.get(ref=id)
	    return redirect("/relation/" + str(r.id))
        except Exception as e:
            messages.add_message(request, messages.WARNING, str(type(e)) + ": "+ str(e))
	
    return redirect("/graphdb/")
