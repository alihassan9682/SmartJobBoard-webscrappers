import time
from helpers import configure_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from extractCityState import find_city_state_in_title
from helpers import configure_webdriver, is_remote  
import csv
import os
from extract_location import extracting_location


def write_to_csv(data, directory, filename):
    fieldnames = list(data[0].keys())
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)


def loadAllJobs(driver):
    JOBS = []
    unique_jobs = set()
    wait = WebDriverWait(driver, 10)

    while True:
        try:
            iframe = wait.until(EC.presence_of_element_located((By.ID, 'icims_content_iframe')))
            driver.switch_to.frame(iframe)

            results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iCIMS_JobsTable")))
            jobs = results.find_elements(By.CLASS_NAME, "row")

            job_links = [
                job.find_element(By.CLASS_NAME, "title").find_element(By.TAG_NAME, 'a').get_attribute("href")
                for job in jobs
            ]

            for job in job_links:
                if job not in unique_jobs:
                    unique_jobs.add(job)
                    JOBS.append(job)

            next_button = driver.find_elements(By.CSS_SELECTOR, ".iCIMS_Paging .glyph")[-1]
            if 'invisible' not in next_button.get_attribute('class'):
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                time.sleep(2)
            else:
                break
            driver.switch_to.default_content()
        except TimeoutException:
            break
        except Exception as e:
            break
        driver.switch_to.default_content()

    return JOBS


def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    wait = WebDriverWait(driver, 20)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(3)

            iframe = wait.until(EC.presence_of_element_located((By.ID, 'icims_content_iframe')))
            driver.switch_to.frame(iframe)
            job_location = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='col-xs-6 header left']")))

            job_location = job_location.text
            job_location = job_location.split('\n')[1].strip() 
        
            City, state = find_city_state_in_title(job_location)

            country = 'United States'
            Zipcode = ''

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="iCIMS_JobContent")
            first_para = desc_content.find("div", class_="container-fluid iCIMS_JobsTable")
            last_para = desc_content.find("div", class_="iCIMS_Logo")
            if first_para:
                first_para.decompose()
            if last_para:
                last_para.decompose()
            jobDescription = desc_content.prettify()

            jobTitle = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iCIMS_Header"))).text

            additional_fields_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "col-xs-12.additionalFields")))
            additional_fields = additional_fields_element.find_elements(By.CLASS_NAME, "iCIMS_JobHeaderTag")

            job_details = {}
            if additional_fields:
                for field in additional_fields:
                    field_name_element = field.find_element(By.CLASS_NAME, 'iCIMS_JobHeaderField')
                    field_value_element = field.find_element(By.CLASS_NAME, 'iCIMS_JobHeaderData')
                    field_name = field_name_element.text.strip()
                    field_value = field_value_element.text.strip()
                    job_details[field_name] = field_value

            Job_id = job_details.get('Requisition ID', jobs.index(job))

            Checking_remote1 = is_remote(job_location)
            Checking_remote2 = is_remote(jobTitle)
            if(Checking_remote1 or Checking_remote2):
                Location = "Remote"
                Remote = True
            else:    
                Location = extracting_location(City,state)
                Remote = False

            


            jobDetails = {
                "Job Id": Job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_details.get('Position Type', ''),
                "Categories": "Medical Device",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": job_location,
                "Remote": Remote,
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshbbraun.com",
                "Full Name": "",
                "Company Name": "B Braun",
                "Employer Website": "https://bbrauncareers-bbraun.icims.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "The B. Braun Group of Companies leads in thoughtful solutions that address real issues in patient care and clinician safety. The global slogan, Sharing Expertise® fosters a teamwork approach to saving lives and solving the problems of the health care industry. It is an ethical and purposeful work culture that welcomes innovation and rewards progress.",
                "Status": "Active",
            }
            JOBS.append(jobDetails)

            driver.switch_to.default_content()

        except Exception as e:
            pass
    return JOBS

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://bbrauncareers-bbraun.icims.com/jobs/search?ss=1&searchKeyword=sales&searchRelation=keyword_all&searchLocation=12781--"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "B Braun.csv")
        except Exception as e:
            pass
    except Exception as e:
        pass

scraping()
