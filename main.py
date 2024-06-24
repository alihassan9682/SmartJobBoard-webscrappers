import subprocess

scrapers = [
    'Abbott.py',
    'Abbvie.py',
    'Amgen.py',
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
    'Lantheus.py',
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
        result = subprocess.run(['python', scraper], check=True)
        print(f"{scraper} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {scraper}: {e}")
        return False

def main():
    for scraper in scrapers:
        success = run_scraper(scraper)
        if not success:
            print(f"Stopping execution. {scraper} failed.")
            break

if __name__ == "__main__":
    main()
