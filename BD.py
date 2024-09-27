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


def removing_tags(driver):
    try:
        cookies = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@data-custom-label='GDPR Accept Button']")))
        cookies.click()
    except:
        pass   
    
    try:
        cookies = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@data-custom-label='GDPR Accept Button']")))
        cookies.click()
    except:
        pass   

def getting_links(driver):
    link_list = []
    
    while True:
        for _ in range(2):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='search-results-list-wrapper']")))
        a_elements = WebDriverWait(container, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        for a in a_elements:
            try:
                href_value = a.get_attribute('href')
                if not href_value in link_list:
                    link_list.append(href_value)
            except:
               pass
          
        try:
            
            next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='NEXT PAGE']")))
            next_button.click()
        except:
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
        
        #finding id
        job_id = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='job-id job-info']"))
        )
        
        job_id = job_id.text
        job_id = job_id.split('\n')[1] 
        
        
        

        # Find and print job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@class='search-title']"))
        )
        job_title = job_title.text
        #print(f"The job title is {job_title}")

        # Find and print job location
        try:
            job_location = job_title
            job_location = job_location.split("(")[1].rstrip(")")
            #print(f"The job location is {job_location}")
        except:
            job_location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='banner-content-wrapper']//p")))
            job_location = job_location.text
            # print(f"The job location is {job_location}")
             

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
        desc_content = soup.find("div", class_="ats-description ajd_job-details__ats-description")
        job_description = desc_content.prettify() if desc_content else None

        if(is_remote(job_location)):
            Location = "Remote"
            # print(f"the location is {Location}")
        else:    
            Location = extracting_location(city,state)
            # print(f"the location is {Location}")

        job_type = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[@class='ajd_overview__quick-fact ajd_overview__quick-fact--time']//span")))
        job_type = job_type.text
        job_type = job_type.split('\n')[1] 
        # print(f"the job type is {job_type}")

        Remote = is_remote(job_location)
        
        jobDetails = {
            "Job Id": job_id,
            "Job Title": job_title,
            "Job Description": job_description,
            "Job Type": job_type,
            "Categories": "Pharmaceuticals",
            "Location": Location,
            "City": city,
            "State": state,
            "Country": "United States",
            "Zip Code": "",
            "Address": job_location,
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
            "Employer Email": "msh@mshbd.com",
            "Full Name": "",
            "Company Name": "BD",
            "Employer Website": "https://jobs.bd.com/",
            "Employer Phone": '201.847.6800',
            "Employer Logo": "https://tbcdn.talentbrew.com/company/159/17183/content/BD_logo_white.png",
            "Company Description": "For 125 years, we've pursued our Purpose of advancing the world of health™. We relentlessly commit to a promising future by developing innovative technologies, services and solutions, helping the healthcare community improve safety and increase efficiency.",
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
        url = "https://jobs.bd.com/search-jobs/Sales/United%20States/159/1/2/6252001/39x76/-98x5/0/2"
        try:
            driver.get(url)
            removing_tags(driver)
            Jobs_links = getting_links(driver)
            
            list_jobs = extracting_links(Jobs_links,driver)
            if list_jobs:
                write_to_csv(list_jobs, "data", "BD.csv")
            else:
                pass

        except Exception as e:
            pass
    except Exception as e:
        pass
scraping()