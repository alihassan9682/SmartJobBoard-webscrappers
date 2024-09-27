import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import csv
import os
from helpers import configure_webdriver, is_remote
from extractCityState import find_city_state_in_title

def getting_links(driver):
    jobs_link = []
    i = 1
    while True:
        try:
            link_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"(//section[@class='openings-section opening opening--grouped js-group'][.//h3[contains(@class, 'text--default') and text()='Sales']]//a[contains(@class, 'link--block') and contains(@class, 'details')])[{i}]")
                )
            )
            link = link_element.get_attribute("href")
            jobs_link.append(link)
            i += 1
        except:
            return jobs_link

def see_all(driver):
    while True:
        try:
            see_more = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//section[@class='openings-section opening opening--grouped js-group'][.//h3[contains(@class, 'text--default') and text()='Sales']]//a[@data-value='4099761']")
                )
            )
            see_more.click()
            time.sleep(2)  # Short delay to let the page update
        except:
            return getting_links(driver)

def extracting_links(link_list, driver):
    list_jobs = []
    for link in link_list:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[@class='job-title']")))
            job_details = getting_values(driver, link)
            if job_details:
                list_jobs.append(job_details)
        except Exception as e:
            pass
          
    return list_jobs

def getting_values(driver, url):
    try:
        # Find and print job title
        job_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@class='job-title']"))
        ).text
        

        # Find and print job location
        job_location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//main[@class='jobad-main job']//ul[@class='job-details']"))
        ).text.split('\n')[0]
        

        # Find city and state
        try:
            city, state = find_city_state_in_title(job_location)
        except:
            city, state = [part.strip() for part in job_location.split(',')[:2]]
        
        # Find job description
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        desc_content = soup.find("div", itemprop="description")
        job_description = desc_content.prettify() if desc_content else None
        
        #location
        from extract_location import extracting_location
        location = extracting_location(city,state)

        jobDetails = {
            "Job Id": "",
            "Job Title": job_title,
            "Job Description": job_description,
            "Job Type": '',
            "Categories": "Pharmaceuticals",
            "Location": location,
            "City": city,
            "State": state,
            "Country": "United States",
            "Zip Code": "",
            "Address": location,
            "Remote": is_remote(job_location),
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
            "Employer Email": "msh@msheversana.com",
            "Full Name": "",
            "Company Name": "EVERSANA",
            "Employer Website": "https://www.eversana.com/",
            "Employer Phone": '800-367-5690',
            "Employer Logo": "https://c.smartrecruiters.com/sr-careersite-image-prod-dc5/63c6ad0d06d92d0c82fbc3eb/291869c1-b367-4799-bd99-2ad310e547e4?r=s3-eu-central-1",
            "Company Description": "The life sciences sector is changing by the minute. That’s why we’ve built the integrated commercial services platform to solve any drug pricing, promotion, access, reimbursement, adherence, or product delivery challenge. Powered by data & analytics. Ready-to-deploy infrastructure. Proven expertise. We’ll manage the complete launch and commercialization of products or address specific program or patient needs. We are EVERSANA. ",
            "Status": "Active",
        }
        
        return jobDetails

    except Exception as e:
        
        return None

def write_to_csv(data, directory, filename):
    fieldnames = list(data[0].keys())
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for item in data:
            writer.writerow(item)

def scraping():
    driver = configure_webdriver(True)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.maximize_window()
    url = "https://careers.smartrecruiters.com/EVERSANA1"
    driver.get(url)
    
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)
    
    links = see_all(driver)
    
    
    list_jobs = extracting_links(links, driver)
    if list_jobs != None:
        write_to_csv(list_jobs, "data", "EVERSANA.csv")
    else:
        pass

    driver.quit()

scraping()
