import time

from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


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

def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def loadAllJobs(driver):
    JOBS = []
    wait = WebDriverWait(driver, 10)
    scroll_to_bottom(driver)

    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "css-8j5iuw")
        ))
        job_links = results.find_elements(By.CSS_SELECTOR, "[data-uxi-element-id='jobItem']")
        
        for link in job_links:
            job_url = link.get_attribute("href")
            if job_url and job_url not in JOBS:
                JOBS.append(job_url)
        try:
            print('HOBS', len(JOBS))
            next_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-uxi-element-id='next']"))
            )
            
            if next_button:
                actions = ActionChains(driver)
                actions.move_to_element(next_button).click().perform()
                time.sleep(2)
            else:
                break
        except:
            print("No more pages or an error occurred")
            break


    return JOBS


def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    wait = WebDriverWait(driver, 10)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(3)
            job_meta = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[name="title"][property="og:title"]'))
            )
            jobTitle = job_meta.get_attribute('content') if job_meta else ''
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", {'data-automation-id': "jobPostingDescription"})
            if desc_content:
                for span in desc_content.find_all("span"):
                    span.unwrap()
                for tag in desc_content.find_all(True):
                    tag.attrs = {}
                jobDescription = desc_content.prettify(formatter="html")
            else:
                jobDescription = ''
            job_details = {
                'time_type': None,
                'posted_on': None,
                'requisition_id': None
            }

            try:
                # Extracting time type
                time_type_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='time'] dd")))
                job_details['time_type'] = time_type_element.text

                # Extracting posted on date
                posted_on_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='postedOn'] dd")))
                job_details['posted_on'] = posted_on_element.text

                # Extracting job requisition ID
                requisition_id_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='requisitionId'] dd")))
                job_details['requisition_id'] = requisition_id_element.text

            except Exception as e:
                print(f"Error occurred: {e}")

            location_div = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'css-cygeeu'))
            )
            try:
                location_button = location_div.find_element(By.CSS_SELECTOR, '[data-automation-id="locationButton-collapsed"]')
                location_button.click()
                time.sleep(1)
            except:
                pass  # The button is not present, continue without clicking

            # Extracting all 'dd' elements with class 'css-129m7dg' inside the 'css-cygeeu' div
            location_elements = location_div.find_elements(By.CLASS_NAME, 'css-129m7dg')
            locations = [elem.text for elem in location_elements]

            location_list = []
            city_list = []
            state_list = []
            country = "United States"

            for location in locations:
                loc_text = location
                parts = [part.strip() for part in loc_text.split('-')]
                
                if len(parts) == 3 or len(parts) > 3:
                    city_list.append(parts[2])
                    state_list.append(parts[1])
                elif len(parts) == 2:
                    state_list.append(parts[1])
                
                location_list.append(loc_text)
            location = ', '.join(location_list) if location_list else ''
            City = ', '.join(city_list) if city_list else ''
            state = ', '.join(state_list) if state_list else ''
            Zipcode = ''
            print("Job Title", jobTitle)
            print("city", City)
            print("state", state)
            print("country", country)
            jobDetails = {
                "Job Id": job_details.get('requisition_id', jobs.index(job)),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_details.get('time_type', ''),
                "Categories": "Diagnostic",
                "Location": location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": location,
                "Remote": '',
                "Salary From": '',
                "Salary To": '',
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": job_details.get('posted_on', ''),
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshexactsciences.com",
                "Full Name": "",
                "Company Name": "Exact Sciences",
                "Employer Website": "https://exactsciences.wd1.myworkdayjobs.com/Exact_Sciences",
                "Employer Phone": "",
                "Employer Logo": "https://exactsciences.wd1.myworkdayjobs.com/Exact_Sciences/assets/logo",
                "Company Description": "We are Exact Sciences, and we're changing lives together through earlier detection and smarter answers.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://exactsciences.wd1.myworkdayjobs.com/Exact_Sciences?q=sales&locationCountry=bc33aa3152ec42d4995f4791a106ed09"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "ExactSciences.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
