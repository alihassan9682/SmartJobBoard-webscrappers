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
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "widget-jobsearch-results-list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jobTitle"))
        )
        jobs = [
                job.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )
            for job in jobs
        ]
        print('total jobs', len(jobs))
        try:
            JOBS = JOBS + jobs
            print('HOBS', len(JOBS))
            next_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//li[@class='pagination-li']/a[@aria-label='Go to the next page of results.']"))
            )
            
            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
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
            desc_content = soup.find("div", class_="job-description-details")
            jobDescription = desc_content.prettify() if desc_content else ""
            job_details_body = soup.find("div", class_="job-details-body")

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
            primary_location_meta = job_details_body.find("p", class_="job-location")
            if primary_location_meta:
                primary_location = primary_location_meta.text.split(": ")[-1].strip()
                Location = primary_location

            # Extract additional locations
            additional_locations_meta = job_details_body.find("p", class_="job-addtnl-location")
            if additional_locations_meta:
                additional_locations_lists = additional_locations_meta.find_next_siblings("ul", class_="add-loc-list")
                for loc_list in additional_locations_lists:
                    loc_items = loc_list.find_all("ul", class_="add-loc-list")
                    for loc in loc_items:
                        additional_location = loc.text.strip()
                        if additional_location:
                            additional_locations.append(additional_location)

            # Combine primary and additional locations
            all_locations = [primary_location] + additional_locations if primary_location else additional_locations

            # Separate the details into Location, City, State, Country
            if all_locations:
                Location = ', '.join(all_locations)
                City = ', '.join([loc.split(', ')[0] for loc in all_locations])
                state = ', '.join([loc.split(', ')[1] for loc in all_locations if len(loc.split(', ')) > 1])
                country = ', '.join([loc.split(', ')[-1] for loc in all_locations if len(loc.split(', ')) > 2])

            # Extract other details
            if job_details_body:
                # Date Posted
                date_posted_meta = job_details_body.find("p", string=lambda x: x and "Date posted:" in x)
                if date_posted_meta:
                    posted_date = date_posted_meta.text.split(": ")[-1].strip()

                # Job ID
                job_id_meta = job_details_body.find("p", string=lambda x: x and "Job ID:" in x)
                if job_id_meta:
                    job_id = job_id_meta.text.split(": ")[-1].strip()

                employee_type_meta = job_details_body.find("p", string=lambda x: x and "Employee type:" in x)
                job_type = employee_type_meta.text.split(": ")[-1].strip() if employee_type_meta else ""

                # Hidden elements
                city_meta = job_details_body.find("p", class_="job-city hide")
                City = city_meta.text.strip() if city_meta else City

                state_meta = job_details_body.find("p", class_="job-state hide")
                state = state_meta.text.strip() if state_meta else state

                country_meta = job_details_body.find("p", class_="job-country hide")
                country = country_meta.text.strip() if country_meta else country

                address_meta = job_details_body.find("p", class_="job-address hide")
                Address = address_meta.text.strip() if address_meta else Location

            # Extract salary details
            salary_meta = soup.find("span", class_="job-salary-range job-info")
            if salary_meta and "-" in salary_meta.text:
                salary_range = salary_meta.text.split(" - ")
                from_salary = salary_range[0].strip()
                to_salary = salary_range[1].strip()

            # Construct job details dictionary
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
                "Address": Address,
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
                "Employer Logo": "",
                "Company Description": "",
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
        url = "https://careers.stryker.com/job-search-results/?keyword=Sales%20Representative&fuzzy=false&location=United%20States&country=US&radius=25"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Stryker.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
