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
    close = wait.until(
        EC.presence_of_element_located((By.ID, "gdpr-button"))
    )
    close.click()
    
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "search-results-list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "search-results-list-item"))
        )
        jobs = [
                job.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )
            for job in jobs
        ]

        try:
            JOBS = JOBS + jobs

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
            job_meta = driver.find_element(By.CLASS_NAME, "search-title")
            jobTitle = job_meta.text if job_meta else ''
            if not filter_job_title(jobTitle):
                continue
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify()
            job_id = soup.find("span", class_="job-id job-info").text.replace("Job ID ", "").strip() if soup.find("span", class_="job-id job-info") else ""
            posted_date = soup.find("span", class_="job-date job-info").text.replace("Date posted", "").strip() if soup.find("span", class_="job-date job-info") else ""

            City = state = ''
            country = 'Unites States'
            city_title, state_title = find_city_state_in_title(jobTitle)
            if city_title:
                City = city_title
            if state_title:
                state = state_title
            Zipcode = ''

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Medical Device",
                "Location": '',
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": country,
                "Remote": '',
                "Salary From": '',
                "Salary To": '',
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": posted_date,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshbectondickson.com",
                "Full Name": "",
                "Company Name": "Becton Dickson",
                "Employer Website": "https://jobs.bd.com/",
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
        url = "https://jobs.bd.com/search-jobs/sales/United%20States/159/1/2/6252001/39x76/-98x5/0/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Becton.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
