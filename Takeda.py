import time

from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
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
    unique_jobs = set()
    wait = WebDriverWait(driver, 10)
    close = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "banner-close-button"))
    )
    close.click()
    while True:
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "search-results-list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
        )
        jobs = results.find_elements(By.TAG_NAME, "li")
        jobs = [
            job.find_element(By.TAG_NAME, "a").get_attribute("href")
            for job in jobs
        ]

        try:
            for job in jobs:
                if job not in unique_jobs:
                    unique_jobs.add(job)
                    JOBS.append(job)
            show_all_button = driver.find_element(By.CLASS_NAME, "pagination-show-all")
            driver.execute_script("arguments[0].scrollIntoView(true);", show_all_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "pagination-show-all")))
            driver.execute_script("arguments[0].click();", show_all_button)
            time.sleep(2)
        except NoSuchElementException:
            print("No more 'Show all' button found, all jobs are loaded.")
            break
        except Exception as e:
            print(f"Error clicking Show all button: {e}")
            break
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
            jobTitle = driver.find_element(By.CLASS_NAME, "ajd_header__job-title").text
            job_id = driver.find_element(By.CLASS_NAME, "job-id").text
            posting_date = driver.find_element(By.CLASS_NAME, "job-date").text
            Location = driver.find_element(By.CLASS_NAME, "job-location").text
            City = ''
            state = ''
            country = 'United States'
            Zipcode = ''

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ajd_job-details__ats-description")
            first_p = desc_content.find("p")
            
            if (first_p):
                first_p.decompose()
            jobDescription = desc_content.prettify()

            jobDetails = {
                "Job Id": job_id.split()[-1],
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Pharmaceuticals",
                "Location": Location.split()[-1],
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location.split()[-1],
                "Remote": True if Location.split()[-1] == 'Remote' else False,
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": posting_date.split()[-1],
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "N/A",
                "Full Name": "",
                "Company Name": "Takeda",
                "Employer Website": "https://jobs.takeda.com/",
                "Employer Phone": "+81-3-3278-2111",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/1113/gst_v2_0/img/logo.svg",
                "Company Description": "As Takeda employees, our decisions and actions can affect people’s lives. This is a noble purpose that demands the highest standards of ethical behavior. Every day, we draw on Takeda’s values and priorities of Patient-Trust-Reputation-Business to ensure we do what’s right – for our patients, each other and society – and remain true to Takeda’s mission.",
            }
            JOBS.append(jobDetails)
        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = " https://jobs.takeda.com/search-jobs/sales/United%20States/1113/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Takeda.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
