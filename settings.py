import os

dev_env = os.environ['SERVER_SOFTWARE'].startswith('Dev')

env_vars = {
	"BASE_URL" : "http://localhost:8080" if dev_env else "http://exquisiteclockapi.appspot.com",
    "JSON_PATH" : "http://localhost:8080/feed_sample.json" if dev_env else "http://www.exquisiteclock.org/clock/feed/feed.json",
    "IMAGE_PATH" : "http://www.exquisiteclock.org/v1/adm/web/clock/"
    }
