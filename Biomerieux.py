import time
import random
from helpers import configure_undetected_chrome_driver, configure_webdriver, is_remote
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
        EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))
    )
    close.click()
    time.sleep(2)
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "jobs-section__list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jobs-section__item"))
        )
        jobs = [
                job.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )
            for job in jobs
        ]

        try:
            JOBS = JOBS + jobs

            time.sleep(3)
            next_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "next_page"))
            )
            
            if next_button and 'disabled' not in next_button.get_attribute('class'):
                actions = ActionChains(driver)
                actions.move_to_element(next_button).click().perform()
                time.sleep(random.uniform(2, 5))
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
            time.sleep(random.uniform(2, 5))

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="job-details__main")
            title_meta = desc_content.find("h1")
            jobTitle = title_meta.text if title_meta else ''
            desc_meta = desc_content.find_all("div", class_= "page-section-medium")
            target_div = next((div for div in desc_meta if div.find('p') and div.find('p').text.strip() == 'Description'), None)
            if target_div:
                for span in target_div.find_all("span"):
                    span.unwrap()  # Remove the <span> tags but keep their text
                for tag in target_div.find_all(True):
                    tag.attrs = {}  # Remove all attributes from all tags
                jobDescription = target_div.prettify(formatter="html")
            else:
                jobDescription = ''
            City = state = job_type = Location =''
            country = 'United States'
            Zipcode = ''

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
                "Employer Email": "msh@mshbiomerieux.com",
                "Full Name": "",
                "Company Name": "Biomerieux",
                "Employer Website": "https://careers.biomerieux.com/",
                "Employer Phone": "",
                "Employer Logo": "https://careers.biomerieux.com/system/production/assets/264009/original/BioMerieux_logo.svg?s=88b891f56bb5e320",
                "Company Description": "Choosing bioMérieux means joining a people-centered, stimulating work environment where teams unleash their full potential and are empowered to dare change the game for public health.",
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
        url = " https://careers.biomerieux.com/search/jobs/in/country/united-states?q=sales"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Biomerieux.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
