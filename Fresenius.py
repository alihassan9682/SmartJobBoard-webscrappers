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

        results = wait.until(EC.presence_of_element_located(
            (By.ID, "search-results-list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
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
            next_button = driver.find_element(By.CLASS_NAME, "next")
            if next_button and 'disabled' not in next_button.get_attribute('class'):
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next")))
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            else:
                print('no more next button')
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
            job_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'intro'))
            )
            jobTitle = job_elements.find_element(By.TAG_NAME, 'h1').text
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify()

            cities = []
            states = []

            location_meta = soup.find('span', class_="loc")
            location_content = location_meta.text if location_meta else ''
            location_parts = location_content.split('|')
            locations = []

            for part in location_parts:
                parts = part.split(',')
                if len(parts) == 2:
                    locations.append(part)
                    cities.append(parts[0])
                    states.append(parts[1])

            Location = ' | '.join(locations)
            City = ', '.join(cities) if cities else ''
            state = ', '.join(states) if states else ''
            country = 'United States'
            Zipcode = ''
            
            job_id_meta = soup.find('span',class_='job-referencee job-info')
            job_id = job_id_meta.text.replace("Job ID", "").strip() if job_id_meta else jobs.index(job)

            print("Location", Location)
            print("Job Id", job_id)
            print("Job Title", jobTitle)
            print("city", City)
            print("state", state)
            print("country", country)
            print('remote', is_remote(jobTitle))
            jobDetails = {
                "Job Id": job_id,
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
                "Remote": is_remote(Location),
                "Salary From": '',
                "Salary To": '',
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": '',
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshfresenius.com",
                "Full Name": "",
                "Company Name": "Fresenius",
                "Employer Website": " https://jobs.fmcna.com/",
                "Employer Phone": "",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/488/full_v1_0-gst/img/logo-blue-0033a0.png",
                "Company Description": "We're the largest provider of renal care products and services in the nation, including state-of-the-art dialysis machines, dialyzers and pharmaceuticals, and we are home to the country's largest renal specialty laboratories. We supply unsurpassed personalized dialysis care services including hemodialysis, home dialysis and transplant support services, and in-center services.",
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
        url = "https://jobs.fmcna.com/search-jobs/sales/United%20States/488/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Fresenius.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
