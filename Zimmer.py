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
        EC.presence_of_element_located((By.ID, "CountryAccordion"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(location_section).perform()

    checkbox = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox'][data-ph-at-text='United States']"))
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
                next = driver.find_element(
                    By.CSS_SELECTOR, "[aria-label='View next page']"
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
            jobTitle = driver.find_element(By.CLASS_NAME, "job-title").text
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="jd-info")
            jobDescription = desc_content.prettify()
            location_meta = soup.find('span', class_='au-target job-location')
            try:
                mul_location_btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "see-multiple-loc-btn"))
                )
            except:
                pass
            if location_meta:
                location = location_meta.get_text(strip=True).replace("Location", "") if location_meta else ''
                location_parts = location.split(',') if location else ''
                if len(location_parts) == 3:
                    city = location_parts[0].strip()
                    state = location_parts[1].strip()
                    country = location_parts[2].strip()
                else:
                    city = state = ''
                    country = 'United States'
            elif mul_location_btn:
                mul_location_btn.click()
                time.sleep(2)
                locations_meta = driver.find_elements(By.XPATH, "//span[@data-ph-id='ph-page-element-page2-taoCkK']")
                locations = [loc.text.strip() for loc in locations_meta if "United States" in loc.text]
                if locations:
                    location = ', '.join(locations)
                    city = ', '.join([loc.split(',')[0].strip() for loc in locations])
                    state = ', '.join([loc.split(',')[1].strip() for loc in locations])
                    country = 'United States'
                else:
                    city = state = ''
                    country = 'United States'
            else:
                print('issue with the location')
            Zipcode = ''
            date_posted = soup.find('div', class_='job-info au-target')['data-ph-at-job-post-date-text']
            info_div = soup.find('div', class_='job-info au-target')
            job_id = info_div.find('span', class_='au-target reqId').get_text(strip=True).replace("Job #","")

            jobDetails = {
                "Job Id": job_id if job_id else jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": "",
                "Categories": "Pharmaceuticals",
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
                "Posting Date": date_posted if date_posted else '',
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshzimmer.com",
                "Full Name": "",
                "Company Name": "Zimmer",
                "Employer Website": "https://careers.zimmerbiomet.com/",
                "Employer Phone": "",
                "Employer Logo": "https://cdn.phenompeople.com/CareerConnectResources/ZBUZBRUS/images/svgexport-2-1683122671945.svg",
                "Company Description": "At Zimmer Biomet, we have a shared commitment to our patients, customers and one another.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://careers.zimmerbiomet.com/us/en/search-results?keywords=sales"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Zimmer.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
