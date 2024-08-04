import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
)
from bs4 import BeautifulSoup
import csv
import os

from helpers import configure_webdriver, is_remote

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
    try:
        ukg_ignite_shell = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ukg-ignite-shell')))
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', ukg_ignite_shell)

        if shadow_root:
            try:
                results = wait.until(EC.presence_of_element_located((By.ID, "Opportunities")))
                jobs = WebDriverWait(results, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "opportunity")))

                for job in jobs:
                    try:
                        job_link = job.find_element(By.CLASS_NAME, 'opportunity-link').get_attribute("href")
                        JOBS.append(job_link)
                    except StaleElementReferenceException as e:
                        print(f"StaleElementReferenceException encountered: {e}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error processing job card: {e}")

            except Exception as e:
                print(f"Error during job loading or pagination: {e}")

        else:
            print("Shadow root not found.")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")

    time.sleep(2)
    return JOBS

def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    wait = WebDriverWait(driver, 10)
    ukg_ignite_shell = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ukg-ignite-shell')))
    shadow_root = driver.execute_script('return arguments[0].shadowRoot', ukg_ignite_shell)

    if shadow_root:
        for job in jobs:
            try:
                driver.get(job)
                time.sleep(2)
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
                
                # Using a helper function to get the text if the element exists
                def get_text_if_exists(soup, selector):
                    element = soup.select_one(selector)
                    return element.text if element else ''

                jobTitle = get_text_if_exists(soup, 'span[data-automation="opportunity-title"]')
                job_id = get_text_if_exists(soup, 'span[data-automation="requisition-number"]')
                if not job_id:
                    job_id = jobs.index(job)  # Use index if job_id is not found

                posted_date = get_text_if_exists(soup, 'span[data-automation="job-posted-date"]')
                location_meta = get_text_if_exists(soup, 'span[data-automation="city-state-zip-country-label"]')
                location_parts = location_meta.split(',') if location_meta else []
                City = location_parts[0].strip() if len(location_parts) == 3 else ''
                state = location_parts[1].strip() if len(location_parts) == 3 else ''
                country = 'United States'
                Remote = 'Remote' in get_text_if_exists(soup, 'span[data-automation="name-and-location-id-label"]')

                desc_content = soup.find("p", class_="opportunity-description")
                jobDescription = desc_content.prettify() if desc_content else ''

                jobDetails = {
                    "Job Id": job_id,
                    "Job Title": jobTitle,
                    "Job Description": jobDescription,
                    "Job Type": 'Full time',
                    "Categories": "Diagnostic",
                    "Location": location_meta,
                    "City": City,
                    "State": state,
                    "Country": country,
                    "Zip Code": '',
                    "Address": location_meta,
                    "Remote": Remote,
                    "Salary From": "",
                    "Salary To": "",
                    "Salary Period": "",
                    "Apply URL": job,
                    "Apply Email": "",
                    "Posting Date": posted_date,
                    "Expiration Date": "",
                    "Applications": "",
                    "Status": "",
                    "Views": "",
                    "Employer Email": "msh@mshlantheus.com",
                    "Full Name": "",
                    "Company Name": "Lantheus",
                    "Employer Website": "https://recruiting.ultipro.com/LAN1018LMII/JobBoard/",
                    "Employer Phone": "",
                    "Employer Logo": "https://recruiting.ultipro.com/LAN1018LMII/JobBoar…-bbd1-406f-8a87-e66bccf06598&m=637897818732430000",
                    "Company Description": "We are the leading radiopharmaceutical-focused company with proven expertise in developing, manufacturing, and commercializing pioneering diagnostic and therapeutic products and artificial intelligence (AI) solutions",
                    "Status": "Active",
                }
                JOBS.append(jobDetails)

                driver.switch_to.default_content()
            except Exception as e:
                print(f"Error in loading post details: {e}")
    else:
        print("Shadow root not found.") 
    return JOBS

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://recruiting.ultipro.com/LAN1018LMII/JobBoard/8cb8bdef-5c4b-4689-a408-96fe4b0a207e/?q=sales&o=relevance&w=&wc=&we=&wpst="
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            if Jobs:
                write_to_csv(Jobs, "data", "Lantheus.csv")
            else:
                print("No jobs found.")
        except Exception as e:
            print(f"Error during job scraping: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
