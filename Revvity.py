import time

from helpers import configure_webdriver, is_remote

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
        EC.presence_of_element_located((By.ID, "system-ialert-reject-button"))
    )
    close.click()
    
    while True:
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
        print('total jobs', len(jobs))
        try:
            JOBS = JOBS + jobs
            print('HOBS', len(JOBS))
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

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title_meta = soup.find("div", class_= "hero-job-details-title")
            jobTitle = title_meta.find('h1').text if title_meta else ''
            job_id_meta = title_meta.find('span', class_="job-id job-info")
            job_id = job_id_meta.get_text(strip=True).replace("Req ID", "") if job_id_meta else jobs.index(job)
            desc_content = soup.find("section", class_="job-description")
            desc_meta = desc_content.find("div", class_= "ats-description")
            jobDescription = desc_meta.prettify() if desc_meta else ''
            location_meta = title_meta.find("span", class_="job-location job-info")
            City = state = job_type =''
            Location = location_meta.text if location_meta else ''
            country = 'United States'
            Zipcode = ''
            print("Location", Location)
            print("Job Title", jobTitle)
            print('remote', is_remote(Location))
            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Diagnostic",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(Location),
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
                "Employer Email": "msh@mshrevvity.com",
                "Full Name": "",
                "Company Name": "Revvity",
                "Employer Website": "https://jobs.revvity.com/",
                "Employer Phone": "",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/20539/v3_0/img/revvity-animated-logo.gif",
                "Company Description": "Impossible is inspiration.If they say “impossible,” we say “challenge accepted.” At Revvity, we fearlessly face tomorrow’s unknowns for a healthier humankind.",
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
        url = "https://jobs.revvity.com/search-jobs/sales/United%20States/20539/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Revvity.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
