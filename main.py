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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import mail
from google.appengine.ext.webapp import template

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
    
class LoadAllImages(webapp.RequestHandler):
    def get(self):
        images_store = ImagesStore()      
        for n in range(0, 10):
            #print "DIGIT", n
            for x in getJSON()[str(n)]:
                if len(x.get("URL")) != 0: 
                    keyname = x.get("URL")
                    images_store.get_or_insert(keyname, display=True,new=False,digit= n,url=x.get("URL"))             


class LoadNewImages(webapp.RequestHandler):
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


class ViewNumbers(webapp.RequestHandler):
    def get(self):
        
        images_store = ImagesStore()
        old_numbers = images_store.all().filter('new =', False)
        new_numbers = images_store.all().filter('new =', True)
        
        
        template_values = {
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
        
class add_display(webapp.RequestHandler):
    def post(self):
        img_key = self.request.get("k")
        # curl -d 'k=70038arqiz56IK.jpg' http://localhost:8080/add
        
        #img_key = "60884arqAqKKLk.jpg"
        images_store = ImagesStore()
        images_store = images_store.get_by_key_name(img_key)
        images_store.display = True
        images_store.put()
        self.response.out.write(True)
               
class remove_display(webapp.RequestHandler):
    def post(self):
        img_key = self.request.get("k")
        # curl -d 'k=70038arqiz56IK.jpg' http://localhost:8080/remove

        #img_key = "60884arqAqKKLk.jpg"
        images_store = ImagesStore()
        images_store = images_store.get_by_key_name(img_key)
        images_store.display = False
        images_store.put()
        self.response.out.write(True)

# class generate_json(webapp.RequestHandler):
#     def get(self):
#         #print ""
#         images_store = ImagesStore()
#         display_list = images_store.all().filter("display =", False)
#         
#         display_dict = {}
#         image_list = []
#         
#         
#         for image in display_list:
#             print image.digit
#             print image.url
#             #image_list = [{"URL" :image.url }]
#             display_dict[image.digit] = image_list.append{"URL" :image.url} # empty list
#         
#         # for n in range(0, 10):
#         #     for number in display_list:
#         #         display_dict[n] = image_list # empty list
#         # #for number in display_list:
#         #    #print number.url
#         
#         result = simplejson.dumps(display_dict)
# 
#         self.response.headers['Content-Type'] = 'application/json'
#         self.response.out.write(result)
#                                          
                                     
class MainHandler(webapp.RequestHandler):
    def get(self):
        pass



def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/loadallimages', LoadAllImages),
                                        ('/loadnewimages', LoadNewImages),
                                        ('/admin', ViewNumbers),
                                        ('/add', add_display),
                                        ('/remove', add_display),
                                        ('/output', generate_json),
                                        ],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()