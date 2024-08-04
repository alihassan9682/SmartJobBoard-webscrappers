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
    while True:
        results = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "jobs_container")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "job"))
        )
        jobs = [
                job.find_element(By.CLASS_NAME, "heading-h5").get_attribute(
                    "href"
                )
            for job in jobs
        ]
        try:
            for job in jobs:
                if job not in unique_jobs:
                    unique_jobs.add(job)
                    JOBS.append(job)
            load_more_button = driver.find_element(By.ID, "load-more-jobs")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "load-more-jobs")))
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
            jobTitle = driver.find_element(By.CLASS_NAME, "job-title").text

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="job-sections")
            jobDescription = desc_content.prettify()

            location_meta = soup.find('meta', itemprop='addressLocality')
            City = location_meta['content'] if location_meta else ''

            state_meta = soup.find('meta', itemprop='addressRegion')
            state = state_meta['content'] if state_meta else ''

            country_meta = soup.find('meta', itemprop='addressCountry')
            country = country_meta['content'] if country_meta else 'United States'
            Location = f"{City}, {state}, {country}"
            employment_type = soup.find('li', itemprop='employmentType').text.strip()
            Zipcode = ''

            date_posted_meta = soup.find('meta', itemprop='datePosted')
            date_posted = date_posted_meta['content'] if date_posted_meta else ''
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": employment_type,
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
                "Posting Date": date_posted,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "N/A",
                "Full Name": "",
                "Company Name": "Biogen",
                "Employer Website": "https://www.biogen.com/",
                "Employer Phone": "+1 781-464-2000",
                "Employer Logo": "https://www.biogen.com/content/dam/corporate/international/global/en-US/global/logos/biogen-logo-colour.svg",
                "Company Description": "Biogen is a leading biotechnology company that pioneers innovative science to deliver new medicines to transform patients’ lives and to create value for shareholders and our communities.We apply deep understanding of human biology and leverage different modalities to advance first-in-class treatments or therapies that deliver superior outcomes. Our approach is to take bold risks, balanced with return on investment to deliver long-term growth.",
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
        url = " https://www.biogen.com/content/corporate/international/global/en-US/careers/careers-search.html?searchKey=sales&country=United%2520States"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Biogen.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
