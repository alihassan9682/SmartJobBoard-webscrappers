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
    location_parts = location.split(',')
    if len(location_parts) == 2:
        state_country = location_parts[1].strip()
        city_state = location_parts[0].strip().split(' ')
        if len(city_state) == 2:
            city = city_state[0].strip()
            state = city_state[1].strip()
        else:
            city = ''
            state = city_state[0].strip()
        country = state_country.split('-')[-1].strip()
    elif len(location_parts) == 1:
        state_country = location_parts[0].strip()
        city = ''
        state = state_country.split('-')[0].strip()
        country = state_country.split('-')[-1].strip()
    else:
        city = state = country = ''

    return city, state, country

def loadAllJobs(driver):
    JOBS = []
    unique_jobs = set()
    wait = WebDriverWait(driver, 10)
    last_processed_index = 0
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "position-cards-container")
        ))
        try:
            jobs = WebDriverWait(results, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "position-card")))
        except StaleElementReferenceException:
            print("StaleElementReferenceException occurred while locating job cards.")
            continue
        for index in range(last_processed_index, len(jobs)):
            job = jobs[index]
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", job)
                time.sleep(1)
                job.click()
                time.sleep(2)

                job_url = driver.current_url

                if job_url not in unique_jobs:
                    unique_jobs.add(job_url)
                    JOBS.append(job_url)
    
            except StaleElementReferenceException as e:
                print(f"StaleElementReferenceException encountered: {e}")
                time.sleep(1)
                break
            except Exception as e:
                print(f"Error processing job card: {e}")

        last_processed_index = len(jobs)
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "show-more-positions")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "show-more-positions")))
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
            jobDescription = desc_content.prettify() if desc_content else ''

            selected_card = soup.find("div", class_='card-selected')
            location_meta = selected_card.find("p",class_='position-location')
            Location_detail = location_meta.text if location_meta.text else ''
            Location =  Location_detail.split('and')[0] if 'and' in Location_detail else Location_detail

            City, state, country = get_location_details(Location_detail)
            city_title, state_title = find_city_state_in_title(jobTitle)
            if city_title:
                City = city_title
            if state_title:
                state = state_title

            country = 'United States'
            Zipcode = ''

            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Medical Device",
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
                "Employer Email": "msh@mshbostonscientific.com",
                "Full Name": "",
                "Company Name": "Boston Scientific",
                "Employer Website": "https://bostonscientific.eightfold.ai",
                "Employer Phone": "",
                "Employer Logo": "https://static.vscdn.net/images/careers/demo/bostonscientific-sandbox/1681242661::BSC_wtag_541blue_rgb.jpg",
                "Company Description": "Work. Life. Family. It can be a lot. We offer a variety of resources to support you in your every day life.",
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
        url = "https://bostonscientific.eightfold.ai/careers?query=sales%20&location=united%20states&pid=563602796281461&domain=bostonscientific.com&sort_by=relevance"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "bostonscientific.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
