import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import os
from extract_location import extracting_location
from extractCityState import filter_job_title, find_city_state_in_title
from helpers import configure_webdriver, is_remote  


def getting_links(driver):
    link_list = []
    while True:
        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'jv-job-list') and contains(@class, 'jv-search-list')]")))
        a_elements = WebDriverWait(container, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        for a in a_elements:
            try:
                href_value = a.get_attribute('href')
                if not href_value in link_list:
                    link_list.append(href_value)
            except:
               pass
        try:
            
            next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='jv-pagination-next']")))
            next_button.click()
        except:
            print(len(link_list))    
            
            return link_list 


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
        
        # #finding id
        # job_id = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, "//span[@class='job-id job-info']"))
        # )
        
        # job_id = job_id.text
        # job_id = job_id.split('\n')[1] 
        
        
        

        # Find and print job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[@class='jv-header']"))
        )
        job_title = job_title.text
        # print(f"The job title is {job_title}")


        # Find and print job location
        try:
            job_location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[@class='jv-job-detail-meta']")))
            job_location = job_location.text
            # print(f"The job location is {job_location}")
        except:
            job_location = ""

        # Find city and state
        try:
            city, state = find_city_state_in_title(job_location)
        except:
            city, state = [part.strip() for part in job_location.split(',')[:2]]
        # print(f"The city is {city}")    
        # print(f"The state is {state}")    
        
        # Find job description
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("div", class_="jv-job-detail-description")
        job_description = desc_content.prettify() if desc_content else None

        Checking_remote1 = is_remote(job_location)
        Checking_remote2 = is_remote(job_title)
        if(Checking_remote1 or Checking_remote2):
            Location = "Remote"
            Remote = True
        else:    
            Location = extracting_location(city,state)
            Remote = False
        # print(f"the location is : {Location}")   
        # print(f"Remote : {Remote}")     

        jobDetails = {
            "Job Id": "",
            "Job Title": job_title,
            "Job Description": job_description,
            "Job Type": "",
            "Categories": "Pharmaceuticals",
            "Location": Location,
            "City": city,
            "State": state,
            "Country": "United States",
            "Zip Code": "",
            "Address": Location,
            "Remote": Remote,
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
            "Employer Email": "msh@mshneogenomics.com",
            "Full Name": "",
            "Company Name": "NeoGenomics",
            "Employer Website": "https://jobs.jobvite.com/",
            "Employer Phone": '866-776-5901',
            "Employer Logo": "https://careers.jobvite.com/neogenomics/images/logos/logo.svg",
            "Company Description": "NeoGenomics, Inc. specializes in cancer genetics testing and information services, providing one of the most comprehensive oncology-focused testing menus in the world for physicians to help them diagnose and treat cancer. The Company's also serves pharmaceutical clients in clinical trials and drug development.",
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
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://jobs.jobvite.com/neogenomics/search?q=sales%20United%20States"
        try:
            driver.get(url)
            Jobs_links = getting_links(driver)
            
            list_jobs = extracting_links(Jobs_links,driver)

            if list_jobs:
                write_to_csv(list_jobs, "data", "NeoGenomics.csv")
            else:
                pass

        except Exception as e:
            pass
    except Exception as e:
        pass
scraping()
