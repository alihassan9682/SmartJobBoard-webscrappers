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
    current_page = 1

    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "attrax-list-widget__list")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "attrax-vacancy-tile__title"))
        )
        jobs = [
            job.get_attribute("href")
            for job in jobs
        ]

        try:
            for job in jobs:
                if job not in unique_jobs:
                    unique_jobs.add(job)
                    JOBS.append(job)
            print('hihihi', len(JOBS))
            next_page_number = current_page + 1
            next_page_elements = driver.find_elements(By.CSS_SELECTOR, f"a[href='javascript:pagination({next_page_number})']")
            
            if not next_page_elements:
                print("No next page element found. Exiting the loop.")
                break
            
            next_page_element = next_page_elements[0]
            driver.execute_script("arguments[0].scrollIntoView(true);", next_page_element)
            driver.execute_script("arguments[0].click();", next_page_element)
            
            current_page += 1
            time.sleep(2)
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
            jobTitle = driver.find_element(By.ID, "headertext").text
            job_id = driver.find_element(By.CSS_SELECTOR, "[data-type='IdWidget']").find_element(By.TAG_NAME, "span").text
            job_type = driver.find_element(By.CLASS_NAME, "JobType-wrapper").text.strip()
            Location = driver.find_element(By.CLASS_NAME, "attrax-job-information-widget__freetext-field-value").text
            if ',' in Location:
                City, state = Location.split(',', 1)
                City = City.strip()
                state = state.strip()
            else:
                City = state = ''

            country = 'United States'
            Zipcode = ''

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", attrs={"data-type":"DescriptionWidget"})

            salary_range = soup.find("div", attrs={"data-type":"SalaryWidget"}).find_all('span')[1].text.strip()
            from_salary = to_salary = ''
            if salary_range and '-' in salary_range:
                from_salary, to_salary = salary_range.split('-', 1)
                from_salary = from_salary.strip()
                to_salary = to_salary.strip()

            print('salary_range', from_salary, to_salary)
            print('loc',Location)
            print('job_type',job_type)
            print('job_id',job_id)
            print('jobTitle',jobTitle)
            print('desc_content',desc_content)
            print('salary_range',salary_range)
            print('City',City)
            print('state',state)

            jobDescription = desc_content.prettify()

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(Location),
                "Salary From": from_salary,
                "Salary To": to_salary,
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": '',
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshabbvie.com",
                "Full Name": "",
                "Company Name": "Abbvie",
                "Employer Website": "https://careers.abbvie.com/",
                "Employer Phone": "",
                "Employer Logo": "https://attraxcdnprod1-freshed3dgayb7c3.z01.azurefd.net/1481171/538548f1-243c-40ff-96ed-610a25cc1a3f/2023.17000.1938/Blob/img/logo.svg",
                "Company Description": "AbbVie discovers and delivers innovative medicines and solutions that enhance people’s lives.",
            }
            JOBS.append(jobDetails)
        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://careers.abbvie.com/en/jobs?q=sales&options=&page=1&la=&lo=&lr=100&ln=United%20States&li=US"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Abbvie.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
