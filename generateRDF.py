import json
import urllib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

import sys
reload(sys)
sys.setdefaultencoding('utf8')


with open("cleanlinks.json") as inputFile:
	links = json.load(inputFile)

g = Graph()
ON = Namespace("http://example.com/ontology/")
DA = Namespace("http://example.com/data/")
g.bind("on",ON)
g.bind("da",DA)

#test = ["http://agalpha.mathbiol.org/repositories/tcga/statements?subj=%3Chttp%3A%2F%2Fpurl.org%2Ftcga%2Fcore%23c92261c2-84fe-4a15-9dd9-8bb89ca8301d%3E"]
#for link in test:
for link in links["links"]:
	#print link
	linkIRI = URIRef(link)
	g.add( (linkIRI, RDF.type, ON.WebResource) ) 	
	#link = urllib.unquote(link).decode('utf8') 

	#adding the scheme	
	scheme = link[:link.index(":")]
	g.add( (linkIRI, ON.scheme, Literal(scheme)) ) 	

	#getting the host
	link = link.replace(scheme+"://","")
	host = link
	if "/" in link:
		host = link[:link.index("/")]
	hostNode = BNode()
	g.add( (linkIRI, ON.host, hostNode) ) 	
	g.add( (hostNode, RDF.type, ON.Host) ) 	
	g.add( (hostNode, ON.name, Literal(host)) ) 	

	#adding the host parts
	hostParts = host.split(".")
	g.add( (hostNode, ON.nbHostParts, Literal(len(hostParts))) ) 	
	numHostPart = 0
	for hostPart in hostParts:
		hostPartNode = BNode()
		numHostPart = numHostPart + 1
		g.add( (hostPartNode, RDF.type, ON.HostPart) ) 
		g.add( (hostPartNode, ON.name, Literal(hostPart)) ) 	
		g.add( (hostPartNode, ON.position, Literal(numHostPart)) ) 	
		g.add( (hostNode, ON.hostPart, hostPartNode) ) 	


	link = link.replace(host,"")
	
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
                g.add( (queryParamDNode, RDF.type, ON.QPDesc) )
                g.add( (queryParamDNode, ON.nbQueryParams, Literal(len(queryParams))) )
                g.add( (queryParamDNode, ON.nbQueryParamStr, Literal(urllib.unquote(queryParamStr).decode('utf8')) )) 
                for queryParam in queryParams:
                        queryParamPart = queryParam.split("=")
                        qpKey = queryParamPart[0]
                        queryParamNode = BNode()
                        g.add( (queryParamDNode, ON.queryParam, queryParamNode) )
                        g.add( (queryParamNode, ON.queryParamKey, Literal(qpKey)) )
                        if (len(queryParamPart) > 1):
                                qpValue = queryParamPart[1]
				qpValue = urllib.unquote(qpValue).decode('utf8') 
                                g.add( (queryParamNode, ON.queryParamValue, Literal(qpValue)) )
                        g.add( (queryParamNode, RDF.type, ON.QueryParam) )
                link = link[:link.index("?")]


	#adding the path
	path = link[:link.rfind("/")+1]
	pathNode = BNode()
	g.add( (linkIRI, ON.path, pathNode) ) 	
	g.add( (pathNode, ON.name, Literal(path)) ) 	
	g.add( (pathNode, RDF.type, ON.Path) ) 	
	pathParts = path.split("/")
	#print str(path) + ":" + str(pathParts)
	pathPartPosition = 0
	for pathPart in pathParts:
		if pathPart == "":
			continue
		pathPartPosition = pathPartPosition + 1
		pathPartNode = BNode()
		#pathPartNode = ON["PathPart"+str(pathPartPosition)]
		g.add( (pathNode, ON.pathPart, pathPartNode) ) 	
		g.add( (pathPartNode, ON.name, Literal(pathPart)) ) 	
		g.add( (pathPartNode, ON.position, Literal(pathPartPosition)) ) 	
	
	link = link.replace(path,"")
        g.add( (pathNode, ON.nbPathParts, Literal(pathPartPosition) ) )


	#adds the resource
	resource = link
	#check if resource container number after .
	#if yes not a file resource
	if "." in resource:
		#case file
		name = resource[:resource.index(".")]
		ext = resource[resource.index("."):]
		fileNode = BNode()
		g.add( (linkIRI, ON.resource, fileNode) )
		g.add( (fileNode, RDF.type, ON.FileResource) )
		g.add( (fileNode, ON.name, Literal(name)) )
		g.add( (fileNode, ON.localName, Literal(resource)) )
		g.add( (fileNode, ON.ext, Literal(ext)) )
	else:
		#normal resource		
		resNode = BNode()
		g.add( (linkIRI, ON.resource, resNode) )
                g.add( (resNode, RDF.type, ON.Resource) )
                g.add( (resNode, ON.localName, Literal(resource)) )


	#build namespace
	namespace = scheme+"://"+host + path 
	link = str(linkIRI)
	if "#" in link:
		namespace = namespace + resource + queryParamStr
		
	g.add( (linkIRI, ON.namespace, Literal(namespace)) )
	
	#print link	
	#print	



print g.serialize(format='turtle')
