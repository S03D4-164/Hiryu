from ..models import *
from django.shortcuts import redirect

def ref_view(request, id):
	try:
		n = Node.objects.get(ref=id)
		return redirect("/node/" + str(n.id))
	except:
		pass
	try:
		r = Relation.objects.get(ref=id)
		return redirect("/relation/" + str(r.id))
	except:
		pass
	
	return redirect("/graphdb/")
