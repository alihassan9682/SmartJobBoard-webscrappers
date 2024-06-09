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
    close = wait.until(
        EC.presence_of_element_located((By.ID, "igdpr-button"))
    )
    close.click()
    
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
        print('hihihi', len(jobs))
        try:
            JOBS = JOBS + jobs
            print('HOBS', len(JOBS))
            next_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "next"))
            )
            
            if next_button and 'disabled' not in next_button.get_attribute('class'):
                actions = ActionChains(driver)
                actions.move_to_element(next_button).click().perform()
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

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("section", class_="job-description")
            title_meta = desc_content.find("h1")
            jobTitle = title_meta.text if title_meta else ''
            desc_meta = desc_content.find("div", class_= "ats-description")
            jobDescription = desc_meta.prettify() if desc_meta else ''
            location_meta = soup.find("span", class_="job-location-info job-info")
            City = state = job_type = Location =''
            Location = location_meta.get_text(strip=True).replace("Location", "") if location_meta else ''
            job_meta = soup.find("span", class_="job-type-info job-info")
            job_type = job_meta.get_text(strip=True).replace("Employee type", "") if job_meta else ''
            country = 'United States'
            location_parts = Location.split(',') if Location else ''
            if len(location_parts) == 3 or len(location_parts) == 2:
                City = location_parts[0].strip()
                state = location_parts[1].strip()

            Zipcode = ''
            print("Job", job_type)
            print("Location", Location)
            print("Job Title", jobTitle)
            print("city", City)
            print("state", state)
            print("country", country)
            print('remote', is_remote(Location))
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Diagnostic",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": True if 'Remote' in jobTitle else False,
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
                "Employer Email": "msh@mshquest.com",
                "Full Name": "",
                "Company Name": "Quest",
                "Employer Website": "https://careers.questdiagnostics.com/",
                "Employer Phone": "",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/38852/gst-v1_0/img/logos/logo-quest-diagnostics.svg",
                "Company Description": "At Quest Diagnostics, our goal is to provide our customers exceptional service that builds long-term value into the future and promotes a healthier world. It’s not just caring for our customers that makes our workplace so inspiring. It’s our dedication to driving your career forward and taking care of the whole you. With opportunities to thrive, learn, and grow your career, you’ll discover more ways to transform professionally and personally than you ever thought possible.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://careers.questdiagnostics.com/search-jobs/sales/United%20States/38852/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Quest.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
