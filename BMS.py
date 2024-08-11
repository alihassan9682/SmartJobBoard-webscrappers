import time

from extractCityState import find_city_state_in_title
from helpers import configure_webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
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

def filter_job_title(job_title):
    valid_titles = [
        "Therapeutic Area Specialist",
        "Manager of Regional Operations",
    ]
    for valid_title in valid_titles:
        if valid_title.lower() in job_title.lower():
            return True
    return False

def loadAllJobs(driver):
    JOBS = []
    unique_jobs = set()
    wait = WebDriverWait(driver, 10)
    last_processed_index = 0
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "position-cards-container")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-container"))
        )
        for index in range(last_processed_index, len(jobs)):
            job = jobs[index]
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", job)
                time.sleep(1)
                job.click()
                time.sleep(3)

                job_url = driver.current_url

                if job_url not in unique_jobs:
                    unique_jobs.add(job_url)
                    JOBS.append(job_url)
    
            except Exception as e:
                print(f"Error processing job card: {e}")

        last_processed_index = len(jobs)
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "show-more-positions")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "show-more-positions")))
            try:
                driver.execute_script("arguments[0].click();", load_more_button)
            except ElementClickInterceptedException:
                time.sleep(2)
                driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(2)
        except NoSuchElementException:
            print("No more 'Load More' button found, all jobs are loaded.")
            break
        except Exception as e:
            print(f"Error clicking load more button: {e}")
            break
    return JOBS


def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    wait = WebDriverWait(driver, 10)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2) 
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            job_meta = soup.find("h1", class_="position-title")
            jobTitle = job_meta.text if job_meta else ''
            if not filter_job_title(jobTitle):
                continue
            desc_content = soup.find("div", class_="position-job-description-column")
            jobDescription = desc_content.prettify()

            selected_card = soup.find("div", class_='card-selected')
            location_meta = selected_card.find("p",class_='field-label')
            print('llooo', location_meta)
            Location = location_meta.text if location_meta else ''

            state = City = ''
            if Location:
                location_parts = Location.split("-")
                City = location_parts[0] if location_parts[0] else ''
                state = location_parts[1] if len(location_parts) > 1 and location_parts[1] else ''
            country = 'United States'
            city_title, state_title = find_city_state_in_title(jobTitle)
            print('city', city_title, state_title)
            if city_title:
                City = city_title
            if state_title:
                state = state_title
            Zipcode = ''
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Pharmaceuticals",
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
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshbms.com",
                "Full Name": "",
                "Company Name": "BMS",
                "Employer Website": "https://jobs.bms.com/",
                "Employer Phone": "1-800-332-2056",
                "Employer Logo": "",
                "Company Description": "We are a global biopharmaceutical company whose mission is to discover, develop and deliver innovative medicines that help patients prevail over serious diseases.",
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
        url = "https://jobs.bms.com/careers?query=sales&location=Field%20-%20United%20States%20-%20US&pid=137461081507&domain=bms.com&sort_by=relevance&triggerGoButton=false&triggerGoButton=true"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "BMS.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
