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


def loadAllJobs(driver):
    JOBS = []
    wait = WebDriverWait(driver, 10)
    close = wait.until(
        EC.presence_of_element_located((By.ID, "system-ialert-button"))
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
            EC.presence_of_element_located((By.XPATH, "//button[@class='pagination-page-jump']/following-sibling::a[1][contains(@class, 'next')]"))
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
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            jobTitle = driver.find_element(By.CLASS_NAME, "header-1").text

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="ats-description")
            jobDescription = desc_content.prettify()
            location_meta = soup.find("span", class_="job-location__small job-info")
            City = state = job_type = Location =''
            country = 'US'

            if location_meta:
                Location = location_meta.span.text if location_meta else ''
                job_type_span = soup.find_all("span", class_="job-location__small job-info")[-1]
                job_type = job_type_span.text.split("WORK LOCATION TYPE: ")[1].strip() if job_type_span and "WORK LOCATION TYPE: " in job_type_span.text else ""
                location_parts = Location.split('-') if Location else ''
                if len(location_parts) == 3:
                    City = location_parts[2].strip()
                    state = location_parts[1].strip()
                    country = location_parts[0].strip()

                
            all_job_date_spans = soup.find_all('span', class_='job-date job-info')
            additional_locations_span = salary_range = posted_date = ''
            for span in all_job_date_spans:
                if "ADDITIONAL LOCATIONS:" in span.get_text(separator=" "):
                    additional_locations_span = span
                if "DATE POSTED:" in span.get_text():
                    posted_date = span.text.split("DATE POSTED: ")[1].strip()
                if "SALARY RANGE:" in span.get_text():
                    salary_range = span.text.split("SALARY RANGE: ")[1].strip()

            if additional_locations_span:
                additional_locations_text = additional_locations_span.get_text(separator=" ").split("ADDITIONAL LOCATIONS: ")[1].strip()
                additional_locations = additional_locations_text.split("; ")
                # print("Additional Locations:", additional_locations)
                locations =  [loc for loc in additional_locations if "US" in loc]
                if locations:
                    if Location:
                        Location += ', ' + ', '.join(locations)
                    else:
                        Location = ', '.join(locations)

                    if City:
                        City += ', ' + ', '.join([loc.split('-')[2].strip() for loc in locations if len(loc.split('-')) == 3])
                    else:
                        City = ', '.join([loc.split('-')[2].strip() for loc in locations if len(loc.split('-')) == 3])

                    if state:
                        state += ', ' + ', '.join([loc.split('-')[1].strip() for loc in locations if len(loc.split('-')) == 3])
                    else:
                        state = ', '.join([loc.split('-')[1].strip() for loc in locations if len(loc.split('-')) == 3])

                    country = 'US'
            else:
                print("No additional locations found")

            Zipcode = ''
            job_id = soup.find("span", class_="job-id job-info").text if soup.find("span", class_="job-id job-info") else ""
            if "-" in salary_range and len(salary_range) > 1:
                from_salary, to_salary = salary_range.split(" - ")
                from_salary = from_salary.strip()
                to_salary = to_salary.strip()
            else:
                from_salary = to_salary = ""

            jobDetails = {
                "Job Id": job_id,
                "Job Title": jobTitle,
                "Job Description": jobDescription,
                "Job Type": job_type,
                "Categories": "Pharmaceuticals",
                "Location": Location,
                "City": City,
                "State": state,
                "Country": country,
                "Zip Code": Zipcode,
                "Address": Location,
                "Remote": is_remote(Location),
                "Salary From": from_salary,
                "Salary To": to_salary,
                "Salary Period": "",
                "Apply URL": job,
                "Apply Email": "",
                "Posting Date": posted_date,
                "Expiration Date": "",
                "Applications": "",
                "Status": "",
                "Views": "",
                "Employer Email": "N/A",
                "Full Name": "",
                "Company Name": "Amgen",
                "Employer Website": "https://careers.amgen.com/",
                "Employer Phone": "",
                "Employer Logo": "https://tbcdn.talentbrew.com/company/87/cms/logos/logo-amgen-lg.png",
                "Company Description": "Amgen is an Equal Opportunity Employer and will consider all qualified applicants for employment without regard to race, color, religion, sex, sexual orientation, gender identity, national origin, protected veteran status or disability status.",
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
        url = "https://careers.amgen.com/en/search-jobs/sales/United%20States/87/1/2/6252001/39x76/-98x5/50/2"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "Amgen.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
