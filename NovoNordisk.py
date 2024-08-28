import time

from extractCityState import filter_job_title, find_city_state_in_title
from helpers import configure_webdriver, is_remote

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

def extract_location_details(location_string):
    remote_status = False
    cities = ""
    states = ""
    country = ""

    locations = [location.strip() for location in location_string.split('/')]

    for loc in locations:
        if loc.startswith("Remote - "):
            remote_status = True
            loc = loc[len("Remote - "):]

        parts = loc.split(',')
        if len(parts) >= 3:
            city = parts[0].strip()
            state = parts[1].strip()
            country = parts[2].strip()
        elif len(parts) == 2:
            city = parts[0].strip()
            state = parts[1].strip()
            country = "United States of America"
        else:
            city = state = country = ''

        cities += city + ", "
        states += state + ", "

    cities = cities.rstrip(", ")
    states = states.rstrip(", ")

    return str(remote_status), cities, states, country

def loadAllJobs(driver):
    JOBS = []
    unique_jobs = set()
    wait = WebDriverWait(driver, 10)
    last_processed_index = 0

    try:
        essential = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ot-pc-refuse-all-handler"))
        )
        essential.click()
    except Exception as e:
        print(f"Error clicking essential cookies button: {e}")

    while True:
        try:
            results = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "g-results")
            ))
            jobs = WebDriverWait(results, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "g-row"))
            )

            for index in range(last_processed_index, len(jobs)):
                job = jobs[index]
                try:
                    job.click()
                    time.sleep(2)
                    
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        job_url = driver.current_url

                        if job_url not in unique_jobs:
                            unique_jobs.add(job_url)
                            JOBS.append(job_url)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(3)
                    else:
                        print("New tab did not open as expected.")
                except Exception as e:
                    print(f"Error processing job: {e}")

            last_processed_index = len(jobs)
            try:
                load_more_button = driver.find_element(By.CLASS_NAME, "loading-button")
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "loading-button")))
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(3)
            except NoSuchElementException:
                print("No more 'Load More' button found, all jobs are loaded.")
                break
            except Exception as e:
                print(f"Error clicking load more button: {e}")
                break
        except Exception as e:
            print(f"Error in main loop: {e}")
            break

    return JOBS
def getJobs(driver):
    JOBS = []
    jobs = loadAllJobs(driver)
    for job in jobs:
        try:
            driver.get(job)
            time.sleep(2)
            jobTitle = driver.find_element(By.CLASS_NAME, "title").text
            if not filter_job_title(jobTitle):
                continue
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc_content = soup.find("div", class_="job-display-details")
            job_display_details_buttons = desc_content.find("div", class_="job-display-details-buttons")
            if (job_display_details_buttons):
                job_display_details_buttons.decompose()
            jobDescription = desc_content.prettify()

            location_tag = soup.find('p', string='Location').find_next_sibling('p')
            Location = location_tag.text if location_tag else ''

            location_parts = Location.split(", ")
            City = location_parts[0] if location_parts[0] else ''
            state = ''
            country = location_parts[1] if location_parts[1] else ''
            Zipcode = ''
            city_title, state_title = find_city_state_in_title(jobTitle)
            if city_title:
                City = city_title
            if state_title:
                state = state_title
            Location = City + ', ' + state + ', ' + 'USA'
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
                "Employer Email": "N/A",
                "Full Name": "",
                "Company Name": "Novo Nordisk",
                "Employer Website": "https://www.novonordisk.com/",
                "Employer Phone": "+45 4444 8888",
                "Employer Logo": "",
                "Company Description": "We are a global healthcare company, founded in 1923 and headquartered just outside Copenhagen, Denmark.Our purpose is to drive change to defeat serious chronic diseases, built upon our heritage in diabetes. We do so by pioneering scientific breakthroughs, expanding access to our medicines and working to prevent and ultimately cure the diseases we treat.",
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
        url = "https://www.novonordisk.com/careers/find-a-job/career-search-results.html?searchText=&countries=United+States&categories=Sales"
        try:
            driver.get(url)
            Jobs = getJobs(driver)
            write_to_csv(Jobs, "data", "NovoNordisk.csv")
        except Exception as e:
            print(f"Error : {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


scraping()
