import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import re
import us
import geonamescache
import os

from helpers import configure_webdriver, is_remote

gc = geonamescache.GeonamesCache()

us_cities = gc.get_cities()
us_states = us.states.mapping('abbr', 'name')
us_states_rev = us.states.mapping('name', 'abbr')

def request_url(driver, url):
    driver.get(url)

def find_city_state_in_title(title):
    title_cleaned = title.lower()

    # Debug: Print cleaned title
    print(f"Processing title: {title_cleaned}")

    detected_city = None
    detected_state = None

    # Check for city in the title using regular expressions
    for city in us_cities.values():
        city_name = city['name'].lower()
        if re.search(rf'\b{re.escape(city_name)}\b', title_cleaned):
            detected_city = city['name']
            print(f"Found city: {detected_city} in title")
            break  # Break if city is found, no need to search further

    # Check for state (full name) in the title
    for state_name in us_states.values():
        if re.search(rf'\b{re.escape(state_name.lower())}\b', title_cleaned):
            detected_state = state_name
            print(f"Found state: {detected_state} in title")
            break  # Break if state is found, no need to search further

    # Check for state abbreviation in the title (case-insensitive)
    for abbr, name in us_states.items():
        if re.search(rf'\b{re.escape(abbr.lower())}\b', title_cleaned, re.IGNORECASE):
            detected_state = name
            print(f"Found state abbreviation: {abbr.upper()} (state: {name}) in title")
            break  # Break if state abbreviation is found, no need to search further

    return detected_city, detected_state

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
        close = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "wscrOk2")))
        close.click()
    except Exception as e:
        print(f"Alert close button not found: {e}")

    try:
        location_section = wait.until(
            EC.presence_of_element_located((By.ID, "country-toggle")))
        actions = ActionChains(driver)
        actions.move_to_element(location_section).perform()

        checkbox = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='checkbox'][data-display='United States']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(2)
    except Exception as e:
        print(f"Error locating or clicking checkbox: {e}")

    try:
        wait.until(EC.presence_of_element_located((By.ID, "applied-filters")))
    except Exception as e:
        print(f"Filters not applied, retrying: {e}")
        location_section = wait.until(
            EC.presence_of_element_located((By.ID, "country-toggle")))
        actions = ActionChains(driver)
        actions.move_to_element(location_section).perform()
        checkbox = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='checkbox'][data-display='United States']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(2)

    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "search-results-list")))
        job_links = results.find_elements(By.CSS_SELECTOR, "ul > li > a")
        for link in job_links:
            job_url = link.get_attribute("href")
            if job_url and job_url not in JOBS:
                JOBS.append(job_url)
        try:
            next_button = driver.find_element(By.CLASS_NAME, "next")
            if 'disabled' in next_button.get_attribute('class'):
                print('No more pages')
                break
            else:
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", next_button)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "next")))
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
        except Exception as e:
            print(f"No next button found or error clicking it: {e}")
            break
    print(f"Found {len(JOBS)} jobs")
    return JOBS


def filter_job_title(job_title):
    valid_titles = [
        "Pharmaceutical Sales Specialist",
        "Pharmaceutical Sales Representative",
        "Respiratory Specialty Sales Specialist",
        "District Sales Manager",
        "Respiratory Biologics Sales Specialist",
        "Oncology Account Specialist",
        "Regional Account Manager",
        "National Oncology Account Director",
    ]
    job_title_lower = job_title.lower()
    for valid_title in valid_titles:
        if valid_title.lower() in job_title_lower:
            return True
    return False


def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find('meta', {'name': 'gtm_tbcn_jobtitle'})
            jobTitle = title_meta['content'] if title_meta else ''

            # Filter job titles here
            if not filter_job_title(jobTitle):
                continue

            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify()

            cities = []
            states = []

            location_meta = soup.find('meta', {'name': 'gtm_tbcn_location'})
            location_content = location_meta['content'] if location_meta else ''
            location_parts = location_content.split('|')
            us_locations = []

            for part in location_parts:
                parts = part.split('~')
                if len(parts) == 3 and parts[2] == 'United States':
                    us_locations.append(part)
                    cities.append(parts[0])
                    states.append(parts[1])

            Location = ' | '.join(us_locations)
            city = ', '.join(cities) if cities else ''
            state = ', '.join(states) if states else ''
            city_title, state_title = find_city_state_in_title(jobTitle)
            print('city', city_title, state_title)
            if city_title:
                city = city_title
            if state_title:
                state = state_title
            country = 'United States'
            Zipcode = ''

            posting_date_meta = soup.find('meta', {'name': 'gtm_firstindex'})
            date_posted = posting_date_meta['content'] if posting_date_meta else ''
            job_id_meta = soup.find('meta', {'name': 'gtm_reqid'})
            job_id = job_id_meta['content'] if job_id_meta else jobs.index(job)

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
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
                "Employer Email": "msh@mshastrazeneca.com",
                "Full Name": "",
                "Company Name": "AstraZeneca",
                "Employer Website": "https://careers.astrazeneca.com",
                "Employer Phone": "",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/7684/v2_0/img/icons/az-logo.svg",
                "Company Description": "We are AstraZeneca, one of the world’s most forward-thinking and connected BioPharmaceutical companies. With a strong purpose, an even stronger bond between each of our people and a science-led, patient-first attitude, we’re changing the future of medicine and the impact it can have on lives across the globe.",
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
        url = "https://careers.astrazeneca.com/search-jobs/sales/7684/1?glat=40.44062&glon=-79.99589"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "AstraZeneca.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
