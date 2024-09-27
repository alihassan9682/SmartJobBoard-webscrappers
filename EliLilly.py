import time
import csv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from helpers import configure_webdriver
from bs4 import BeautifulSoup
from extractCityState import find_city_state_in_title


def request_url(driver, url):
    """Open the given URL in the browser."""
    driver.get(url)

def select_united_states_checkbox(driver):
    """Click the checkbox for the United States to filter job listings."""
    try:
        # Locate and click the checkbox for United States
        country_elements = driver.find_elements(By.CSS_SELECTOR, '#CountryBody .phs-facet-results fieldset ul li')
        for country_element in country_elements:
            label = country_element.find_element(By.XPATH, './label/span[2]')
            if "United States" in label.text:
                checkbox = country_element.find_element(By.CSS_SELECTOR, 'label > span.checkbox')
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                time.sleep(1)  # Ensure the element is in view
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(2)  # Wait for the page to update
                break
    except Exception as e:
        pass

def get_job_urls(driver):
    """Extract job URLs from the job listings page."""
    job_data = []
    try:
        # Locate job listing elements
        job_elements = driver.find_elements(By.CLASS_NAME, 'jobs-list-item')
        for job_element in job_elements:
            try:
                # Extract the job URL from the job element
                job_url = job_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
                job_data.append(job_url)
            except Exception as e:
                pass
    except Exception as e:
        pass
    return job_data

def extract_job_details(driver, job_url):
    """Extract job details from a job page."""
    try:
        driver.get(job_url)
        time.sleep(5)  # Allow time for the page to load

        # Extract job title
        job_title_elements = driver.find_elements(By.CLASS_NAME, 'job-title')
        job_title = job_title_elements[0].text if job_title_elements else "N/A"

        # Extract job location
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-ph-id="ph-page-element-page4-JEFiGF"]'))
        )
        if elements:
            job_location = elements[0].text.split("\n")[1]
        else:
            job_location = "No elements found"

        # Find city and state
        try:
            
            city = job_location.split(',', 1)[0].strip().split()[0]
            if "Remote" in city:
                city = None
            state = job_location.split(',', 2)[1].strip() if ',' in job_location else ""
            
        except:
             city, state = find_city_state_in_title(job_location)


        def is_remote(location):
            remote_keywords = ['remote', 'work from home', 'telecommute']
            return 'Remote' if any(keyword in location.lower() for keyword in remote_keywords) else 'Not Remote'

        # Extract job description
        job_description_elements = driver.find_elements(By.CLASS_NAME, "job-description")
        job_description = job_description_elements[0].text if job_description_elements else "N/A"
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("div", class_="jd-info au-target")
        if desc_content:
            job_description = desc_content.prettify()
        else:
            job_description = None

        # Extract job type
        job_type_elements = driver.find_elements(By.CLASS_NAME, "au-target")
        job_type = job_type_elements[0].text.split('\n')[0] if job_type_elements else "N/A"

        # Extract job ID
        try:
            job_id_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="au-target jobId"]'))
            )
            job_id = job_id_element.text
        except Exception as e:
            pass
            job_id = "N/A"

        job_details = {
            "Job Id": job_id.split("\n")[1] if "\n" in job_id else job_id,
            "Job Title": job_title,
            "Job Description": job_description,
            "Job Type": job_type,
            "Categories": "Sales And Marketing",
            "Location": job_location.replace('Remote, ', '') if 'Remote, ' in job_location else job_location,
            "City": city,
            "State": state,
            "Country": "",
            "Zip Code": "",
            "Address": "",
            "Remote": is_remote(job_location),
            "Salary From": "",
            "Salary To": "",
            "Salary Period": "",
            "Apply URL": "https://careers.lilly.com/us/en/apply?jobSeqNo=LILLUSR68963EXTERNALENUS&step=1",
            "Apply Email": "",
            "Posting Date": '',
            "Expiration Date": "",
            "Applications": "",
            "Status": "",
            "Views": "",
            "Employer Email": "msh@mshelililly.com",
            "Full Name": "",
            "Company Name": "Eli Lilly and Company",
            "Employer Website": "https://www.lilly.com/",
            "Employer Phone": "(800) 545-5979",
            "Employer Logo": "https://cdn.phenompeople.com/CareerConnectResources/LILLUS/images/lillylogo-1662975140389.png",
            "Company Description": "Eli Lilly and Company is an American pharmaceutical company headquartered in Indianapolis, Indiana, with offices in 18 countries. Its products are sold in approximately 125 countries.",
            "Status": "Active",
        }
        return job_details
    except Exception as e:
        pass
        return None

def write_to_csv(data, directory, filename):
    """Write job details to a CSV file."""
    fieldnames = list(data[0].keys()) if data else []
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    pass
    with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for item in data:
            writer.writerow(item)
    

def scraping():
    """Main function to perform the web scraping."""
    try:
        # Configure the web driver
        driver = configure_webdriver(True)
        driver.maximize_window()

        # Set the initial URL of the website to scrape
        url = "https://careers.lilly.com/us/en/c/salesmarketing-jobs"
        try:
            request_url(driver, url)
            select_united_states_checkbox(driver)
            
            # Get job URLs
            job_urls = get_job_urls(driver)
            job_details_list = []
            for job_url in job_urls:
                job_details = extract_job_details(driver, job_url)
                if job_details:
                    job_details_list.append(job_details)
            
            if job_details_list:
                write_to_csv(job_details_list, "data", "EliLilly.csv")
        
        except Exception as e:
            pass
        finally:
            driver.quit()
    except Exception as e:
        pass

# Run the scraping function
scraping()
