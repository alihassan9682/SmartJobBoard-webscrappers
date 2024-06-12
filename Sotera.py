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
        (By.CLASS_NAME, "jobs-list__list")
    ))
    jobs = WebDriverWait(results, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-qa='searchResultItem']"))
    )
    job_links = [
        job.find_element(By.TAG_NAME, "a").get_attribute("href")
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
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(3)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find("h1", class_="job-details__title")
            jobTitle = title_meta.text if title_meta else ''
            print('title', jobTitle)
            desc_content = soup.find('div', class_= "job-details__section")
            jobDescription = desc_content.prettify() if desc_content else ''

            location_meta = soup.find('span', {'data-bind': 'html: postingLocationsContent'})
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
            job_details = {}
            for item in soup.select('.job-meta__item'):
                title = item.find(class_='job-meta__title').text.strip()
                value = item.find(class_='job-meta__subitem').text.strip()
                job_details[title] = value
            Zipcode = ''
            jobDetails = {
                "Job Id": job_details.get('Job Identification', jobs.index(job)),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Diagnostic",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": job_details.get('Locations', ''),
                "Remote": is_remote(Location),
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": job_details.get('Posting Date', ''),
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshsotera.com",
                "Full Name": "",
                "Company Name": "Sotera",
                "Employer Website": "https://eftx.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1007",
                "Employer Phone": "",
                "Employer Logo": "https://soterahealth.com/wp-content/uploads/2023/05/careers-logo.png",
                "Company Description": "Sotera Health is driven by its mission, Safeguarding Global Health®. Along with our three best-in-class businesses – Sterigenics®, Nordion® and Nelson Labs® – we are a leading global provider of mission-critical end-to-end sterilization solutions and lab testing and advisory services for the healthcare industry.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://eftx.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1007/requisitions?keyword=sales&lastSelectedFacet=LOCATIONS&mode=location&selectedLocationsFacet=300000000229164"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Sotera.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
