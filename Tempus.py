import time

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

    results = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "job-list-content")
    ))
    jobs = WebDriverWait(results, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
    )
    job_links = [
        job.find_element(By.CLASS_NAME, "job").get_attribute("href")
        for job in jobs
    ]

    for job in job_links:
        if job not in unique_jobs:
            unique_jobs.add(job)
            JOBS.append(job)

    print('jobs', len(JOBS))

    return JOBS

def getJobs(driver):
    JOBS = []
    time.sleep(1)
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find("h1", class_="app-title")
            jobTitle = title_meta.text if title_meta else ''
            print('title', jobTitle)
            desc_content = soup.find('div', {'id': 'content'})
            jobDescription = desc_content.prettify() if desc_content else ''

            location_meta = soup.find('div', class_='location')
            Location = location_meta.text.strip() if location_meta else ''
            City = state = ''
            print('location', Location)
            country = 'United States'
            if Location:
                location_parts = Location.split(',')
                if len(location_parts) == 3:
                    City = location_parts[0].strip()
                    state = location_parts[1].strip()
                elif len(location_parts) == 2:
                    City = location_parts[0].strip()
                    state = location_parts[1].strip()
                else:
                    City = state = ''

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
                "Employer Email": "msh@mshtempus.com",
                "Full Name": "",
                "Company Name": "Tempus",
                "Employer Website": " https://www.tempus.com/",
                "Employer Phone": "",
                "Employer Logo": "https://www.tempus.com/wp-content/themes/tempus-theme/dist/images/tempus_black.svg",
                "Company Description": "We’re building innovative tech solutions oriented around clinical care and research products—and the virtuous cycle between them.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS

def scraping():
    try:
        driver = configure_undetected_chrome_driver(True)
        driver.maximize_window()
        url = " https://www.tempus.com/job-postings/?department=&location=&filter=sales&remoteFriendly=0"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Tempus.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
