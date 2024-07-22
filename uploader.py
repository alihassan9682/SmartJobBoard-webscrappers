from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time

from helpers import configure_webdriver

def upload_file(csv_filename):
    driver = configure_webdriver(True)

    try:
        driver.get("https://medsaleshub.mysmartjobboard.com/admin/")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.ID, "loginButton")

        username_field.send_keys("alihassan9682@gmail.com")
        password_field.send_keys("laptop96")
        login_button.click()

        time.sleep(5)

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
