import time

from extractCityState import filter_job_title, find_city_state_in_title
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


def loadAllJobs(driver):
    JOBS = []
    wait = WebDriverWait(driver, 10)
    close = wait.until(
        EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))
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
        jobs = [
                job.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )
            for job in jobs
        ]

        try:
            JOBS = JOBS + jobs

            next_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "next"))
            )
            
            if next_button and 'disabled' not in next_button.get_attribute('class'):
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
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            job_elements = None
            try:
                job_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'jd-header-content__job-heading'))
                )
            except:
                print("No Job element found")
            jobTitle = job_elements.find_element(By.TAG_NAME, 'h1').text
            if not filter_job_title(jobTitle):
                continue
            # info_bar = job_elements.find_element(By.CLASS_NAME, 'info-bar')
            job_id_element = job_elements.find_element(By.CLASS_NAME, 'job-id')
            job_id = job_id_element.text.replace("Req #: ", "").strip() if job_id_element else jobs.index(job)
            location_element = job_elements.find_element(By.CLASS_NAME, 'job-location')
            Location_ist = location_element.text.replace("Location:", "").strip() if location_element else ''
            Location = Location_ist
            try:
                additional_locations_element = job_elements.find_element(By.CLASS_NAME, 'job-additional-locations')
                Additional_Locations = additional_locations_element.text.replace("Additional locations", "").strip()
                Location += ", " + Additional_Locations
            except:
                pass
            
            date_posted_element = job_elements.find_element(By.CLASS_NAME, 'job-date')
            posted_date = date_posted_element.text.replace("Date posted: ", "").strip() if date_posted_element else ''
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify()
            location_parts = Location_ist.split(',')
            City = state = job_type = ''
            if len(location_parts) == 3:
                City = location_parts[0].strip()
                state = location_parts[1].strip()
            elif len(location_parts) ==2:
                City = location_parts[0].strip()
                state = ''
            else:
                City = state = ''
            country = 'Unites States'
            city_title, state_title = find_city_state_in_title(jobTitle)
            if city_title:
                City = city_title
            if state_title:
                state = state_title

            from extract_location import extracting_location
            Location = extracting_location(City,state)
            
            Zipcode = ''

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Medical Device",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(Location),
                "Salary From": '',
                "Salary To": '',
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": posted_date,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshbaxter.com",
                "Full Name": "",
                "Company Name": "Baxter",
                "Employer Website": " https://jobs.baxter.com/",
                "Employer Phone": "",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/152/v3_0/img/baxter_logo_blue.svg",
                "Company Description": "As an innovative, global healthcare leader, Baxter offers advanced products, technologies and therapies that provide the support people need to lead healthier, longer lives.",
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
        url = " https://jobs.baxter.com/en/search-jobs/sales/United%20States/152/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Baxter.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
