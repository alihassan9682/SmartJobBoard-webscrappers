import subprocess
import os
import sys

from uploader import upload_file

if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))


scrapers = [

    # 'AmplityHealth.py',
    # 'Amgen.py',
    # 'Jhonsan.py',
    # 'Abbott.py',
    # 'Abbvie.py',
    # 'AstraZeneca.py',
    # 'Baxter.py',
    # 'Becton.py',
    # 'BMS.py',
    # 'BostonScientific.py',
    # 'ExactSciences.py',
    # 'Guardant.py',
    # 'Medtronic.py',
    # 'Merck.py',
    # 'NovoNordisk.py',
    # 'Eisai.py',
    # 'EVERSANA.py',
    # 'TeleFlex.py',
    # 'Sanofi.py',
    # 'Stryker.py',
    # 'ThermoFisher.py',
    # 'Conmed.py',
    # 'NeoGenomics.py',
    # 'BD.py',
    # 'Syneo.py',
     'IQVIA.py',
    # 'Myriad.py',
    # 'EliLilly.py',
    # 'Lantheus.py',
    # 'B Braun.py',
    #'Biogen.py',
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