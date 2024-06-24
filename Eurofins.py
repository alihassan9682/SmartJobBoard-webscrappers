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
    close = wait.until(
        EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
    )
    close.click()
    
    prev_job_count = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust sleep time as needed to wait for the jobs to load

        results = wait.until(EC.presence_of_element_located(
            (By.ID, "joblist")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "boxlist"))
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

        if len(JOBS) == prev_job_count:
            break
        prev_job_count = len(JOBS)
    
    return JOBS

def getJobs(driver):
    JOBS = []
    time.sleep(1)
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(1)
            title_meta = driver.find_element(By.CLASS_NAME, "job-title")
            jobTitle = title_meta.text if title_meta else ''
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find('div', itemprop='description')
            jobDescription = desc_content.prettify() if desc_content else ''

            location_meta = soup.find('span', class_='summary-detail')
            Location = location_meta.text if location_meta else ''
            City = state = ''
            country = 'United States'
            if Location:
                location_parts = Location.split(',')
                if len(location_parts) == 3:
                    City = location_parts[0].strip()
                    state = location_parts[1].strip()
                elif len(location_parts) == 2:
                    City = location_parts[0].strip()
                    state = ''
                else:
                    City = state = ''

            employment_type = soup.find('li', itemprop='employmentType').text.strip()
            Zipcode = ''

            date_posted_meta = soup.find('meta', itemprop='datePosted')
            date_posted = date_posted_meta['content'] if date_posted_meta else ''
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": employment_type if employment_type else '',
                "Categories": "Diagnostic",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": '',
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": date_posted,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@msheurofins.com",
                "Full Name": "",
                "Company Name": "Eurofins",
                "Employer Website": "https://careers.eurofins.com/",
                "Employer Phone": "",
                "Employer Logo": "https://c.smartrecruiters.com/sr-company-images-prod-aws-dc5/59a68830e4b02f57443071f7/8c61bb56-beca-4635-b558-78899fdad486/huge?r=s3-eu-central-1&_1694667983751",
                "Company Description": "Eurofins Scientific is an international life sciences company, providing a unique range of analytical testing services to clients across multiple industries, to make life and our environment safer, healthier and more sustainable. From the food you eat, to the water you drink, to the medicines you rely on, Eurofins works with the biggest companies in the world to ensure the products they supply are safe, their ingredients are authentic and labelling is accurate.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS

def scraping():
    try:
        driver = configure_undetected_chrome_driver(True)
        driver.maximize_window()
        url = "https://careers.eurofins.com/us/jobs/?keywords=sales&countryId=us"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Eurofins.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
