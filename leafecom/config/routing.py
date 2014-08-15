"""
The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config["pylons.paths"]["controllers"],
                 always_scan=config["debug"])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect("/error/{action}", controller="error")
    map.connect("/error/{action}/{id}", controller="error")

    # CUSTOM ROUTES HERE
    map.connect("/oregon", controller="oregon", action="index")
    
    map.subdomains = True

    map.connect("/{action}", controller="lisaf", conditions={"sub_domain": ["lisaforrello", "lisaforello", "lisaf"]})
    map.connect("/{action}/", controller="lisaf", conditions={"sub_domain": ["lisaforrello", "lisaforello", "lisaf"]})

    map.connect("/reportAbuse/*url", controller="archives", action="reportAbuse")
    map.connect("/ip/*format", controller="ip", action="index")
    map.connect("/download/*url", controller="download", action="GET")
    map.connect("/dls/upload_file", controller="dls", action="upload_file")
    map.connect("/dls/upload", controller="dls", action="upload")
    map.connect("/dls/upload/", controller="dls", action="upload")
    map.connect("/medical/data_entry", controller="medical", action="data_entry")
    map.connect("/medical/data_entry/", controller="medical", action="data_entry")
    map.connect("/email/search", controller="addalias", action="search")
    map.connect("/email/search/*term", controller="addalias", action="search")
    map.connect("/{controller}/{id}", action="index")
    map.connect("/{controller}/{action}", action="index")
    map.connect("/{controller}/{action}/", action="index")

    # For the vault controller
    map.connect("/vault/{key}/{id}", controller="vault", action="index")

    map.connect("/{controller}/{action}/{id}")
    map.connect("/{controller}/{action}/{id}/")
    map.connect("/{controller}/{action}/{listname}/{id}")
    map.connect("/{controller}", action="index")
    map.connect("/{controller}/", action="index")
    map.connect("/", controller="index", action="index")
#
#
#
#    print "LEN", len(map.matchlist)
#    for xx in map.matchlist:
##         print "collection_name", xx.collection_name
#        print "conditions", xx.conditions
#        print "defaults", xx.defaults
##         print "filter", xx.filter
##         print "maxkeys", xx.maxkeys
##         print "member_name", xx.member_name
##         print "parent_resource", xx.parent_resource
##         print "regpath", xx.regpath
##         print "req_regs", xx.req_regs
##         print "reqs", xx.reqs
#        print "routelist", xx.routelist
#        print "routepath", xx.routepath
##         print "static", xx.static
#        print "sub_domains", xx.sub_domains
#        print "-"*44
#        print
## 
#


    return map
