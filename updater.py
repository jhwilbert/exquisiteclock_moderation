#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.api import backends
from models import ImagesStore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import urllib
import simplejson
import settings

###############################################################################################
# DATA LOADERS
###############################################################################################

def getJSON():
    response = urllib.urlopen(settings.env_vars["JSON_PATH"])
    content = response.read()
    json_output = simplejson.loads(content)
    return json_output
    
class load_all(webapp.RequestHandler):
    def get(self):
        images_store = ImagesStore()      
        for n in range(0, 10):
            print "-----------------GETTING DIGIT---------------", n
            print ""
            print ""
            for x in getJSON()[str(n)]:
                if len(x.get("URL")) != 0: 
                    keyname = x.get("URL")[:-4]
                    print "Inserting",x.get("URL")
                    print ""
                    images_store.get_or_insert(keyname, display=True,new=False,digit= n,url=x.get("URL"))             


class load_new(webapp.RequestHandler):
    def get(self):
        images_store = ImagesStore()     
        for n in range(0, 10):
            #print "DIGIT", n
            for x in getJSON()[str(n)]:
                if x.has_key("N"):
                    keyname = x.get("URL")[:-4]
                    images_store.get_or_insert(keyname, display=False,new=True,digit= n,url=x.get("URL"))


###############################################################################################
# HANDLERS
###############################################################################################                   
                    

def main():             
    application = webapp.WSGIApplication([('/backend/load_all', load_all),
                                        ('/backend/load_new', load_new)],
                                        debug=True)
                
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()