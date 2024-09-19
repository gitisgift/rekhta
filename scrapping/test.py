from selenium.webdriver.common.by import By
from driver import (create_driver, open_webpage, scrap_poet_profile, load_mappings,
		 scrap_ghazals_titles, scrap_ghazals)
import os
import json
from time import sleep
from models import Poet, Sher, Ghazal


poets = json.loads(os.getenv('poets'))
url = os.getenv('URL')
scroll_amount = 200

mappings = load_mappings()

all_poets = poets['poets']

def create_file(folder_path, file_name):
	with open(folder_path+file_name, 'w') as fp:
		pass
	fp.close()

def write_to_file(file_path, dict_data):
	with open(file_path, 'w') as f:
		f.write(json.dumps(dict_data))

def read_file(file_path):
	with open(file_path, 'r') as f:
		output = f.read()
	f.close()
	return output

for poet in all_poets:
	if not os.path.isdir(poet):
		os.makedirs(poet)
	driver = create_driver(image_disable=True, headless=True)
 	# scrap profile
	# create_file(poet, "/profile.json")
	# output = scrap_poet_profile(driver, url+poet+"/profile", mappings["mappings"]["profile"])
	# write_to_file(f"{poet}/profile.json", output)

	# scrap  ghazals titles
	# all_ghazals_title = scrap_ghazals_titles(driver, url+poet+"/ghazals", mappings["mappings"]["ghazals_titles"])
	# create_file(poet, "/all_ghazals.json")
	# write_to_file(f"{poet}/all_ghazals.json", all_ghazals_title)

	#scrap ghazals


	ghazal = scrap_ghazals(driver, "https://www.rekhta.org/ghazals/na-sochnaa-ki-zamaane-se-dar-gae-ham-bhii-a-g-josh-ghazals", mappings["mappings"]["ghazals"])
	create_file(poet, "/na-sochnaa-ki-zamaane-se-dar-gae-ham-bhii-a-g-josh-ghazals.text")
	write_to_file(f"{poet}/na-sochnaa-ki-zamaane-se-dar-gae-ham-bhii-a-g-josh-ghazals.text", ghazal)
	driver.quit()

