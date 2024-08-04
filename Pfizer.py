import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import os

from helpers import configure_webdriver, is_remote  # Ensure these imports are correct for your environment

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
    
    try:
        close = wait.until(
            EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))
        )
        close.click()
    except Exception as e:
        print(f"Error clicking cookie consent button: {e}")

    try:
        location_section = wait.until(
            EC.presence_of_element_located((By.ID, "workday-region_input"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(location_section).perform()
    except Exception as e:
        print(f"Error locating region placeholder: {e}")

    try:
        checkbox = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox'][data-val='United States of America']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(2)
    except Exception as e:
        print(f"Error locating or clicking United States checkbox: {e}")
    
    try:
        view_jobs_div = wait.until(
            EC.presence_of_element_located((By.ID, 'workday-region_itemList'))
        )
        view_job_button = view_jobs_div.find_element(By.CLASS_NAME, 'view-all-button')
        
        driver.execute_script("arguments[0].scrollIntoView(true);", view_job_button)
        driver.execute_script("arguments[0].click();", view_job_button)
        time.sleep(3)
    except Exception as e:
        print(f"Error locating or clicking view all button: {e}")
    
    while True:
        try:
            results = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "result-wrapper")
            ))
            jobs = WebDriverWait(results, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job-posting"))
            )
            jobs = [
                job.find_element(By.TAG_NAME, "a").get_attribute("href")
                for job in jobs
            ]
            try:
                JOBS = JOBS + jobs
        
                next_button_div = driver.find_element(By.ID, "next-page")
                next_button = next_button_div.find_element(By.TAG_NAME, 'a')
                if 'disabled' in next_button_div.get_attribute('class'):
                    print('No more pages', len(JOBS))
                    break
                else:
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((next_button)))
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
            except Exception as e:
                print(f"Error locating or clicking next button: {e}")
                break
        except Exception as e:
            print(f"No next button found or error clicking it: {e}")
            break
    return JOBS

def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            jobTitle = driver.find_element(By.CLASS_NAME, "posting-title").text
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="posting-description")
            jobDescription = desc_content.prettify() if desc_content else ''

            location_elements = soup.select('.locations li')

            cities = []
            states = []
            Locations = []
            for location in location_elements:
                location_text = location.get_text(strip=True)
                try:
                    if 'United States' in location_text:
                        Locations.append(location_text)
                        parts = location_text.split(' - ')
                        if len(parts) == 3:
                            cities.append(parts[2])
                            states.append(parts[1])
                except:
                    pass

            city = ', '.join(cities) if cities else ''
            state = ', '.join(states) if states else ''
            location = ', '.join(Locations) if Locations else ''
            country = 'United States of America'
            Zipcode = ''

            job_type = soup.select_one('.type').get_text(strip=True) if soup.select_one('.type') else ''

            posting_date = soup.select_one('.posted-date').get_text(strip=True) if soup.select_one('.posted-date') else ''

            job_id = soup.select_one('.job-id').get_text(strip=True) if soup.select_one('.job-id') else str(jobs.index(job))

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
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
                "Posting Date": posting_date,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshpfizer.com",
                "Full Name": "",
                "Company Name": "Pfizer",
                "Employer Website": "https://www.pfizer.com/",
                "Employer Phone": "1-800-879-3477",
                "Employer Logo": "",
                "Company Description": "We’re in relentless pursuit of breakthroughs that change patients’ lives. We innovate every day to make the world a healthier place. It was Charles Pfizer’s vision at the beginning and it holds true today.",
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
        url = "https://www.pfizer.com/about/careers/search-results?langcode=en&keywords=sales&count=10&sort=latest"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Pfizer.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
