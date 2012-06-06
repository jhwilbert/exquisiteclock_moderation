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
            #print "DIGIT", n
            for x in getJSON()[str(n)]:
                if len(x.get("URL")) != 0: 
                    keyname = x.get("URL")
                    images_store.get_or_insert(keyname, display=True,new=False,digit= n,url=x.get("URL"))             


class load_new(webapp.RequestHandler):
    def get(self):
        images_store = ImagesStore()     
        for n in range(0, 10):
            #print "DIGIT", n
            for x in getJSON()[str(n)]:
                if x.has_key("N"):
                    keyname = x.get("URL")
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
        
        if curr_page == '':
            curr_page = 1
        else:
            curr_page = int(curr_page)

        next_page = int(curr_page) + 1
        prev_page = int(curr_page) + 1
                    
        # new numbers  
        new_numbers = images_store.all().filter('new =', True)
        
        # old numbers
        old_numbers_query = images_store.all().filter('new =', False)
        old_numbers_pagedQuery = PagedQuery(old_numbers_query,PAGESIZE)
        old_numbers = old_numbers_pagedQuery.fetch_page(curr_page)
        
        template_values = {
            'curr_page' : curr_page,
            'prev_page' : prev_page,
            'next_page' : next_page,
            'total_pages' : xrange(old_numbers_pagedQuery.page_count()),
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
    def get(self):
        #print ""
        images_store = ImagesStore()
        display_list = images_store.all().filter("display =", True)
        
        index = 0

        display_dict = {}
        image_dict = {}
        image_list = []
        json_list = []
        #print ''
        for i in range(0,10):
            image_list.append(images_store.all().filter("digit =", i).filter("display =", True))
        
            for image in image_list[i]:
                json_list.append({"URL": image.url})
                
            display_dict[i] = json_list
            print i
            print "--------------------"
        print display_dict[i]

            
        # result = simplejson.dumps(display_dict)
        # self.response.headers['Content-Type'] = 'application/json'
        # self.response.out.write(result)
        #print image_list
        

        # print display_list
        # 
        # for image in display_list:
        #     print image.digit
        #     print image.url
        # 
        # for image in display_list:
        #     print image.digit
        #     print image.url
        #     #image_list = [{"URL" :image.url }]
        #     display_dict[image.digit] = image_list.append{"URL" :image.url} # empty list
        
        # # for n in range(0, 10):
        # #     for number in display_list:
        # #         display_dict[n] = image_list # empty list
        # # #for number in display_list:
        # #    #print number.url
        # 
        # result = simplejson.dumps(display_dict)
        # 
        # self.response.headers['Content-Type'] = 'application/json'
        # self.response.out.write(result)
                                         

                                     
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