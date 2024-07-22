import subprocess
import os
import sys

from uploader import upload_file

if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

scrapers = [
    'Amgen.py',
    'Tempus.py',
    'Abbott.py',
    'Abbvie.py',
    'AstraZeneca.py',
    'Baxter.py',
    'BBraun.py',
    'Becton.py',
    'Biogen.py',
    'Biomerieux.py',
    'BMS.py',
    'Boston.py',
    'Bruker.py',
    'Cardinal.py',
    'Danaher.py',
    'Eurofins.py',
    'ExactSciences.py',
    'Foundation.py',
    'Fresenius.py',
    'GE.py',
    'GSK.py',
    'Guardant.py',
    'Jhonsan.py',
    'Medline.py',
    'Medtronic.py',
    'Merck.py',
    'Moderna.py',
    'Natera.py',
    'NovoNordisk.py',
    'Olympus.py',
    'Pfizer.py',
    'Philips.py',
    'Quest.py',
    'QuidelOrtho.py',
    'Regeneron.py',
    'Revvity.py',
    'Roche.py',
    'Sanofi.py',
    'Siemens.py',
    'Sotera.py',
    'Stryker.py',
    'Takeda.py',
    'Tempus.py',
    'ThermoFisher.py',
    'Zimmer.py'
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
