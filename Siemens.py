import time
from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
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


def get_location_details(location):
    if 'and' in location:
        location = location.split('and')[0].strip()

    parts = location.split(', ')
    city = state = country = ''

    if len(parts) == 3:
        city = parts[0].strip()
        state = parts[1].strip()
        country = parts[2].strip()
    elif len(parts) == 2:
        state = parts[0].strip()
        country = parts[1].strip()
    elif len(parts) == 1:
        country = parts[0].strip()

    return city, state, country


def loadAllJobs(driver):
    JOBS = []
    unique_jobs = set()
    wait = WebDriverWait(driver, 10)
    last_processed_index = 0
    close = wait.until(
        EC.presence_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"))
    )
    close.click()
    while True:

        results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "position-cards-container")))
        try:
            jobs = WebDriverWait(results, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "position-card")))
        except StaleElementReferenceException:
            print("StaleElementReferenceException occurred while locating job cards. Refreshing...")
            continue
        for index in range(last_processed_index, len(jobs)):
            job = jobs[index]
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", job)
                time.sleep(2)
                job.click()
                time.sleep(2)

                job_url = driver.current_url

                if job_url not in unique_jobs:
                    unique_jobs.add(job_url)
                    JOBS.append(job_url)
    
                    
            except StaleElementReferenceException as e:
                print(f"StaleElementReferenceException encountered: {e}")
                time.sleep(1)
                break
            except Exception as e:
                print(f"Error processing job card: {e}")

        last_processed_index = len(jobs)
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "show-more-positions")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "show-more-positions")))
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
            job_meta = soup.find("h1", class_="position-title")
            jobTitle = job_meta.text if job_meta else ''
            print('job title', jobTitle)
            desc_content = soup.find("div", class_="position-job-description-column")
            jobDescription = desc_content.prettify() if desc_content else ''

            selected_card = soup.find("div", class_='card-selected')
            location_meta = selected_card.find("p", class_='position-location')
            remote_meta = selected_card.find("p", class_='label_g_1gGNB small_E4otQdF')
            Location_detail = location_meta.text if location_meta else ''
            Location = Location_detail.split('and')[0] if 'and' in Location_detail else Location_detail
            City, state, country = get_location_details(Location_detail)
            country = 'United States'
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
                "Remote": is_remote(remote_meta if remote_meta else ''),
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "msh@mshsiemens.com",
                "Full Name": "",
                "Company Name": "Siemens",
                "Employer Website": "https://jobs.siemens-healthineers.com",
                "Employer Phone": "",
                "Employer Logo": "https://static.vscdn.net/images/careers/demo/siemens/1677769995::Healthineers+Logo+2023",
                "Company Description": "We pioneer breakthroughs in healthcare. For everyone. Everywhere. Sustainably.",
                "Status": "Active",
            }
            JOBS.append(jobDetails)

        except StaleElementReferenceException as e:
            print(f"StaleElementReferenceException encountered: {e}")
            time.sleep(1)
            continue
        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://jobs.siemens-healthineers.com/careers?query=Sales&location=united%20states&pid=563156119657205&domain=siemens.com&sort_by=relevance&triggerGoButton=false&triggerGoButton=true"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Siemens.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
