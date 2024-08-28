import time

from extractCityState import filter_job_title, find_city_state_in_title
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
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "results-list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "results-list__item-title"))
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
                    (By.CLASS_NAME, "page-link-next"))
            )
            if next_button:
                check_disabled = next_button.get_attribute("aria-disabled")
                if check_disabled == "false":
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
                else:
                    print('No more next button')
                    break
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
            job_meta = driver.find_element(By.ID, "job-title")
            jobTitle = job_meta.text if job_meta else ''
            if not filter_job_title(jobTitle):
                continue
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="description")
            jobDescription = desc_content.prettify() if desc_content else ""
            # Initialize fields
            Location = City = state = ''
            country = 'US'
            additional_locations = []
            job_type = ''
            salary_range = ''
            posted_date = ''
            Zipcode = ''
            job_id = ''
            from_salary = ''
            to_salary = ''

            # Extract primary location
            primary_location_meta = soup.find(
                "div", class_="job-locations-parsed")

            # Extract additional locations
            if primary_location_meta:
                loc_items = primary_location_meta.find_all("li")
                for loc_list in loc_items:
                        additional_location = loc_list.text.strip()
                        if additional_location:
                            additional_locations.append(additional_location)

            # Separate the details into Location, City, State, Country
            if additional_locations:
                Location = ', '.join(additional_locations)
                City = ', '.join([loc.split(', ')[0]
                                 for loc in additional_locations])
                state = ', '.join(
                    [loc.split(', ')[1] for loc in additional_locations if len(loc.split(', ')) > 1])
                country = ', '.join(
                    [loc.split(', ')[-1] for loc in additional_locations if len(loc.split(', ')) > 2])

            city_title, state_title = find_city_state_in_title(jobTitle)
            if city_title:
                City = city_title
            if state_title:
                state = state_title
            Location = City + ', ' + state + ', ' + 'USA'
            # Construct job details dictionary
            jobDetails = {
                "Job Id": job_id if job_id else jobs.index(job),
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
                "Salary From": from_salary,
                "Salary To": to_salary,
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": posted_date,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshstryker.com",
                "Full Name": "",
                "Company Name": "Stryker",
                "Employer Website": "https://careers.stryker.com/",
                "Employer Phone": "",
                "Employer Logo": "https://d25zu39ynyitwy.cloudfront.net/oms/000000/image/2024/5/LFSKF_logo/logo_-1x-1.png",
                "Company Description": "Stryker is one of the world's leading medical technology companies. Alongside our customers around the world, we impact more than 150 million patients annually.",
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
        url = "https://careers.stryker.com/jobs?keyword=Sales&location_name=United%20States&location_type=4"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Stryker.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
