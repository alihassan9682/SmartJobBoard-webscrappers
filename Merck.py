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
    close = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "Close"))
    )
    close.click()
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "phs-facet-results-block")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jobs-list-item"))
        )
        jobs = [
            [
                job.find_element(By.CSS_SELECTOR, "[au-target-id='131']").get_attribute(
                    "href"
                ),
                job.find_element(By.CSS_SELECTOR, "[au-target-id='147']").text.split('\n')[-1],
            ]
            for job in jobs
        ]
        try:
            JOBS = JOBS + jobs
            next = driver.find_element(
                By.CSS_SELECTOR, "[au-target-id='241']"
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
            driver.get(job[0])
            time.sleep(2)
            jobTitle = driver.find_element(By.CLASS_NAME, "job-title").text
            Location = "United States"
            City = ''
            state = ''
            country = ''
            Zipcode = ''

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="jd-info")
            jobDescription = desc_content.prettify()

            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job[1],
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(job[1]),
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job[0],
                "Apply Email": "",
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshmerck.com",
                "Full Name": "",
                "Company Name": "Merck",
                "Employer Website": "https://www.merck.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "We’re a global health care company working to deliver innovative health solutions through our medicines, vaccines, biologic therapies and animal health products. We’re focused on discovering new solutions for today and the future.",
                "Status": "Active",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(False)
        driver.maximize_window()
        url = "https://jobs.merck.com/us/en/search-results?keywords=sales"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Merck.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
