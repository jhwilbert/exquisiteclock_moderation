import os

dev_env = os.environ['SERVER_SOFTWARE'].startswith('Dev')

env_vars = {
    "BASE_URL" : "http://localhost:8080" if dev_env else "http://exquisiteclockapi.appspot.com",
    "JSON_PATH" : "http://www.exquisiteclock.org/clock/feed/feed.json",  # use remote JSON as localhost timeouts
    "IMAGE_PATH" : "http://www.exquisiteclock.org/v1/adm/web/clock/",
    "LARGE_IMAGE_PATH" : "http://www.exquisiteclock.org/v1/adm/installation/clock/"
}
