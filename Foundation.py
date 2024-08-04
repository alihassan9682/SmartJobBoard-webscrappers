import time

from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


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
    wait = WebDriverWait(driver, 10)
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "table")
        ))
        job_links = results.find_elements(By.CSS_SELECTOR, "tr > td > a")
        
        for link in job_links:
            job_url = link.get_attribute("href")
            if job_url and job_url not in JOBS:
                JOBS.append(job_url)
        try:

            next_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "next"))
            )
            
            if next_button and 'disabled' not in next_button.get_attribute('class'):
                actions = ActionChains(driver)
                actions.move_to_element(next_button).click().perform()
                time.sleep(2)
            else:
                break
        except:
            print("No more pages or an error occurred")
            break


    return JOBS


def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            job_meta = driver.find_element(By.CLASS_NAME, "job-title")
            jobTitle = job_meta.text if job_meta else ''
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="job-description")
            job_type_meta = soup.find("span", {'id': 'employment_type_2_2_0_0'})
            job_type = job_type_meta.text.strip() if job_type_meta else ''
            jobDescription = desc_content.prettify()
            locations = soup.find_all('span', id=lambda x: x and x.startswith('location_'))

            location_list = []
            city_list = []
            state_list = []
            country = "United States"

            for location in locations:
                loc_text = location.get_text(strip=True)
                parts = [part.strip() for part in loc_text.split(',')]
                
                if len(parts) == 3:
                    city_list.append(parts[0])
                    state_list.append(parts[1])
                
                location_list.append(loc_text)
            location = ', '.join(location_list) if location_list else ''
            City = ', '.join(city_list) if city_list else ''
            state = ', '.join(state_list) if state_list else ''
            Zipcode = ''

            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type if job_type else '',
                "Categories": "Diagnostic",
                "Location": location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": location,
                "Remote": '',
                "Salary From": '',
                "Salary To": '',
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": '',
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshfoundation.com",
                "Full Name": "",
                "Company Name": "Foundation Medicine",
                "Employer Website": "https://careers.foundationmedicine.com",
                "Employer Phone": "",
                "Employer Logo": "https://files.clinchtalent.com/foundation-medicine…503f1be2ea7611d2d34a5d746b33d4/Logos/fmi-logo.png",
                "Company Description": "Foundation Medicine began with an idea—to simplify the complex nature of cancer genomics, bringing cutting-edge science and technology to everyday cancer care. Our approach generates insights that help doctors match patients to more treatment options and helps accelerate the development of new therapies. Foundation Medicine is the culmination of talented people coming together to realize an important vision, and the work we do every day impacts real lives.",
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
        url = "https://careers.foundationmedicine.com/jobs/search?block_index=0&block_uid=e212863cb3af48a84294098bca2a239c&country_codes%5B%5D=US&location_uids=&page=1&page_row_index=3&page_row_uid=7f0237d79099871492807d60f29486e5&page_version_uid=62d51d9cd9bb6f2ececd64f314111712&query=sales&search_cities=&search_country_codes=&search_departments=&sort="
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Foundation.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
