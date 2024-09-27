import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import csv
import os
from helpers import configure_webdriver, is_remote
from extractCityState import find_city_state_in_title

def next_page(driver):
        try:
            next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//a[@class='paginationItemLast'])[2]"))) 
            next_page.click()
            if next_page!=None:
                return driver,True
        except:
            return driver,False

def getting_links(driver):
    list_jobs = []
    i = 0
    while(True):
        try:
            i+=1
            TData = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"(//tbody//tr[@class='data-row'])[{i}]//td[1]//span//a")))
            links = TData.get_attribute("href")
            list_jobs.append(links)
        except:
            
            driver, flag = next_page(driver)
            if flag == False:
                break
            i=0     
                
    return list_jobs 

def extracting_links(link_list, driver):
    list_jobs = []

    for link in link_list:
        try:
            driver.get(link)
            job_details = getting_values(driver, link)
            if job_details:
                list_jobs.append(job_details)
        except Exception as e:
            pass
    
    return list_jobs

def getting_values(driver, url):
    try:
        
        #finding id
        job_id = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[b[contains(text(), 'Requisition ID')]]"))
        )
        job_id = job_id.get_attribute('innerText')
        job_id = job_id[-5:]
        

        # Find and  job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@id='job-title']"))
        )
        job_title = job_title.text

        # Find and  job location
        job_location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='jobGeoLocation']"))
        ).text

        # Find city and state
        try:
            city, state = find_city_state_in_title(job_location)
        except:
            city, state = [part.strip() for part in job_location.split(',')[:2]]
        
        # Find job description
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("span", itemprop="description")
        job_description = desc_content.prettify() if desc_content else None

        from extract_location import extracting_location
        location = extracting_location(city,state)

        jobDetails = {
            "Job Id": job_id,
            "Job Title": job_title,
            "Job Description": job_description,
            "Job Type": '',
            "Categories": "Pharmaceuticals",
            "Location": location,
            "City": city,
            "State": state,
            "Country": "United States",
            "Zip Code": "",
            "Address": job_location,
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
            "Employer Email": "msh@mshteleflex.com",
            "Full Name": "",
            "Company Name": "Teleflex",
            "Employer Website": "https://careers.teleflex.com/",
            "Employer Phone": '866-246-6990',
            "Employer Logo": "",
            "Company Description": "Welcome to Teleflex. To find the products available in your region, select the appropriate country/region and language.",
            "Status": "Active",
        }
        
        return jobDetails
    except Exception as e:
        return None


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

def scraping():
    driver = configure_webdriver(True)
    driver.maximize_window()
    url = "https://careers.teleflex.com/go/SalesSales-Support/7666300/?q=&q2=&alertId=&title=Sales&location=USA"
    driver.get(url)
    links = getting_links(driver)
    list_jobs = extracting_links(links, driver)
    if list_jobs:
        write_to_csv(list_jobs, "data", "TeleFlex.csv")
    else:
        pass

    driver.quit()

scraping()