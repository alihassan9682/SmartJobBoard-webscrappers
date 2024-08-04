import time

from helpers import configure_webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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

def extract_location_details(location_string):
    remote_status = False
    cities = ""
    states = ""
    country = ""

    locations = [location.strip() for location in location_string.split('/')]

    for loc in locations:
        if loc.startswith("Remote - "):
            remote_status = True
            loc = loc[len("Remote - "):]

        parts = loc.split(',')
        if len(parts) >= 3:
            city = parts[0].strip()
            state = parts[1].strip()
            country = parts[2].strip()
        elif len(parts) == 2:
            city = parts[0].strip()
            state = parts[1].strip()
            country = "United States of America"
        else:
            city = state = country = ''

        cities += city + ", "
        states += state + ", "

    cities = cities.rstrip(", ")
    states = states.rstrip(", ")

    return str(remote_status), cities, states, country

def loadAllJobs(driver):
    JOBS = []
    wait = WebDriverWait(driver, 10)
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "js-job-search-results")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "card-job"))
        )
        jobs = [
            job.find_element(By.CLASS_NAME, "js-view-job").get_attribute(
                "href"
            )
            for job in jobs
            ]
        try:
            JOBS = JOBS + jobs
            next = driver.find_element(
                By.CSS_SELECTOR, "[aria-label='Next page']"
            ).get_attribute("href")
            driver.get(next)
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
            jobTitle = driver.find_element(By.CLASS_NAME, "hero-heading").text
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("article", class_="cms-content")
            sidebar = desc_content.find("div", class_="job-sidebar")
            if (sidebar):
                sidebar.decompose()
            jobDescription = desc_content.prettify()

            job_meta = soup.find('ul', class_='job-meta')

            function_li = job_meta.find_all('li')
            print('function lis', function_li[0].text.strip(), function_li[2].text.strip())
            remote_status, cities, states, Country = extract_location_details(function_li[0].text.strip())
            Location = function_li[0].text.strip()
            City = cities
            state = states
            country = Country
            Zipcode = ''

            jobDetails = {
                "Job Id": function_li[2].text.strip(),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": 'Remote' if remote_status == 'True' else '',
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": remote_status,
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
                "Employer Email": "candidatesupport@regeneron.com",
                "Full Name": "",
                "Company Name": "Regeneron",
                "Employer Website": "https://www.regeneron.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "Our commitment to patients extends well beyond our labs. We are proud to support the communities we serve, to embrace a culture and business model of patients over profits and to hold the highest ethical standards when it comes to patient well-being.",
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
        url = "https://careers.regeneron.com/en/jobs/?keyword=sales&country=United+States+of+America&pagesize=20#results"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Regeneron.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
