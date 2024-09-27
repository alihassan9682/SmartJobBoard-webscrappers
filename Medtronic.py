import time
from extractCityState import filter_job_title, find_city_state_in_title
from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
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


def get_location_details(location):
    parts = location.split(', ')
    city = state = country = ''

    if len(parts) == 3:
        city = parts[0].strip()
        state = parts[1].strip()
        country = parts[2].strip()
    elif len(parts) == 2:
        state = parts[0].strip()
        country = parts[1].strip()
    elif len(parts) == 1:
        country = parts[0].strip()

    return city, state, country


def loadAllJobs(driver):
    JOBS = []
    wait = WebDriverWait(driver, 10)

    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "css-8j5iuw")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "css-19uc56f"))
        )
        jobs = [
            job.get_attribute(
                "href"
            )
            for job in jobs
        ]

        try:
            JOBS = JOBS + jobs

            next_button = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-uxi-element-id='next']"))
            )
            if next_button:
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-uxi-element-id='next']")))
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
            else:
                
                break
        except:
            
            break
    return JOBS

def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    wait = WebDriverWait(driver, 10)
    for job in jobs:
        try:
            driver.get(job)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            job_meta = driver.find_element(By.CSS_SELECTOR, "[data-automation-id='jobPostingHeader']")
            jobTitle = job_meta.text if job_meta else ''
            if not filter_job_title(jobTitle):
                continue
            city_title, state_title = find_city_state_in_title(jobTitle)
            desc_content = soup.select_one("[data-automation-id='jobPostingDescription']")
            jobDescription = str(desc_content) if desc_content else ''

            job_details = soup.select_one("[data-automation-id='job-posting-details']")
            location_meta = job_details.select_one('div[data-automation-id="locations"] dd') if job_details else ''
            Location = location_meta.get_text() if location_meta else ''
            job_type_meta = job_details.select_one('div[data-automation-id="time"] dd') if job_details else ''
            job_id_meta = job_details.select_one('div[data-automation-id="requisitionId"] dd') if job_details else ''
            date_posted_meta = job_details.select_one('div[data-automation-id="postedOn"] dd') if job_details else ''
        
            job_id = job_id_meta.get_text() if job_id_meta else len(JOBS) + 1
            job_type = job_type_meta.get_text() if job_type_meta else ''
            date_posted = date_posted_meta.get_text() if date_posted_meta else ''
            City, state, country = get_location_details(Location)
            country = 'United States'

            if city_title:
                City = city_title
            if state_title:
                state = state_title
            
            from extract_location import extracting_location
            Location = extracting_location(City,state)

            Zipcode = ''

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Medical Device",
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
                "Posting Date": date_posted,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshmedtronic.com",
                "Full Name": "",
                "Company Name": "Medtronic",
                "Employer Website": "https://medtronic.eightfold.ai",
                "Employer Phone": "",
                "Employer Logo": "https://static.vscdn.net/images/careers/demo/medtronic-sandbox/main_logo_tagline",
                "Company Description": "As we engineer breakthrough medical discoveries, we develop new ways to enable the world to access them. Diversity fuels the innovation behind our life-saving technologies.",
                "Status": "Active",
            }
            JOBS.append(jobDetails)

        except StaleElementReferenceException as e:
            
            continue
        except Exception as e:
            pass
    return JOBS

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://medtronic.wd1.myworkdayjobs.com/MedtronicCareers?locationCountry=bc33aa3152ec42d4995f4791a106ed09&jobFamilyGroup=3b9e5dd261944d18b3f8d166e2c447bc"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Medtronic.csv")
        except Exception as e:
            pass
    except Exception as e:
        pass


scraping()
