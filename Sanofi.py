import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import os

from helpers import configure_webdriver, is_remote  # Ensure these imports are correct for your environment

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
    close = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "system-alert-close"))
    )
    close.click()

    location_section = wait.until(
        EC.presence_of_element_located((By.ID, "country-toggle"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(location_section).perform()

    checkbox = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox'][data-display='United States']"))
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    time.sleep(1)

    driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(2)

    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "search-results-list")
        ))
        job_links = results.find_elements(By.CSS_SELECTOR, "ul > li > a")
        for link in job_links:
            job_url = link.get_attribute("href")
            if job_url:
                JOBS.append(job_url)
        try:
            next_button = driver.find_element(By.CLASS_NAME, "next")
            if 'disabled' in next_button.get_attribute('class'):
                print('no more pages')
                break
            else:
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next")))
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
        except:
            break
    return JOBS


def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            jobTitle = driver.find_element(By.CLASS_NAME, "main-heading").text
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify()
            Location = driver.find_element(By.CLASS_NAME, "job-location").text
            location_meta = Location.split(';') if ';' in Location else [Location]
            cities = [loc.strip().split(',')[0].strip() if loc.strip() else '' for loc in location_meta]
            states = [loc.strip().split(',')[1].strip() if ',' in loc and len(loc.split(',')) > 1 else '' for loc in location_meta]

            city = ', '.join(cities) if cities else ''
            state = ', '.join(states) if states else ''

            country = 'United States'
            Zipcode = ''
            date_posted = soup.find('span', class_='job-date').text
            job_id = soup.find('span', class_='job-id job-info icon-job-id with-text').text
            job_type = soup.find('span', class_='icon-contract with-text').text

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": city,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address":Location,
                "Remote": is_remote(Location),
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
                "Employer Email": "msh@mshsnofi.com",
                "Full Name": "",
                "Company Name": "Sanofi",
                "Employer Website": "https://en.jobs.sanofi.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "We are an innovative global healthcare company with one purpose: to chase the miracles of science to improve people’s lives",
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
        url = "https://en.jobs.sanofi.com/search-jobs/sales/20873/1"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Sanofi.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
