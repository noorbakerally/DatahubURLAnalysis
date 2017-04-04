import json
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

with open("cleanlinks.json") as inputFile:
	links = json.load(inputFile)

g = Graph()
ON = Namespace("http://example.com/ontology/")
DA = Namespace("http://example.com/data/")
g.bind("on",ON)
g.bind("da",DA)
test = ["http://readinglists.ucl.ac.uk/lists/CC195814-83A4-386F-509A-37E2F35A204B?param1=valu&param2=value#Fragment"]
#for link in links["links"]:
for link in test:
	print link
	linkIRI = URIRef(link)

	#adding the scheme	
	scheme = link[:link.index(":")]
	g.add( (linkIRI, ON.scheme, Literal(scheme)) ) 	

	#getting the host
	link = link.replace(scheme+"://","")
	host = link[:link.index("/")]
	g.add( (linkIRI, ON.host, Literal(host)) ) 	

	#adding the host parts
	hostParts = host.split(".")
	numHostPart = 0
	for hostPart in hostParts:
		numHostPart = numHostPart + 1
		g.add( (linkIRI, ON.hostPart, Literal(hostPart)) ) 	
	g.add( (linkIRI, ON.nbHostPart, Literal(numHostPart)) ) 	


	link = link.replace(host,"")

	#adding the path
	path = link[:link.rfind("/")+1]
	pathNode = BNode()
	g.add( (linkIRI, ON.path, pathNode) ) 	
	g.add( (pathNode, ON.name, Literal(path)) ) 	
	g.add( (pathNode, RDF.type, ON.Path) ) 	
	pathParts = path.split("/")
	pathPartPosition = 0
	for pathPart in pathParts:
		if pathPart == "":
			continue
		pathPartPosition = pathPartPosition + 1
		pathPartNode = BNode()
		g.add( (pathNode, ON.pathPart, pathPartNode) ) 	
		g.add( (pathPartNode, ON.name, Literal(pathPart)) ) 	
		g.add( (pathPartNode, ON.position, Literal(pathPartPosition)) ) 	
	
	link = link.replace(path,"")

	#get the fragment part
	if "#" in link:
		fragment = link[link.index("#")+1:]
		fragmentNode = BNode()
		g.add( (linkIRI, ON.fragment, fragmentNode) ) 	
		g.add( (fragmentNode, RDF.type, ON.Fragment) ) 	
		g.add( (fragmentNode, ON.fragmentStr, Literal(fragment)) ) 	
		link = link[:link.index("#")]

	#add the query parameter
	if "?" in link:
		queryParamStr = link[link.index("?")+1:]
		queryParamDNode = BNode()
		g.add( (linkIRI, ON.qpdesc, queryParamDNode) ) 	
		g.add( (queryParamDNode, RDF.type, ON.QPDesc) ) 	
		queryParams = queryParamStr.split("&")
		for queryParam in queryParams:
			queryParamPart = queryParam.split("=")
			qpKey = queryParamPart[0]
			qpValue = queryParamPart[1]
			queryParamNode = BNode()
			g.add( (queryParamDNode, ON.queryParam, queryParamNode) ) 	
			g.add( (queryParamNode, ON.queryParamKey, Literal(qpKey)) ) 	
			g.add( (queryParamNode, ON.queryParamValue, Literal(qpValue)) ) 	
			g.add( (queryParamNode, RDF.type, ON.QueryParam) ) 	
		link = link[:link.index("?")]


	#adds the resource
	resource = link
	if "." in resource:
		#case file
		fileParts = resource.split(".")
		name = fileParts[0]
		ext = fileParts[1]
		fileNode = BNode()
		g.add( (linkIRI, ON.resource, fileNode) )
		g.add( (fileNode, RDF.type, ON.FileResource) )
		g.add( (fileNode, ON.name, Literal(name)) )
		g.add( (fileNode, ON.fullName, Literal(resource)) )
		g.add( (fileNode, ON.ext, Literal(ext)) )
	else:
		#normal resource		
		resNode = BNode()
		g.add( (linkIRI, ON.resource, resNode) )
                g.add( (resNode, RDF.type, ON.Resource) )
                g.add( (resNode, ON.fullName, Literal(resource)) )


	
	print link	
	print	


	break

print g.serialize(format='turtle')
