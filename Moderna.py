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
    last_processed_index = 0
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "position-cards-container")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "position-card"))
        )
        for index in range(last_processed_index, len(jobs)):
            job = jobs[index]
            try:
                job.click()
                time.sleep(3)

                job_url = driver.current_url

                if job_url not in unique_jobs:
                    unique_jobs.add(job_url)
                    JOBS.append(job_url)
            except Exception as e:
                print(f"Error processing job card: {e}")

        last_processed_index = len(jobs)
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "show-more-positions")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "show-more-positions")))
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
    wait = WebDriverWait(driver, 10)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2) 
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            jobTitle = soup.find("h1", class_="position-title").text
            desc_content = soup.find("div", class_="position-job-description-column")
            jobDescription = desc_content.prettify()

            selected_card = soup.find("div", class_='card-selected')
            location_meta = selected_card.find("p",class_='position-location')
            Location = location_meta.text if location_meta else ''

            state = ''

            country = 'United States'
            City = ''
            Zipcode = ''

            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": '',
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": '',
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
                "Employer Email": "msh@mshmoderna.com",
                "Full Name": "",
                "Company Name": "Moderna",
                "Employer Website": "https://modernatx.eightfold.ai/",
                "Employer Phone": "",
                "Employer Logo": "https://static.vscdn.net/images/careers/demo/modernatx-sandbox/1646929253::MB033L-T.png",
                "Company Description": "Moderna Is An Equal Opportunity Employer And Makes Employment Decisions Without Regard To Race, Color, Religion, Sex, Sexual Orientation, Gender Identity, National Origin, Age, Protected Veteran Status, Disability Status, Or Any Other Status Protected By Law.",
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
        url = "https://modernatx.eightfold.ai/careers/?query=sales&location=united%20states&pid=309256314917&domain=modernatx.com&sort_by=relevance&triggerGoButton=true"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Moderna.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
