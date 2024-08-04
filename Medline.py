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
    keyword = wait.until(EC.presence_of_element_located((By.ID, "KEYWORD")))
    keyword.send_keys("sales")
    search_button = driver.find_element(By.ID, "search")
    search_button.click()
    time.sleep(2)

    checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox'][title='United States']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(2)

    while True:
        try:
            results = wait.until(EC.presence_of_element_located((By.ID, "jobList")))
            jobs = WebDriverWait(results, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "multiline-data-container")))
            job_links = [job.find_element(By.TAG_NAME, "a").get_attribute("href") for job in jobs]
            JOBS.extend(job_links)

            try:
                load_more_button = driver.find_element(By.ID, "next")
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "next")))
                check_disabled = load_more_button.get_attribute("aria-disabled")
                if check_disabled == "false":
                    load_more_button.click()
                    time.sleep(2)
                else:
                    print('No more next button')
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
            job_meta = driver.find_element(By.ID, "requisitionDescriptionInterface.reqTitleLinkAction.row1")
            jobTitle = job_meta.text if job_meta else ''
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="mastercontentpanel3")
            desc = desc_content.find("div", class_="editablesection")
            jobDescription = desc.prettify() if desc else ''
            City = state = country = ''
            P_Location = driver.find_element(By.ID, "requisitionDescriptionInterface.ID1511.row1")
            if P_Location:
                Location = P_Location.text
                parts = Location.split('-')
                if len(parts) == 3 or len(parts) == 4:
                    state = parts[1]
                    City = parts[2]
                    
                else:
                    City = state = ''
                country = 'United States'
            try:
                location_meta = driver.find_element(By.ID, "requisitionDescriptionInterface.ID1561.row1").text
                if location_meta:
                    
                    Location += location_meta
                    locations = location_meta.split(',')
                    cities = []
                    states = []
                    for loc in locations:
                        parts = loc.strip().split('-')
                        if len(parts) == 3 or len(parts) == 4:
                            cities.append(parts[2].strip())
                            states.append(parts[1].strip())
                        elif len(parts) == 2:
                            cities.append(parts[1].strip())
                            states.append(parts[0].strip())
                        elif len(parts) == 1:
                            cities.append(parts[0].strip())
                            states.append('')
                        else:
                            print(f"Unexpected location format: {loc}")
                

                    City += ', '.join(cities) if cities else ''
                    state += ', '.join(states) if states else ''
                    country = 'United States'

            except:
                pass

            Zipcode = ''

            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
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
                "Posting Date": '',
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshmedline.com",
                "Full Name": "",
                "Company Name": "Medline",
                "Employer Website": " https://medline.taleo.net/",
                "Employer Phone": "",
                "Employer Logo": "https://medline.taleo.net/careersection/theme/321/1707193440000/en/theme/images/medline-header.png",
                "Company Description": "We create partnerships that last by bringing the best ideas forward. Our entrepreneurial culture, along with our experience as a clinical leader and supply chain expert, inspires a “can-do” attitude, allowing us to act quickly and choose the right products and solutions so you can provide the best care.",
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
        url = "https://medline.taleo.net/careersection/md_external/jobsearch.ftl?lang=en"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Medline.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
