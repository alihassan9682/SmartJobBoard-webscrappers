import time

from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

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
    wait = WebDriverWait(driver, 20)

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            results = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "container-fluid iCIMS_JobsTable")
            ))
        except TimeoutException:
            print("Timeout: The element with class 'container-fluid iCIMS_JobsTable' was not found within the specified timeout.")
        
        print("results", results)
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "row"))
        )
        print('Waiting for', results)
        jobs = [
            job.find_element(By.CLASS_NAME, "col-xs-12 title").find_element(By.TAG_NAME, 'a').get_attribute("href")
            for job in jobs
        ]
        try:
            JOBS = JOBS + jobs
            print('running jobs', len(JOBS))
            next_button = driver.find_elements(By.XPATH, ".//a[contains(@class, 'glyph')]")[-1]
            if 'invisible' in next_button.get_attribute('class'):
                break
            else:
                next = next_button.get_attribute("href")
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
            jobTitle = driver.find_element(By.CLASS_NAME, "iCIMS_Header").text
            Location = "United States"
            City = ''
            state = ''
            country = 'United States'
            Zipcode = ''

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="iCIMS_JobContent")
            first_para = desc_content.find("div", class_="container-fluid iCIMS_JobsTable")
            last_para = desc_content.find("div", class_="iCIMS_Logo")
            if (first_para):
                first_para.decompose()
            if (last_para):
                last_para.decompose()
            jobDescription = desc_content.prettify()

            additional_fields = soup.find('div', class_='col-xs-12 additionalFields')

            job_details = {}

            for tag in additional_fields.find_all('div', class_='iCIMS_JobHeaderTag'):
                field_name = tag.find('dt', class_='iCIMS_JobHeaderField').text.strip()
                field_value = tag.find('dd', class_='iCIMS_JobHeaderData').text.strip()
                job_details[field_name] = field_value

            for key, value in job_details.items():
                print(f"{key}: {value}")
            jobDetails = {
                "Job Id": job_details['Requisition ID'] if job_details['Requisition ID'] else jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_details['Position Type'] if job_details['Position Type'] else '',
                "Categories": "Medical Device",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": '',
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
                "Employer Email": "msh@mshbbraun.com",
                "Full Name": "",
                "Company Name": "B Braun",
                "Employer Website": " https://bbrauncareers-bbraun.icims.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "The B. Braun Group of Companies leads in thoughtful solutions that address real issues in patient care and clinician safety.  The global slogan, Sharing Expertise® fosters a teamwork approach to saving lives and solving the problems of the health care industry.  It is an ethical and purposeful work culture that welcomes innovation and rewards progress.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = " https://bbrauncareers-bbraun.icims.com/jobs/search?ss=1&searchKeyword=sales&searchRelation=keyword_all&searchLocation=12781--"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "BBraun.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
