from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the webdriver
driver = webdriver.Chrome()

try:
    # Open the URL
    driver.get(
        "https://bbrauncareers-bbraun.icims.com/jobs/search?pr=1&searchKeyword=sales&searchLocation=12781--&searchRelation=keyword_all&mobile=false&width=1168&height=500&bga=true&needsRedirect=false&jan1offset=240&jun1offset=240"
    )

    # Wait for the job listings table to be present
    wait = WebDriverWait(driver, 20)  # Increase the timeout if needed
    job_table = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "iCIMS_JobsTable"))
    )

    # Print the page source to verify the content
    print(driver.page_source)

    # Use XPath to find job listings
    job_listings = job_table.find_elements(
        By.XPATH, ".//div[contains(@class, 'row')]"
    )  # Adjust the XPath as needed

    for job in job_listings:
        try:
            title_element = job.find_element(
                By.XPATH, ".//div[contains(@class, 'title')]"
            )
            location_element = job.find_element(
                By.XPATH, ".//div[contains(@class, 'location')]"
            )
            title = title_element.text if title_element else "N/A"
            location = location_element.text if location_element else "N/A"
            print(f"Job Title: {title}, Location: {location}")
        except Exception as job_e:
            print(f"Error extracting job details: {job_e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
