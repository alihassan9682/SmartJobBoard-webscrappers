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

def cookies(driver):
    try:
        cookies = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
        cookies.click()
    except:
        pass   
 

def getting_links(driver):
    link_list = []
    
    while True:
        

        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//section[@id='search-results-list']//ul")))
        a_elements = WebDriverWait(container, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        for a in a_elements:
            try:
                href_value = a.get_attribute('href')
                if not href_value in link_list:
                    link_list.append(href_value)
            except:
               pass
          
        try:
            
            next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pagination-paging')]//a[contains(@class, 'next')]")))
            next_button.click()
        except:
            # print(len(link_list))
            
            return link_list 

def extracting_links(link_list, driver):
    list_jobs = []
    for link in link_list:
        try:
            driver.get(link)
            # print("now going to get values")
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
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'job-id') and contains(@class, 'job-info')]")))
        job_id = job_id.text
        # print(f"the job id is {job_id}")
        
        
        

        # Find and print job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(@class, 'job-details-heading')]"))
        )
        job_title = job_title.text
        # print(f"The job title is {job_title}")

        # Find and print job location
        
        try:
            job_location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'job-info') and contains(@class, 'job-location') and contains(@class, 'Multi') and contains(@class, 'loc')]")))
            job_location = job_location.text
            # print(f"The job location is {job_location}")
        except:
            pass

        # Find city and state
        try:
            city, state = find_city_state_in_title(job_location)
        except:
            get = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'job-info') and contains(@class, 'job-location') and contains(@class, 'Multi') and contains(@class, 'loc')]")))
            
            city, state = find_city_state_in_title(get)
        # print(f"The city is {city}")    
        # print(f"The state is {state}")    
        
        # Find job description
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("div", class_="ats-description")
        job_description = desc_content.prettify() if desc_content else None
        # print(f"The job description is done")

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

        # job_type = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, "//li[@class='ajd_overview__quick-fact ajd_overview__quick-fact--time']//span")))
        # job_type = job_type.text
        # job_type = job_type.split('\n')[1] 
        # print(f"the job type is {job_type}")

        
        
        jobDetails = {
            "Job Id": job_id,
            "Job Title": job_title,
            "Job Description": job_description,
            "Job Type": "",
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
            "Employer Email": "msh@mshiqvia.com",
            "Full Name": "",
            "Company Name": "BD",
            "Employer Website": "https://jobs.bd.com/",
            "Employer Phone": '201.847.6800',
            "Employer Logo": "https://tbcdn.talentbrew.com/company/159/17183/content/BD_logo_white.png",
            "Company Description": "For 125 years, we've pursued our Purpose of advancing the world of health™. We relentlessly commit to a promising future by developing innovative technologies, services and solutions, helping the healthcare community improve safety and increase efficiency.",
            "Status": "Active",
        }
        # print("done with job details")
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
        url = "https://jobs.iqvia.com/en/search-jobs/Sales/United%20States/24443/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            cookies(driver)
            links = getting_links(driver)
            
            # print("now extracting")
            list_jobs = extracting_links(links,driver)
            # print("making csv")
            write_to_csv(list_jobs, "data", "IQVIA.csv")
        except Exception as e:
            pass
    except Exception as e:
        pass


scraping()