from selenium import webdriver
from bs4 import BeautifulSoup
import csv


# Function to scrape text with formatting
def scrape_website(url):
    # Initialize Selenium WebDriver
    driver = (
        webdriver.Chrome()
    )  # Or use any other WebDriver based on your browser choice
    driver.get(url)

    # Get the page source
    page_source = driver.page_source
    
    # Close the WebDriver
    driver.quit()
    soup = BeautifulSoup(page_source, "html.parser")
    main_content = soup.find(
        "span", class_="jobdescription"
    ) 

    # Extract text with formatting
    formatted_text = main_content.prettify()

    return formatted_text


# Function to save text to CSV
def save_to_csv(text, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Formatted Text"])
        writer.writerow([text])


# Example usage
url = "https://careers.olympusamerica.com/job/Center-Valley-Senior-Sales-Training-Manager%2C-Surgical-Solutions-Energy-&-Systems-Integration-PA-18034-0610/1168373900/"  # Replace with the URL of the website you want to scrape
formatted_text = scrape_website(url)
save_to_csv(formatted_text, "scraped_text.csv")
