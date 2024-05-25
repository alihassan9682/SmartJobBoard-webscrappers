import time

from helpers import configure_webdriver, configure_undetected_chrome_driver, is_remote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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
    essential = wait.until(
        EC.presence_of_element_located((By.ID, "js-cookie-reject"))
    )
    essential.click()
    while True:
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        results = wait.until(EC.presence_of_element_located(
            (By.ID, "js-job-search-results")
        ))
        jobs = WebDriverWait(results, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "card-job"))
        )
        jobs = [
            [
                job.find_element(By.CLASS_NAME, "js-view-job").get_attribute(
                    "href"
                ),
                # job.find_element(By.CSS_SELECTOR, "[au-target-id='147']").text.split('\n')[-1],
            ]
            for job in jobs
        ]
        try:
            JOBS = JOBS + jobs
            next = driver.find_element(
                By.CSS_SELECTOR, "[title='Go to next page of results']"
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
            driver.get(job[0])
            time.sleep(2)
            jobTitle = driver.find_element(By.CLASS_NAME, "hero-heading").text
            Location = "United States"
            City = ''
            state = ''
            country = ''
            Zipcode = ''

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("article", class_="cms-content")
            jobDescription = desc_content.prettify()
            jobCategory = ""

            job_meta = soup.find('ul', class_='job-meta')
            function_li = job_meta.find('li')

            # Extract the function value
            if function_li:
                jobCategory = function_li.find_next_sibling('li').span.text
                print("jobCategory:", jobCategory)
            else:
                print("jobCategory not found.")
            jobDetails = {
                "Job Id": jobs.index(job),
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": "",
                "Categories": jobCategory,
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": "",
                "Salary From": "",
                "Salary To": "",
                "Salary Period": "",
                "Apply URL": job[0],
                "Apply Email": "",
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "N/A",
                "Full Name": "",
                "Company Name": "Johnson and Johnson",
                "Employer Website": "https://jobs.jnj.com/",
                "Employer Phone": "",
                "Employer Logo": "",
                "Company Description": "At Johnson & Johnson, we believe health is everything. Our strength in healthcare innovation empowers us to build a world where complex diseases are prevented, treated and cured, treatments are smarter and less invasive and solutions are personal.",
            }
            JOBS.append(jobDetails)

        except Exception as e:
            print(f"Error in loading post details: {e}")
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://jobs.jnj.com/en/jobs/?search=sales&country=United+States&pagesize=20#results"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Jhonsan.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
