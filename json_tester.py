######################################################################################################
# Sistema de Update Exquisite Clock
######################################################################################################

import os 
import urllib, json




######################################################################################################
# Variaveis

# Caminho para armazenamento de imagens e JSON na maquina local
IMAGES_PATH_LOCAL = "/Users/joaowilbert/Sites/exquisiteclock/build/images/"
JSON_PATH_LOCAL = "/Users/joaowilbert/Sites/exquisiteclock/build/"

# Caminho do relogio (nao alterar)
IMAGES_PATH_REMOTE = "http://www.exquisiteclock.org/v1/adm/installation/clock/"
JSON_PATH_REMOTE = "http://www.exquisiteclock.org/clock/feed/feed.json"
JSON_PATH_REMOTE_API = "http://exquisiteclockapi.appspot.com/json"

######################################################################################################
# Classe Implementada usando WGET (http://www.gnu.org/software/wget/)

class wget_updater:
	def __init__(self):
		pass

	def update_images(self):
		
		# Download Images Using WGET
		os.system("wget -m -nd -A.jpg -N -P %s %s" % (IMAGES_PATH_LOCAL,IMAGES_PATH_REMOTE))
	
	def update_json(self):
		os.system("wget -m -nd -N -P %s %s" % (JSON_PATH_LOCAL,JSON_PATH_REMOTE))	


######################################################################################################
# Classe Implementada usando Python

class python_updater:
	def __init__(self):
		pass
	def update_images(self):

		response = urllib.urlopen(JSON_PATH_REMOTE_API)
		content = response.read()

		data = json.loads(content)
		
		os.chdir(IMAGES_PATH_LOCAL)

		for n in range(0, 10):

			print "Downloading %s ----------------------------------------------------------" % n 
			for x in data[str(n)]:
			
				remote_file = IMAGES_PATH_REMOTE + x["URL"]

				if os.path.isfile(x["URL"]):
					print "Skipping %s" % remote_file
					pass
				else:
				
					urllib.urlretrieve(remote_file,x["URL"])
					print "Downloading %s" % remote_file
		response.close()

	def update_json(self):

		#JSON_LOCAL_FILE = "/Users/joaowilbert/Sites/exquisiteclock/feed.json"
		#urllib.urlretrieve(JSON_PATH_REMOTE,JSON_LOCAL_FILE)
		response = urllib.urlopen(JSON_PATH_REMOTE_API)
		content = response.read()

		data = json.loads(content)
		
		print data


######################################################################################################
# Instancias
# Comentar para ativar o tipo de update


# Usando Python Updater
clock = python_updater()
clock.update_json()

# Usar WGET Updater
# clock = wget_updater()
# if clock.update_images():
# 	clock.update_json()


