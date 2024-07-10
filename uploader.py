from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time

from helpers import configure_webdriver

def upload_files():
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


        data_folder = 'data'
        for filename in os.listdir(data_folder):
            driver.get("https://medsaleshub.mysmartjobboard.com/admin/jobs/import/")
            if filename.endswith(".csv"):
                file_path = os.path.join(data_folder, filename)
                absolute_file_path = os.path.abspath(file_path)
                file_input = driver.find_element(By.NAME, "import_file")
                file_input.send_keys(absolute_file_path)
                upload_button = driver.find_element(By.ID, "run-import")
                upload_button.click()
                time.sleep(5)

        print("All files uploaded successfully.")
    finally:
        driver.quit()