import time

from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

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


def loadAllJobs(driver):
    JOBS = []
    wait = WebDriverWait(driver, 10)
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "job-results-container")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "mat-expansion-panel"))
        )
        jobs = [
                job.find_element(By.CLASS_NAME, "job-title-link").get_attribute(
                    "href"
                )
            for job in jobs
        ]
        try:
            JOBS = JOBS + jobs
            print('hahaha',len(JOBS))
            load_more_button = driver.find_element(By.CLASS_NAME, "mat-paginator-navigation-next")
            if 'mat-button-disabled' in load_more_button.get_attribute("class"):
                print("Next button is disabled. Exiting the loop.")
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "mat-paginator-navigation-next")))
            driver.execute_script("arguments[0].click();", load_more_button)
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
            jobTitle = driver.find_element(By.ID, "hero_title").text

            Location = driver.find_element(By.ID, "header-locations").text
            location_meta = Location.split(';')
            cities = [loc.strip().split(',')[0].strip() for loc in location_meta]
            states = [loc.strip().split(',')[1].strip() for loc in location_meta]
            
            City = ', '.join(cities) if cities else ''
            state = ', '.join(states) if states else ''
            country = 'United States'
            Zipcode = ''
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("section", class_="main-description-section")
            jobDescription = desc_content.prettify()

            job_id = driver.find_element(By.ID, "header-req_id").text
            jobDetails = {
                "Job Id": job_id,
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
                "Remote": is_remote(Location),
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
                "Employer Email": "msh@msggsk.com",
                "Full Name": "",
                "Company Name": "GSK",
                "Employer Website": "https://jobs.gsk.com/",
                "Employer Phone": "",
                "Employer Logo": "https://us.gsk.com/assets/img/gif_logo_opt.gif",
                "Company Description": "We are a focused biopharma company. We prevent and treat disease with vaccines, specialty and general medicines. We focus on the science of the immune system and ​advanced technologies, investing in four core ​therapeutic areas (infectious diseases, HIV, ​respiratory/immunology and oncology). Our ​Ahead Together strategy means intervening ​early to prevent and change the course of ​disease, helping to protect people and ​support healthcare systems.",
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
        url = " https://jobs.gsk.com/en-us/jobs?keywords=sales&location=united%20states&page=1"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "GSK.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
