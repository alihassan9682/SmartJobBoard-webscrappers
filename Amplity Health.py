# -*- coding: utf-8 -*-
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

def request_url(driver, url):
    driver.get(url)

def write_to_csv(data, directory, filename):
    fieldnames = list(data[0].keys())
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for item in data:
            writer.writerow(item)

def filter_job_title(job_title):
    valid_titles = [
        "Sales District Manager",
        "Sales Specialist",
        "Sales Account Manager",
        "Sales Representative",
        "Customer Care",
        "Business Manager",
        "Program Director",
    ]
    for valid_title in valid_titles:
        if valid_title.lower() in job_title.lower():
            return True
    return False

def getting_links(driver):
    link_list = []
    while True:
        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//section[@class ='css-8j5iuw']/ul")))
        a_elements = WebDriverWait(container, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        for a in a_elements:
            try:
                href_value = a.get_attribute('href')
                if not href_value in link_list:
                    link_list.append(href_value)
            except Exception as e:
               pass
        try:
            div_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='css-3z7fsk']")))
            button = div_element.find_element(By.XPATH, ".//button[@aria-label='next' and @class='css-1oatwy4']")
            button.click()
            sleep(5)
        except Exception as e:
            return link_list 

def finding_date(finding_date):
    finding_date = finding_date.lower()
    if 'today' in finding_date:
        return datetime.now().date()
    elif 'yesterday' in finding_date:
        return (datetime.now() - timedelta(days=1)).date()
    else:
        first_word = re.sub(r'\D', '', finding_date.split()[0])
        first_word = int(first_word)
        return (datetime.now() - timedelta(days=first_word)).date()


def getting_values(driver,url):
    JOBS = []

    #getting job id
    job_ids = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//dd[@class='css-129m7dg'])[last()]")))
    job_id = job_ids.text

    #finding job_title
    accessing_title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='css-gk87zv']/span")))
    job_title = ' '.join((accessing_title.text).split()[:(accessing_title.text).split().index('page')])
    
    #finding job location
    elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-automation-id="locations"] dl dd')))
    job_location = elements[0].text

    #finding city and state
    try:
        city, state = find_city_state_in_title(job_title)
    except:
         city, state = job_location.split(',')

    #finding job discription
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    desc_content = soup.find("div", class_="css-11p01j8")
    job_discription = desc_content.prettify() if desc_content else None

    #finding_date_of_post
    finding_word = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//dd[@class='css-129m7dg' and contains(text(), 'Posted')]")))
    finding_word = finding_word.text
    x = finding_word.split('Posted', 1)[-1].strip()
    date_posted = finding_date(x)
    
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
                "Posting Date": date_posted,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshamplity.com",
                "Full Name": "",
                "Company Name": "Amplity Health",
                "Employer Website": "https://www.amplity.com/",
                "Employer Phone": "+1 800-672-0676",
                "Employer Logo": "",
                "Company Description": "Partnership. Personified.Amplity Health is a global contract sales and commercial organization partnering with pharma and biotech companies to provide tailored outsourced programs and communications throughout a drug's life cycle. We specialize in scientific stakeholder engagement and go-to-market strategies, emphasizing person-to-person interactions that build trust with physicians, patients, payers, community organizations, and life science executives.We manage, coach, lead and employ stakeholder-facing professionals around the world, many with advanced degrees, to make sure more of our customers patients gain access to, and benefit fromthe best medicines for the right reasons. ",
                "Status": "Active",
            }
    JOBS.append(jobDetails.copy())
    return JOBS

def extracting_links(link_list,driver):
    i =0
    for links in link_list:
        i += 1
        url = f'{links}'
        try:
            driver.get(url)
            time.sleep(2)

            JOBs = getting_values(driver,url)
            if JOBs == False:
                continue
            write_to_csv(JOBs, "data", "Amplity Health.csv")
            JOBs.clear() 
        except Exception as e:
            pass
        
def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://amplity.wd1.myworkdayjobs.com/en-US/AmplityHealth/details/Pharmaceutical-Sales-District-Manager---NorthEast_R4533?jobFamilyGroup=e091782eaa4710016a641c50649a0000&jobFamilyGroup=cbd281dd39b2100114977ed9627f0000"
        try:
            driver.get(url)
            Jobs_links = getting_links(driver)
            extracting_links(Jobs_links,driver)

        except Exception as e:
            pass
    except Exception as e:
        pass
scraping()
