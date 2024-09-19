from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import os
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
import yaml
import time

load_dotenv()

driver_path = os.getenv('DRIVER_PATH')
yaml_file = os.getenv('YAML_FILE')

chrome_options = Options()
service = Service(executable_path=driver_path)


def load_mappings():
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)



def create_driver(**kwargs):
    pref = {}
    if 'javascript_disable' in kwargs:
        pref.update({"profile.managed_default_content_settings.javascript":2})
    elif kwargs.get('image_disable', True):
        pref.update({"profile.managed_default_content_settings.images": 2})
    elif 'headless' in kwargs:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu") 
    return webdriver.Chrome(service=service, options=chrome_options)


def open_webpage(webdriver, url):
    webdriver.get(url)

def find_content_from_profile(mapping, diver, soup, output= {}):
    for key, value in mapping.items():
        if isinstance(value, dict):
            if 'children' in value:
                soup = soup.find(value['component'], class_=value['class'])
                find_content_from_profile(value['children'], driver, soup, output)
            elif 'findfrom' in value:
                pass
            elif 'tag' in value and value['tag']==key:
                if 'class' in value:
                    output[key] = soup.find(value["component"], class_=value["class"]).get_text(strip=True)
                if 'id' in value:
                    output[key] = soup.find(value["component"], class_=value["id"]).get_text(strip=True)
    return output

def find_parent_total_children(driver, parent_path):
    time.sleep(1)
    parent_element  = driver.find_element(By.XPATH, parent_path)
    return driver.execute_script("return arguments[0].children.length;", parent_element)


def get_x_path_of_node(value_from, parent_path, auto_index_number=None, xpath=''):
    if isinstance(value_from, dict) and value_from.get("type") == "child":
        child_tag = value_from.get('tag')
        child_class = value_from.get("class", False)
        child_id = value_from.get("id", False)
        index = value_from.get('index', False)
        if child_class:
            xpath += f"//{child_tag}[contains(@class, '{child_class}')]"
        elif child_id:
            xpath += f"//{child_tag}[contains(@id,'{child_id}')]"
        else:
            xpath += f"//{child_tag}"
        if index:
            xpath+= f"[{index}]"
        elif auto_index_number:
            xpath+=f"[{auto_index_number}]"
    return xpath

def recusrive_path(value_from, driver, parent_path, xpath, child_index=None, all_children=False, x_paths=[]):
    # if value_from == "self":
    #     return xpath, value_from["find_value"]

    if isinstance(value_from, dict) and value_from.get("type") == "child":
        if value_from.get("all_children") == "yes":
            total_children = find_parent_total_children(driver, parent_path)
            print(total_children)
            for i in range(1, total_children+1):
                temp_path = get_x_path_of_node(value_from, parent_path, auto_index_number=i)
                print(temp_path)
                if 'value_from' in value_from and isinstance(value_from['value_from'], dict):
                    return recusrive_path(value_from['value_from'], driver, xpath=xpath+temp_path, x_paths=[])
        else:
            temp_path = get_x_path_of_node(value_from, parent_path, auto_index_number=child_index)
            return recusrive_path(value_from['value_from'], driver, value_from, xpath=xpath+temp_path, x_paths=[])
    elif value_from == "self":
        x_paths.append(xpath)
        return  x_paths, parent_path["find_value"]
    
         

def find_x_path(driver, key, mapping):
    parent = mapping.get('parent', {})
    parent_tag = parent.get('tag')
    parent_class = parent.get('class', False)
    parent_id = parent.get('id', False)
    if parent_class:
        parent_path = f"//*[@class='{parent_class}']"
    elif parent_id:
        parent_path = f"//*[@Id='{parent_id}']"
    
    if parent.get("all_children") == "yes":
        total_children = find_parent_total_children(driver, parent_path)
        print(total_children, parent_path)
        xpaths = []
        for i in range(1, total_children+1):
            xpath, find_value = recusrive_path(parent["value_from"], driver, parent_path, "", i)
            xpaths.extend(xpath)
        return parent_path, xpaths, find_value
    else:
        xpaths, find_value = recusrive_path(parent["value_from"], driver, parent_path, "")
    return parent_path, xpaths, find_value
        

def scrap_poet_profile(driver, url, mappings):
    driver.get(url)
    sleep(2)
    output = {}
    for key, value in mappings.items():
        parent_path, xpaths, find_value  = find_x_path(driver, key, value)
        element = driver.find_element(By.XPATH, f"{parent_path}{xpaths[0]}")
        output[key] = element.get_attribute("innerHTML")
    return output


def scrap_ghazals_titles(driver, url, mappings):
    driver.get(url)
    sleep(5)
    output = {}
    for key, value in mappings.items():
        parent_path, xpaths, find_value = find_x_path(driver, key, value)
        
        if len(find_value) > 1:
            i = 1
            for path in xpaths:
                output[i] = []
                element = driver.find_element(By.XPATH, f"{parent_path}{path}")
                
                for val in find_value:
                    output[i].append(
                        {val:element.get_attribute(val)}
                    )
                i+=1
    return output

def scrap_ghazals(driver, url, mappings):
    driver.get(url)
    sleep(3)
    output = {}
    pMC_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "pMC"))
    )
    ghazals = ""
    #pMC_element = driver.find_element(By.CLASS_NAME, "pMC")
    #print(pMC_elements.get_attribute("innerHTML"))
    
    for pMC_index, pMC_element in enumerate(pMC_elements):
        w_elements = pMC_element.find_elements(By.CLASS_NAME, "w")
        for w_index, w_element in enumerate(w_elements):
            c_element = w_element.find_element(By.CLASS_NAME, "c")
            p_elements = c_element.find_elements(By.TAG_NAME, "p")
            for p_index, p_element in enumerate(p_elements):
                soup = BeautifulSoup(p_element.get_attribute("innerHTML"), 'html.parser')
                ghazals+=soup.get_text(strip=False)+'\n'
            ghazals+='\n\n'
        
    print(ghazals)
    return ghazals
    
    driver.quit()


    
        

    

    
