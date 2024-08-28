import subprocess
import os
import sys

from uploader import upload_file

if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

scrapers = [
    'Abbvie.py',
    'Amgen.py',
    'AstraZeneca.py', 
    'BMS.py',
    'Natera.py',
    'Guardant.py',
    'ExactSciences.py',
    'ThermoFisher.py',
    'Baxter.py',
    'Becton.py',
    'NovoNordisk.py',
    'Sanofi.py',
    'Boston.py',
    'Abbott.py',
    'Merck.py',
    'Jhonsan.py',
    'Stryker.py',
    'Medtronic.py'
]

def run_scraper(scraper):
    try:
        scraper_path = os.path.join(current_dir, scraper)
        result = subprocess.run(['python', scraper_path], check=True)
        print(f"{scraper} completed successfully.")
        upload_file(f'{scraper.split(".")[0]}.csv')
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {scraper}: {e}")
        return False

def main():
    for scraper in scrapers:
        try:
            run_scraper(scraper)
        except Exception as e:
            print(f"Exception occurred while running {scraper}: {e}")

if __name__ == "__main__":
    main()
