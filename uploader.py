from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

from helpers import configure_webdriver

driver = configure_webdriver(True)

def delete_existing_file(filename):
    try:
        driver.get("https://medsaleshub.mysmartjobboard.com/admin/employers/")
        time.sleep(5)
        company = filename.split('.')[0]

        filter_dropdown = driver.find_element(By.CLASS_NAME, "btn-dropdown")
        filter_dropdown.click()
        time.sleep(2)

        filter_input = driver.find_element(By.CSS_SELECTOR, "[aria-labelledby='select2-company-container']")
        filter_input.click()
        search_input = driver.find_element(By.CLASS_NAME, "select2-search__field")
        if search_input:
            search_input.send_keys(company)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
        filter_form = driver.find_element(By.XPATH, "//form[@name='search_form']")
        filter_form.submit()
        time.sleep(5)

        try:
            table_body = driver.find_element(By.XPATH, "//table[@class='table table-striped with-bulk']/tbody")
            rows = table_body.find_elements(By.TAG_NAME, "tr")
            if len(rows) == 0:
                print("No results found.")
                return

            first_th = driver.find_element(By.XPATH, "//table[@class='table table-striped with-bulk']/thead/tr/th[1]")
            checkbox_f = first_th.find_element(By.CLASS_NAME, 'fa')
            checkbox_f.click()
            time.sleep(2)

            delete_button = driver.find_element(By.XPATH, "//button[@class='btn btn-default bulk-action' and @data-action='delete']")
            delete_button.click()
            time.sleep(2)

            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(5)
            print(f"Company '{company}' records deleted successfully.")

        except Exception as e:
            print(f"Error while processing results: {e}")
    except Exception as e:
        print(f"Error while deleting the file: {e}")

def upload_file(csv_filename):

    try:
        driver.get("https://medsaleshub.mysmartjobboard.com/admin/")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.ID, "loginButton")

        username_field.send_keys("alihassan9682@gmail.com")
        password_field.send_keys("laptop96")
        login_button.click()

        time.sleep(5)
        delete_existing_file(csv_filename)
        driver.get("https://medsaleshub.mysmartjobboard.com/admin/jobs/import/")
        file_path = os.path.join('data', csv_filename)
        absolute_file_path = os.path.abspath(file_path)
        if os.path.exists(absolute_file_path):
            file_input = driver.find_element(By.NAME, "import_file")
            file_input.send_keys(absolute_file_path)
            time.sleep(2)
            upload_button = driver.find_element(By.ID, "run-import")
            upload_button.click()
            time.sleep(2)
            upload_button = driver.find_element(By.ID, "run-import")
            upload_button.click()
            time.sleep(5)
            print(f"File '{csv_filename}' uploaded successfully.")
        else:
            print(f"File '{csv_filename}' not found.")

    finally:
        driver.quit()
