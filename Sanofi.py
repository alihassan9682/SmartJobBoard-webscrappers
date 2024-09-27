# -*- coding: utf-8 -*-

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import os

from extractCityState import filter_job_title, find_city_state_in_title
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
        EC.presence_of_element_located((By.CLASS_NAME, "banner-close-button"))
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
    checkbox1 = wait.until(
            EC.presence_of_element_located((By.ID, "category-toggle"))
        )

    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox1)
    driver.execute_script("arguments[0].click();", checkbox1)
    time.sleep(1)
    
    sales_checkbox = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-display=Sales]"))
    )

    driver.execute_script("arguments[0].click();", sales_checkbox)
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
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.4);")
            time.sleep(2)
            job_div = driver.find_element(By.CLASS_NAME, "job-description")
            jobTitle = job_div.find_element(By.TAG_NAME, "h1").text
            job_id = job_div.get_attribute("data-job-id")
            if not filter_job_title(jobTitle):
                continue
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify() if desc_content else ''
            city_title, state_title = find_city_state_in_title(jobTitle)
            # Extract location safely
            Location = driver.find_element(By.CLASS_NAME, "job-location").text if driver.find_elements(By.CLASS_NAME, "job-location") else ''
            location_meta = Location.split(';') if Location and ';' in Location else [Location]
            cities = []
            states = []
            
            for loc in location_meta:
                parts = loc.strip().split(',')
                if len(parts) > 0:
                    cities.append(parts[0].strip())
                if len(parts) > 1:
                    states.append(parts[1].strip())

            city = ', '.join(cities) if cities else ''
            state = ', '.join(states) if states else ''
            if city_title:
                city = city_title
            if state_title:
                state = state_title

            from extract_location import extracting_location
            Location = extracting_location(city,state)
            
            country = 'United States'
            Zipcode = ''
            date_posted = soup.find('span', class_='job-date').text if soup.find('span', class_='job-date') else ''
            job_type = soup.find('span', class_='job-type job-info').text if soup.find('span', class_='job-type job-info') else ''

            jobDetails = {
                "Job Id": job_id if job_id else jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type if job_type else '',
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": city,
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
                "Posting Date": date_posted,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshsanofi.com",
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
            pass
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://jobs.sanofi.com/en/search-jobs/sales/United%20States/2649/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            
            write_to_csv(Jobs, "data", "Sanofi.csv")
        except Exception as e:
            pass
    except Exception as e:
        pass


scraping()
