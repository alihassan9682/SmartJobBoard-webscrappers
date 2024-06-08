import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import os

from helpers import configure_webdriver, is_remote  

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
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ph-at-id='cookie-close-link']"))
    )
    close.click()

    location_section = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[id='CountryAccordion']"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(location_section).perform()

    checkbox = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox'][data-ph-at-text='United States of America']"))
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    time.sleep(1)

    driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(2)

    while True:
            results = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-ph-at-id='jobs-list']")
            ))
            jobs = WebDriverWait(results, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "jobs-list-item"))
            )
            jobs = [
                    job.find_element(By.CSS_SELECTOR, "a[data-ph-at-id='job-link']").get_attribute(
                        "href"
                    )
                for job in jobs
            ]
            try:
                JOBS = JOBS + jobs
                print('total', len(JOBS))
                next = driver.find_element(
                    By.CSS_SELECTOR, "[data-ph-at-id='pagination-next-link']"
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
            driver.get(job)
            time.sleep(2)
            job_meta = driver.find_element(By.CLASS_NAME, "job-title")
            jobTitle = job_meta.text if job_meta else ''
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="jd-info")
            jobDescription = desc_content.prettify() if desc_content else ''
            location = city = state = ''
            country = 'United States of America'
            location_meta = soup.find('span', class_='au-target job-location')
            if location_meta:
                location = location_meta.get_text(strip=True)
                location_parts = location.split(',') if location else ''
                if len(location_parts) == 3:
                    city = location_parts[0].strip()
                    state = location_parts[1].strip()
                    country = location_parts[2].strip()
                else:
                    city = state = ''
                    country = 'United States of America'
            try:
                mul_location = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "see-multiple-loc-btn"))
                )
                if mul_location:
                    mul_location.click()
                    locations_meta = driver.find_elements(By.XPATH, "//span[@data-ph-id='ph-page-element-page8-t4HcBr']")
                    locations = [loc.text.strip() for loc in locations_meta if "United States of America" in loc.text]
                    if locations:
                        location = ', '.join(locations)
                        city = ', '.join([loc.split(',')[0].strip() for loc in locations if loc[0]])
                        print('city', city)
                        state = ', '.join([loc.split(',')[1].strip() for loc in locations if loc[1]])
                        country = 'United States of America'
                else:
                    print('issue with the location')
            except:
                pass
            print('location', location)
            print('city',city)
            print('state', state)
            Zipcode = ''
            date_posted = soup.find('div', class_='job-info au-target')['data-ph-at-job-post-date-text']
            job_type = soup.find('div', class_='job-info au-target')['data-ph-at-job-type-text']
            job_id = soup.find('span', class_='au-target jobId').get_text(strip=True).replace("Job Id","")

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type if job_type else '',
                "Categories": "Diagnostics",
                "Location": location,
                "City": city,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": location,
                "Remote": is_remote(location),
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": date_posted,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshthermofisher.com",
                "Full Name": "",
                "Company Name": "Thermo Fisher",
                "Employer Website": "https://jobs.thermofisher.com/",
                "Employer Phone": "",
                "Employer Logo": "https://cdn.phenompeople.com/CareerConnectResources/TFSCGLOBAL/en_global/desktop/assets/images/header_logo.png",
                "Company Description": "Thermo Fisher Scientific Inc. is the world leader in serving science, with annual revenue of more than $40 billion. Our Mission is to enable our customers to make the world healthier, cleaner and safer. Whether our customers are accelerating life sciences research, solving complex analytical challenges, increasing productivity in their laboratories, improving patient health through diagnostics or the development and manufacture of life-changing therapies, we are here to support them",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://jobs.thermofisher.com/global/en/search-results?m=3&keywords=sales"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "ThermoFisher.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
