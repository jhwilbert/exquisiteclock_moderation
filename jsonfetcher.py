import urllib
import simplejson
import settings

def get_json():
    """
    Returns JSON object to be parsed
    """

    response = urllib.urlopen(settings.env_vars["JSON_PATH"])
    content = response.read()
    json_output = simplejson.loads(content)
    return json_output
