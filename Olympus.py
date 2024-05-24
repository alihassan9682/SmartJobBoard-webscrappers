import time

from helpers import configure_webdriver, configure_undetected_chrome_driver

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


def getJobs(driver):
    JOBS = []
    jobs = driver.find_elements(By.CLASS_NAME, "data-row")
    for job in jobs:
        try:
            jobID = job.find_element(By.CLASS_NAME, "jobFacility").text
            jobTitle = job.find_element(By.CLASS_NAME, "jobTitle").text
            Location = job.find_element(By.CLASS_NAME, "colLocation").text
            splitLoc = Location.split(',')
            City = splitLoc[0]
            state = splitLoc[1]
            country = splitLoc[2]
            Zipcode = splitLoc[3]

            original_window = driver.current_window_handle
            url = job.find_element(By.CLASS_NAME, "jobTitle-link").get_attribute("href")
            driver.switch_to.new_window("tab")
            driver.get(url)
            time.sleep(2)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find(
                "span", class_="jobdescription"
            ) 
            jobDescription = desc_content.prettify()

            ApplyLink = driver.find_element("css selector", "[aria-label='Apply now']").get_attribute("href")
            jobDetails = {
                "Job Id": jobID,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": "",
                "Categories": "Medical Device",
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
                "Apply URL": url,
                "Apply Email": "",
                "Posting Date": "",
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "OCAAccommodations@olympus.com",
                "Full Name": "",
                "Company Name": "Olympus",
                "Employer Website": "https://careers.olympusamerica.com/home/",
                "Employer Phone": "1-888-659-6787",
                "Employer Logo": "",
                "Company Description": "Olympus, a leading medical technology company, has focused on making people’s lives better for over 100 years Our Purpose is to make people’s lives healthier, safer, and more fulfilling.",
            }
            JOBS.append(jobDetails)
            driver.close()
            driver.switch_to.window(original_window)
        except Exception as e:
            print(f"Error in loading post details: {e}")
            driver.close()
            driver.switch_to.window(original_window)
    return JOBS


def scraping():
    try:
        driver = configure_webdriver(False)
        driver.maximize_window()
        url = "https://careers.olympusamerica.com/search/?createNewAlert=false&q=sales&optionsFacetsDD_customfield4=&optionsFacetsDD_country=&optionsFacetsDD_customfield5=&optionsFacetsDD_customfield3="
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Olympus.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
