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
        cookies = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
        cookies.click()
    except:
        pass   


def getting_links(driver):
    link_list = []
    i = 0
    while True:
        i+=1
        # for _ in range(2):
        #     driver.execute_script("window.scrollBy(0, 1000);")
        #     time.sleep(1)
        
        try:
            container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//ul[@data-ph-at-id='jobs-list']/li[{i}]//div[@class='information']")))
            a_elements = WebDriverWait(container, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            for a in a_elements:
                try:
                    href_value = a.get_attribute('href')
                    if not href_value in link_list:
                        link_list.append(href_value)
                except:
                    pass    

        except:
            try:
                next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@key-aria-label='c-sales-zcdusz-ph-search-results-v2-default-viewNextPage']")))
                next_button.click()
                i = 0
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
        
        #finding id
        
        job_id = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@show.bind='jobDetail.jobId']"))
        )
        job_id = job_id.text
        job_id = job_id.split('\n')[1]
        # print(f"the job id is : {job_id}") 

        
        
        

        # Find and print job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@data-ph-id='ph-page-element-page5-JpVU0a']"))
        )
        job_title = job_title.text
        # print(f"The job title is {job_title}")


        # Find and print job location
        try:
            job_location = job_title
            job_location = job_location.rsplit('-', 1)[-1]
            #print(f"The job location is {job_location}")
        except:
            job_location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@data-ph-id='ph-page-element-page5-d9mSer']")))
            job_location = job_location.text
            job_location = job_location.split('\n')[1] 

        # Find city and state
        try:
            city, state = find_city_state_in_title(job_location)
        except:
            city, state = find_city_state_in_title(job_title)
        # print(f"The city is {city}")    
        # print(f"The state is {state}")    
        

        # Find job description
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("div", attrs={"data-ph-at-id": "jobdescription-text"})
        job_description = desc_content.prettify() if desc_content else None
        # print("done getting discription")

        Checking_remote1 = is_remote(job_location)
        Checking_remote2 = is_remote(job_title)
        if(Checking_remote1 or Checking_remote2):
            Location = "Remote"
            Remote = True
        else:    
            Location = extracting_location(city,state)
            Remote = False
        # print(f"the location : {Location}")    
        # print(f"Remote : {Remote}")    
        
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
            "Employer Email": "msh@mshconmed.com",
            "Full Name": "",
            "Company Name": "Conmed",
            "Employer Website": "https://conmed.com/",
            "Employer Phone": '844.602.6637',
            "Employer Logo": "",
            "Company Description": "Exceptional People. Exceptional Outcomes. A Global Medical Technology Company",
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
        url = "https://careers.conmed.com/c/sales-jobs/search-results?qcountry=United%20States%20of%20America"
        try:
            driver.get(url)
            removing_tags(driver)
            Jobs_links = getting_links(driver)
            list_jobs = extracting_links(Jobs_links,driver)
            if list_jobs:
                # print("Going to create csv")
                write_to_csv(list_jobs, "data", "Conmed.csv")
            else:
                # print("No job details found.")
                pass

        except Exception as e:
            pass
    except Exception as e:
        pass
scraping()
