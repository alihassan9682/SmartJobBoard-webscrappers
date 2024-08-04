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
    time.sleep(2)
    
    checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "facet_department"))
        )

    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    time.sleep(1)

    driver.execute_script("arguments[0].click();", checkbox)
    
    sales_checkbox = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-filter-value='Sales']"))
    )

    # driver.execute_script("arguments[0].scrollIntoView(true);", sales_checkbox)
    # time.sleep(1)

    driver.execute_script("arguments[0].click();", sales_checkbox)
    time.sleep(2)
    results = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "srJobList")
    ))
    WebDriverWait(results, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "srJobListJobEven"))
    )
    job_rows_even = driver.find_elements(By.CLASS_NAME, "srJobListJobEven")
    job_rows_odd = driver.find_elements(By.CLASS_NAME, "srJobListJobOdd")
    job_rows = job_rows_even + job_rows_odd

    for row in job_rows:
        onclick_attr = row.get_attribute("onclick")
        if onclick_attr:
            url_start = onclick_attr.find("window.open(&quot;") + len("window.open(&quot;")
            url_end = onclick_attr.find("&quot;);")
            job_url = onclick_attr[url_start:url_end]
            job_url = job_url.replace('"', '')
            if not job_url.startswith("https://"):
                job_url = "http" + job_url
            JOBS.append(job_url)
    

    return JOBS

def getJobs(driver):
    JOBS = []
    time.sleep(1)
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find("h1", class_="job-title")
            jobTitle = title_meta.text if title_meta else ''
            desc_content = soup.find('div', {'itemprop': 'description'})
            jobDescription = desc_content.prettify() if desc_content else ''
            job_details = {}
            job_location = soup.find('span', {'class': 'job-detail', 'itemprop': 'address'})
            if job_location:
                job_details['Formatted Address'] = job_location.find('spl-job-location').get('formattedaddress')
                job_details['Workplace Description'] = job_location.find('spl-job-location').get('workplacedescription')
            employment_type = soup.find('li', {'class': 'job-detail', 'itemprop': 'employmentType'})
            if employment_type:
                job_details['Employment Type'] = employment_type.text
            date_posted = soup.find('meta', {'itemprop': 'datePosted'})
            if date_posted:
                job_details['Date Posted'] = date_posted.get('content')

            location_meta = job_details.get('Formatted Address', '')
            Location = location_meta if location_meta else ''
            City = state = ''
            country = 'United States'
            if Location:
                location_parts = Location.split(',')
                if len(location_parts) == 3:
                    City = location_parts[0].strip()
                    state = location_parts[1].strip()
                elif len(location_parts) == 2:
                    City = location_parts[0].strip()
                    state = location_parts[1].strip()
                else:
                    City = state = ''

            Zipcode = ''
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_details.get('Employment Type',''),
                "Categories": "Diagnostic",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": True if 'Remotely' in job_details.get('Workplace Description','') else False,
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": job_details.get('Date Posted',''),
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshguardant.com",
                "Full Name": "",
                "Company Name": "Guardant",
                "Employer Website": " https://guardanthealth.com/",
                "Employer Phone": "",
                "Employer Logo": "https://guardanthealth.com/wp-content/uploads/GUARDANT_LOGO_RGB_2024.svg",
                "Company Description": "Guardant Health is a leading precision oncology company focused on helping conquer cancer globally through use of its proprietary tests, vast data sets and advanced analytics. The Guardant Health oncology platform leverages capabilities to drive commercial adoption, improve patient clinical outcomes and lower healthcare costs across all stages of the cancer care continuum. Guardant Health has commercially launched Guardant360®, Guardant360 CDx, Guardant360 TissueNext™, Guardant360 Response™, and GuardantOMNI® tests for advanced stage cancer patients, and Guardant Reveal™ for early-stage cancer patients. The Guardant Health screening portfolio, including the Shield™ test, aims to address the needs of individuals eligible for cancer screening",
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
        url = " https://guardanthealth.com/careers/jobs/"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Guardant.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
