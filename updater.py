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

from google.appengine.api import mail
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

def get_json():
    """
    Returns JSON object to be parsed
    """
    response = urllib.urlopen(settings.env_vars["JSON_PATH"])
    content = response.read()
    json_output = simplejson.loads(content)
    return json_output
    
class load_all(webapp.RequestHandler):
    """
    Loads all numbers from Exquisite Clock JSON output
    To be called using backend: http://localhost:9199/backend/load_all
    """    
    def get(self):
        self.response.out.write("<html><body>")
        self.response.out.write("<p>Loading all numbers from Exquisite Clock</p>")
        self.response.out.write("</body></html>")
        
        images_store = ImagesStore()      
        for n in range(0, 10):
            for x in get_json()[str(n)]:
                if len(x.get("URL")) != 0: 
                    keyname = x.get("URL")[:-4]
                    images_store.get_or_insert(keyname, display=True,new=False,digit= n,url=x.get("URL"))             

class load_new(webapp.RequestHandler):
    """
    Loads recent numbers from Exquisite Clock JSON output
    To be called using backend: http://localhost:9199/backend/load_new
    """
    
    def get(self):
        self.response.out.write("<html><body>")
        self.response.out.write("<p>Loading recent numbers from Exquisite Clock</p>")
        self.response.out.write("</body></html>")
        
        new_numbers = 0
        images_store = ImagesStore()     
        for n in range(0, 10):
            for x in get_json()[str(n)]:
                if x.has_key("N"):
                    new_numbers = new_numbers+1
                    keyname = x.get("URL")[:-4]
                    images_store.get_or_insert(keyname, display=False,new=True,digit= n,url=x.get("URL"))
        if new_numbers > 0:
            send_mail()

class send_mail():
    """
    Notifies recipients of new number arrivals. TODO: Implement multiple recipients using dict.
    """
    
    mail.send_mail(sender="ExquisiteClock <jhwilbert@gmail.com>",
                  to="Joao Wilbert <jhwilbert@gmail.com>",
                  subject="Exquisite Clock Moderation",
                  body="""
    New numbers have been uploaded to the clock.

    """)
    
###############################################################################################
# HANDLERS
###############################################################################################                   
                    
def main():             
    application = webapp.WSGIApplication([('/backend/load_all', load_all),
                                          ('/backend/load_new', load_new)
                                          ],
                                          debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()