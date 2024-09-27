import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import csv
import os
from helpers import configure_webdriver, is_remote
from extractCityState import *

def getting_links(driver):
    jobs_link = []
    i = 1
    while True:
        try:
            link_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"(//a[@class='job-list-item__link'])[{i}]")
                )
            )
            link = link_element.get_attribute("href")
            jobs_link.append(link)
            i += 1
        except:
            #print(f"number of jobs get {(len(jobs_link))}")
            return jobs_link

def extracting_links(link_list, driver):
    list_jobs = []
    i = 0
    for link in link_list:
        try:
            driver.get(link)
            job_details = getting_values(driver, link)
           #print(f"the length of job detail in extracting link are :{(len(job_details))}")
            if job_details:
                i+=1
                list_jobs.append(job_details)
        except Exception as e:
            pass
    #print(f"the length of i is {i}")
    #print(f"the length of list_jobs in extracting links are {(len(list_jobs))}")
    return list_jobs

d = 0
def getting_values(driver, url):
    try:
        # Find and print job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@class='heading job-details__title']"))
        ).text
        (f"the job title is : {job_title}")
        if not filter_job_title(job_title):
            global d
            d += 1
            return None
        

        

        # Find and print job location
        
        job_location = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//div[@class='job-details__subtitle text-color-secondary']"))
        ).text
        job_location = job_location.split('States')[0] + 'States' if 'States' in job_location else job_location
        
        try:
            city, state = find_city_state_in_title(job_location)
        except:
            city = job_location.split(',')[0].strip()
            state = job_location.split(',', 2)[1].split(',')[0].strip() if ',' in job_location else job_location.split(',', 1)[1].strip()

        if(city == None and state == None):
            job_location = job_title.rsplit('-', 1)[-1].strip()
            try:
                city, state = find_city_state_in_title(job_location)
            except:
                city = job_location.split(',')[0].strip()
                state = job_location.split(',', 2)[1].split(',')[0].strip() if ',' in job_location else job_location.split(',', 1)[1].strip()

        #print(f"the job location is : {job_location}")
        # Find city and state
        #print(f"the city is : {city}")
        #print(f"the state is : {state}")


        # Find job description
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("div", class_="job-details__section")
        job_description = desc_content.prettify() if desc_content else None

        
        #location
        location = city + ', ' + state + ', ' + 'USA'

        #job id
        job_id = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//li[span[text()='Job Identification']]//span[2]"))
        ).text
        #print(f"the job is is : {job_id}")

        #starting salary
        salary_start = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//li[span[text()='Minimum Salary']]//span[2]"))
        ).text
       #print(f"salary starting : {salary_start}")

        #starting salary
        salary_ending = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//li[span[text()='Midpoint Salary']]//span[2]"))
        ).text
        #print(f"salary ending: {salary_ending}")

        #posting date
        posting_date = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//li[span[text()='Posting Date']]//span[2]"))
        ).text
        #print(f"posting date : {posting_date}")

        #is remote
        remote = is_remote(job_location)
        #print(f"the job is remote or not : {remote}")

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
            "Address": location,
            "Remote": is_remote(job_location),
            "Salary From": salary_start,
            "Salary To": salary_ending,
            "Salary Period": "",
            "Apply URL": url,
            "Apply Email": "",
            "Posting Date": posting_date,
            "Expiration Date": "",
            "Applications": "",
            "Status": "",
            "Views": "",
            "Employer Email": "msh@mshmyriad.com",
            "Full Name": "",
            "Company Name": "Myriad",
            "Employer Website": "https://myriad.com/",
            "Employer Phone": '(888) 268-6795',
            "Employer Logo": "https://myriad.com/wp-content/uploads/2024/03/Myriad_genetics_logo.svg",
            "Company Description": "As a leader in genetic testing and precision medicine, Myriad is committed to a long-term growth strategy fueled by high quality, science driven products, a strong and scalable commercial engine and innovative tech, data and research capabilities. We are a trusted, differentiated healthcare partner with specialized expertise that persistently works to strengthen our strategic advantages regardless of market conditions.",
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
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.maximize_window()
    url = "https://ekgn.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2001/requisitions?keyword=sales&location=United+States&locationId=300000000306332&locationLevel=country&mode=location"
    driver.get(url)
    
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)
    
    links = getting_links(driver)
    list_jobs = extracting_links(links, driver)
    #print(f"the length of list_jobs in scraping is {(len(list_jobs))}")
    if list_jobs != None:
        write_to_csv(list_jobs, "data", "Myriad.csv")
    else:
        print("No job details found.")
    #print(f"the value of d is {d}")
    driver.quit()

scraping()