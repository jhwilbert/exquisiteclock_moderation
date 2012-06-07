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

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import mail
from google.appengine.ext.webapp import template
from paging import PagedQuery
from models import ImagesStore
import urllib
import simplejson
import os



IMAGE_PATH = "http://www.exquisiteclock.org/v1/adm/web/clock/"
JSON_PATH = "http://www.exquisiteclock.org/clock/feed/feed.json"
CURRENT_DOMAIN ="http://localhost:8080"



###############################################################################################
# DATA LOADERS
###############################################################################################
def getJSON():
    # Reading Local
    f = open('feed_sample.json', 'r')
    content = f.read()
    json_output = simplejson.loads(content)
    return json_output

    # Reading Remote
    # feed_url = "http://www.exquisiteclock.org/clock/feed/feed.json"
    # response = urllib.urlopen(feed_url)
    # content = response.read()
    # json_output = simplejson.loads(content)
    # return json_output
    


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
# VIEWS
###############################################################################################

PAGESIZE = 50

class ViewNumbers(webapp.RequestHandler):
    
    def get(self):
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
            'base_url' : IMAGE_PATH,
            'current_domain' : CURRENT_DOMAIN,
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
        self.redirect("/admin")
        self.response.out.write(True)
               
class disable(webapp.RequestHandler):
    def get(self,img_key):
        
        images_store = ImagesStore()
        images_store = images_store.get_by_key_name(img_key)
        images_store.display = False
        images_store.put()
        self.redirect("/admin")
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
             
class MainHandler(webapp.RequestHandler):
    def get(self):
        self.redirect("/admin")

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/load_all', load_all),
                                        ('/load_new', load_new),
                                        ('/admin', ViewNumbers),
                                        ('/enable/([^/]+)', enable),
                                        ('/disable/([^/]+)', disable),
                                        ('/json', generate_json),
                                        
                                        ],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()