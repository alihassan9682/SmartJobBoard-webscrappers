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
        EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
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
                    By.CLASS_NAME, "next-btn"
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
            location_meta = soup.find('span', class_='au-target cityStateCountry')
            try:
                mul_location = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ph-at-id='job-multi-locations-list']"))
                )
            except:
                pass
        
            if mul_location:
                locations_meta = driver.find_elements(By.XPATH, "//span[@data-ph-id='ph-page-element-page20-BapAAo']")
                locations = [loc.text.strip() for loc in locations_meta if "United States of America" in loc.text]
                if locations:
                    location = ', '.join(locations)
                    city = ', '.join([loc.split(',')[0].strip() for loc in locations if len(loc) == 3])
                    state = ', '.join([loc.split(',')[1].strip() for loc in locations if len(loc) == 3])
                    country = 'United States of America'
                else:
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
            else:
                print('issue with the location')
            Zipcode = ''
            date_posted = soup.find('div', class_='job-info au-target')['data-ph-at-job-post-date-text']
            job_type = soup.find('div', class_='job-info au-target')['data-ph-at-job-type-text']
            job_id = soup.find('span', class_='au-target jobId').get_text(strip=True).replace("Job Id","")

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type if job_type else '',
                "Categories": "Medical Device",
                "Location": location,
                "City": city,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": location,
                "Remote": "",
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
                "Employer Email": "msh@mshdanaher.com",
                "Full Name": "",
                "Company Name": "Danaher",
                "Employer Website": " https://jobs.danaher.com/",
                "Employer Phone": "",
                "Employer Logo": "https://cdn.phenompeople.com/CareerConnectResources/DANAGLOBAL/images/Danaher_logo_h_tm_rgb-1696293771671.png",
                "Company Description": "We’re Danaher - a leading global life sciences and diagnostics innovator, committed to accelerating the power of science and technology to improve human health.",
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
        url = " https://jobs.danaher.com/global/en/search-results?keywords=sales"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Danaher.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
