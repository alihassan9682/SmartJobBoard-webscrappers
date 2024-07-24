import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
)
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
    last_processed_index = 0

    try:
        # Handle the cookie consent
        close = wait.until(EC.presence_of_element_located((By.ID, "usercentrics-root")))
        shadow_root_script = "return arguments[0].shadowRoot"
        shadow_root = driver.execute_script(shadow_root_script, close)
        if shadow_root:
            deny_button = shadow_root.find_element(By.CSS_SELECTOR, '[data-testid="uc-deny-all-button"]')
            deny_button.click()
        else:
            print("Shadow root not found.")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")

    time.sleep(2)

    try:
        keyword = wait.until(EC.presence_of_element_located((By.ID, "Keyword")))
        keyword.send_keys("sales")
        time.sleep(1)
        keyword_country = wait.until(EC.presence_of_element_located((By.ID, "geolocation_value")))
        keyword_country.send_keys("United States")
        time.sleep(2)

        search_button = driver.find_element(By.ID, "Search")
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(3)
    except Exception as e:
        print(f"Error during initial search setup: {e}")

    while True:
        try:
            results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job-results")))
            jobs = WebDriverWait(results, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jtable-data-row")))

            for index in range(last_processed_index, len(jobs)):
                job = jobs[index]
                try:
                    job_link = job.get_attribute("data-href")
                    JOBS.append(job_link)
                except StaleElementReferenceException as e:
                    print(f"StaleElementReferenceException encountered: {e}")
                    time.sleep(1)
                    break
                except Exception as e:
                    print(f"Error processing job card: {e}")

            last_processed_index = len(jobs)

            try:
                load_more_button = driver.find_element(By.CLASS_NAME, "jtable-page-number-next")
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "jtable-page-number-next")))
                try:
                    driver.execute_script("arguments[0].click();", load_more_button)
                except ElementClickInterceptedException:
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(2)
            except NoSuchElementException:
                print("No more 'Load More' button found, all jobs are loaded.")
                break
            except Exception as e:
                print(f"Error clicking load more button: {e}")
                break

        except Exception as e:
            print(f"Error during job loading or pagination: {e}")
            break

    return JOBS

def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find('meta', {'property': 'og:title'})
            jobTitle = title_meta['content'] if title_meta else ''
            desc_content = soup.find("div", class_="Description")
            desc = desc_content.find("div", class_="Apply Bottom") if desc_content else None
            if desc:
                desc.decompose()
            jobDescription = desc_content.prettify() if desc_content else ''

            job_details = {}
            details_ul = soup.find("ul", class_="Details")
            if details_ul:
                details_li = details_ul.find_all("li")
                for li in details_li:
                    label = li.find("span", class_="details-label").text.strip(": \n")
                    data_span = li.find("span", class_="details-data")
                    if data_span:
                        data = ''.join([span.text for span in data_span.find_all("span")]) or data_span.text.strip()
                    else:
                        data = ''
                    job_details[label] = data
            City = ''
            state = ''
            Zipcode = ''
            Location = job_details.get('Location', '')
            country = job_details.get('Country', 'United States')
            print('Extracted Location:', Location)

            City, state = '', ''
            if Location:
                parts = Location.split(', ')
                if len(parts) == 2:
                    City, state = parts

            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_details.get('Type', ''),
                "Categories": "Medical Device",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(jobTitle),
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": job_details.get('Date Posted', ''),
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshcardinal.com",
                "Full Name": "",
                "Company Name": "Cardinal",
                "Employer Website": "https://jobs.cardinalhealth.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://jobs.cardinalhealth.com/search/searchjobs"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            if Jobs:
                write_to_csv(Jobs, "data", "Cardinal.csv")
            else:
                print("No jobs found.")
        except Exception as e:
            print(f"Error during job scraping: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
