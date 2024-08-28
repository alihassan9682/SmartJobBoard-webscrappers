import time

from extractCityState import filter_job_title, find_city_state_in_title
from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import csv
import os

def request_url(driver, url):
    driver.get(url)

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
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    results = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "[data-id='4025647004']")
    ))
    jobs = WebDriverWait(results, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "jobs_post"))
    )
    job_links = [
        job.find_element(By.TAG_NAME, "a").get_attribute("href")
        for job in jobs
    ]

    for job in job_links:
        if job not in unique_jobs:
            unique_jobs.add(job)
            JOBS.append(job)


    return JOBS

def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            
            iframe = driver.find_element(By.ID, 'grnhse_iframe')
            driver.switch_to.frame(iframe)
            time.sleep(2)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find("h1", class_="app-title")
            jobTitle = title_meta.text if title_meta else ''
            print("job title: " + jobTitle)
            if not filter_job_title(jobTitle):
                continue
            desc_content = driver.find_element(By.ID, "content")
            jobDescription = desc_content if desc_content else ''
            City = state = Location = ''
            country = 'United States'

            city_title, state_title = find_city_state_in_title(Location)
            if city_title:
                City = city_title
            if state_title:
                state = state_title
            if city_title and state_title:
                Location = city_title + ', ' + state_title
            else:
                Location = ''
            Zipcode = ''
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Diagnostic",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(Location),
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
                "Employer Email": "msh@mshnatera.com",
                "Full Name": "",
                "Company Name": "Natera",
                "Employer Website": "https://www.natera.com/",
                "Employer Phone": "",
                "Employer Logo": "https://www.natera.com/wp-content/themes/natera/assets/images/logo.svg",
                "Company Description": "Natera™ is a global leader in cell-free DNA (cfDNA) testing, dedicated to oncology, women’s health, and organ health. We aim to make personalized genetic testing and diagnostics part of the standard of care to protect health and inform earlier, more targeted interventions that help lead to longer, healthier lives.",
                "Status": "Active",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://www.natera.com/company/careers/job-openings/"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Natera.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
