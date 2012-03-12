#!/usr/bin/env python
from google.appengine.ext import db


class ImagesStore(db.Model):
  new           = db.BooleanProperty(default=False)
  digit         = db.IntegerProperty(default=0)
  url           = db.TextProperty(default="None")
  display       = db.BooleanProperty(default=False)