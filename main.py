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

import urllib
import json

IMAGE_PATH = "http://www.exquisiteclock.org/v1/adm/web/clock/"
JSON_PATH = "http://www.exquisiteclock.org/clock/feed/feed.json"


class MainHandler(webapp.RequestHandler):


    def get(self):
        
        print ""
        
        # Reading Remote
        feed_url = "http://www.exquisiteclock.org/clock/feed/feed.json"
        response = urllib.urlopen(feed_url)
        content = response.read()
        json_output = json.loads(content)

        # Reading Local
        # f = open('feed_sample.json', 'r')
        #         content = f.read()
        #         json_output = json.loads(content)
        #         
        images_list = []
        
        for n in range(0, 10):
            #print "DIGIT", n
            for x in json_output[str(n)]:
                #print x.has_key("URL")
                if x.has_key("N"):
                    full_path = IMAGE_PATH + x.get('URL')
                    images_list.append(full_path)
#        print len(images_list)

        if len(images_list) != 0:

            print "Sending Email"
            # Sendout email
            message = mail.EmailMessage(sender="Exquisite Clock <jhwilbert@gmail.com.com>",
                                        subject="Novos numeros Exquisite Clock")
            message.to = "Joao Wilbert <jhwilbert@gmail..com>"
            message.body = """
            Novo numero no relogio
            """
            message.send()
        else:
            print "No new numbers"

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
