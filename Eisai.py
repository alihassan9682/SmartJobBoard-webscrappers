import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import re
import os
from helpers import configure_webdriver, is_remote
from time import sleep
from datetime import datetime, timedelta
# from extractCityState import find_city_state_in_title
from helpers import configure_webdriver, is_remote
from time import sleep
from extractCityState import find_city_state_in_title

def getting_links(driver):
    jobs_link =[]
    while True:
        Selecting_USA = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//*[@data-ph-id='ph-page-element-page20-HEhM9A'])[1]")))
        Selecting_USA.click()
        i = 0
        while True:
            i += 1
            try:
                Selecting_USA = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"(//li[@class='jobs-list-item'])[{i}]//a[@ph-tevent='job_click']")))
                links = Selecting_USA.get_attribute("href")
                jobs_link.append(links)
            except:
                break
        try:
            next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='icon icon-arrow-right']"))) 
            next_page.click() 
        except:       
            return jobs_link  

def write_to_csv(data, directory, filename):
    fieldnames = list(data[0].keys())
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for item in data:
            writer.writerow(item)      

def extracting_links(link_list,driver):
    list_jobs = []
    while(True):
        for links in link_list:
            url = f'{links}'
            try:
                driver.get(url)
                time.sleep(2)
                JOBs = getting_values(driver,url)
                if JOBs != None:
                    list_jobs.append(JOBs)
            except Exception as e:
                pass
        return list_jobs        

def filter_job_title(job_title):
    valid_titles = [
        "Account Specialist",
        "Sales Specialist",
        "Business Leader",
    ]
    for valid_title in valid_titles:
        if valid_title.lower() in job_title.lower():
            return True
    return False

def getting_values(driver,url):

    #finding job_title
    accessing_title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//title[@key='default-job-title']")))
    job_title = accessing_title.get_attribute("textContent")
    if filter_job_title(job_title):
        pass
    else:
        return None
    #getting job id
    accessing_id = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'au-target') and contains(@class, 'jobId')]")))
    job_id = accessing_id.text
    job_id = job_id.split()[-1]
    

    #finding job location
    job_location = job_title[job_title.find("(")+1:job_title.find(")")]
    

    #finding city and state
    try:
        accessing_title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//title[@key='default-job-title']")))
        job_title = accessing_title.get_attribute("textContent")
        city, state = find_city_state_in_title(job_title)
    except:
        place = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//button[@class='see-multiple-loc-btn ph-a11y-multi-location au-target'])[1]")))
        place.click()
        place = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//span[@data-ph-id='ph-page-element-page7-POw0M6'])[2]")))
        place = place.text
        city, state = place.split(', ')
    

    #finding job discription
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    desc_content = soup.find("div", class_="jd-info au-target")
    job_discription = desc_content.prettify() if desc_content else None
    

    #location
    from extract_location import extracting_location
    location = extracting_location(city,state)

    jobDetails = {
                "Job Id": job_id,
                "Job Title": job_title,
                "Job Description": job_discription,
                "Job Type": '',
                "Categories": "Pharmaceuticals",
                "Location": job_location,
                "City": city,
                "State": state,
                "Country": "United States",
                "Zip Code": "",
                "Address": location,
                "Remote": is_remote(job_location),
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": url,
                "Apply Email": "",
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@msheisai.com",
                "Full Name": "",
                "Company Name": "Eisai",
                "Employer Website": "https://www.eisai.com/",
                "Employer Phone": ['New Jersey = 1-201-692-1100',
                                   'Canada = 1-905-361-7130',
                                   'Brazil = 55-11-5555-3865' ],
                "Employer Logo": "",
                "Company Description": "A Leading Global Research and Development-Based Pharmaceutical Company Headquartered in Japan Established in 1941, Eisai is a pharmaceutical company operating globally in terms of R&D, manufacturing  and marketing, with a strong focus on prescription medicines. ",
                "Status": "Active",
            }
    
   

    return jobDetails

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://careers.eisai.com/us/en/search-results?category=Sales"
        try:
            driver.get(url)
            links = []
            
            links = getting_links(driver)
            
            list_jobs = extracting_links(links,driver)
            if(list_jobs) == None:
                return
            
            write_to_csv(list_jobs, "data", "eisai.csv")
        except Exception as e:
            pass
    except Exception as e:
        pass
scraping()