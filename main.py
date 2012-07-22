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
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import mail
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

from paging import PagedQuery
from models import ImagesStore
import urllib
import simplejson
import os
import logging
import settings
import base64
import passwd
import jsonfetcher

PAGESIZE = 50

###############################################################################################
# DECORATORS
###############################################################################################

def basicAuth(func):
  def callf(webappRequest, *args, **kwargs):
    auth_header = webappRequest.request.headers.get('Authorization')

    if auth_header == None:
      webappRequest.response.set_status(401, message="Authorization Required")
      webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
    else:
      # Isolate the encoded user/passwd and decode it
      auth_parts = auth_header.split(' ')
      user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
      user_arg = user_pass_parts[0]
      pass_arg = user_pass_parts[1]

      if user_arg != passwd.data["login"] or pass_arg != passwd.data["password"]:
        webappRequest.response.set_status(401, message="Authorization Required")
        webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
        # Rendering a 401 Error page is a good way to go...
      else:
        return func(webappRequest, *args, **kwargs)

  return callf
      
###############################################################################################
# VIEWS
###############################################################################################

class ViewNumbers(webapp.RequestHandler):
    @basicAuth
    
    def get(self):
        #print ""
        #print settings.env_vars["JSON_PATH"]
        
        images_store = ImagesStore()

        # get page
        curr_page = self.request.get('page')
        display_digit = self.request.get('digit')
        
        # page var
        if curr_page == '':
            curr_page = 1
        else:
            curr_page = int(curr_page)

        # handle digit var
        if display_digit == '':
            display_digit = 0
        else:
            display_digit = int(display_digit)

        next_page = int(curr_page) + 1
        prev_page = int(curr_page) + 1
                    
        # new numbers  
        new_numbers = images_store.all().filter('new =', True)
        
        # old numbers
        old_numbers_query = images_store.all().filter('new =', False).filter('digit =',display_digit)
        old_numbers_pagedQuery = PagedQuery(old_numbers_query,PAGESIZE)
        old_numbers = old_numbers_pagedQuery.fetch_page(curr_page)
        
        template_values = {
            'curr_digit' : display_digit,
            'has_nextpage' : old_numbers_pagedQuery.has_page(next_page),
            'curr_page' : curr_page,
            'prev_page' : prev_page,
            'next_page' : next_page,
            'total_pages' : xrange(1,old_numbers_pagedQuery.page_count()+1,1),
            'new_numbers' : new_numbers,
            'base_url' : settings.env_vars["IMAGE_PATH"],
            'preview_url' : settings.env_vars["LARGE_IMAGE_PATH"],
            'current_domain' : settings.env_vars["BASE_URL"],
            'old_numbers' : old_numbers,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        

###############################################################################################
# ACTIONS
###############################################################################################        
        
class enable(webapp.RequestHandler):
    def get(self,img_key):
        
        images_store = ImagesStore()
        images_store = images_store.get_by_key_name(img_key)
        images_store.display = True
        images_store.put()
        self.redirect("/")
        self.response.out.write(True)
               
class disable(webapp.RequestHandler):
    def get(self,img_key):
        
        images_store = ImagesStore()
        images_store = images_store.get_by_key_name(img_key)
        images_store.display = False
        images_store.put()
        self.redirect("/")
        self.response.out.write(True)
        
class generate_json(webapp.RequestHandler):
    def getnumbers(self,query):
        entrylist = []
        for entry in query:
            number = { "URL" : entry.url}
            entrylist.append(number)
        return entrylist
            
    def get(self):
        images_store = ImagesStore()
        all_digits = {}
        for j in range(10):
            all_digits[j] = self.getnumbers(images_store.all().filter("digit =", j).filter("display =", True))
        result = simplejson.dumps(all_digits)
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(result)

###############################################################################################
# CRAWLER 
###############################################################################################

class load_new(webapp.RequestHandler):
    """
    Loads recent numbers from Exquisite Clock JSON output
    To be called using backend: http://localhost:8080/load_new
    """
    
    def get(self):
        self.response.out.write("<html><body>")
        self.response.out.write("<p>Loading recent numbers from Exquisite Clock</p>")
        self.response.out.write("</body></html>")
        
        new_numbers = 0
        
        images_store = ImagesStore() 
        
        response = urllib.urlopen(settings.env_vars["JSON_PATH"])
        content = response.read()
        json_output = simplejson.loads(content)

        # Parse JSON and populate datastore
        for n in range(0, 10):
            for x in json_output[str(n)]:
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
# MAIN
###############################################################################################
  
def main():
    application = webapp.WSGIApplication([('/', ViewNumbers),
                                        ('/enable/([^/]+)', enable),
                                        ('/disable/([^/]+)', disable),
										('/load_new', load_new),
                                        ('/json', generate_json),
                                        
                                        ],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()