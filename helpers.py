import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import re


def is_remote(job_description):
    remote_patterns = [
        r"\bremote\b",  
        r"\bwork from home\b", 
        r"\btelecommute\b", 
        r"\banywhere\b", 
        r"\bvirtual\b", 
        r"\bwork from anywhere\b", 
        r"\bdistributed team\b",  
    ]

    remote_regex = re.compile("|".join(remote_patterns), re.IGNORECASE)
    if remote_regex.search(job_description):
        return True
    else:
        return False


def configure_webdriver(
    open_browser=False, block_media=False, block_elements=["css", "img", "js"]
):
    options = webdriver.ChromeOptions()

    # Install the extension
    extension_path = "scraper/utils/pia.crx"

    if not open_browser:
        options.add_argument("--headless=new")
    if block_media:
        hide_elements = {
            "plugins": 2,
            "popups": 2,
            "geolocation": 2,
            "notifications": 2,
            "auto_select_certificate": 2,
            "fullscreen": 2,
            "mouselock": 2,
            "mixed_script": 2,
            "media_stream": 2,
            "media_stream_mic": 2,
            "media_stream_camera": 2,
            "protocol_handlers": 2,
            "ppapi_broker": 2,
            "automatic_downloads": 2,
            "midi_sysex": 2,
            "push_messaging": 2,
            "ssl_cert_decisions": 2,
            "metro_switch_to_desktop": 2,
            "protected_media_identifier": 2,
            "app_banner": 2,
            "site_engagement": 2,
            "durable_storage": 2,
        }
        if "cookies" in block_elements:
            hide_elements.update({"cookies": 2})
        if "js" in block_elements:
            hide_elements.update({"javascript": 2})
        if "img" in block_elements:
            hide_elements.update({"images": 2})
        prefs = {"profile.default_content_setting_values": hide_elements}
        options.add_argument("--disable-features=EnableNetworkService")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option("prefs", prefs)
    options.add_argument("window-size=1200,1100")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    )

    # options.add_extension(extension_path)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    if block_media:
        # Enable Chrome DevTools Protocol
        driver.execute_cdp_cmd("Page.enable", {})
        driver.execute_cdp_cmd("Network.enable", {})

        # Set blocked URL patterns to disable images and stylesheets
        blocked_patterns = []
        if "img" in block_elements:
            blocked_patterns.extend(
                [
                    "*.jpg",
                    "*.jpeg",
                    "*.png",
                    "*.gif",
                ]
            )
        if "css" in block_elements:
            blocked_patterns.extend(["*.css"])
        if "js" in block_elements:
            blocked_patterns.extend(["*.js"])
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": blocked_patterns})
    return driver


def configure_undetected_chrome_driver(open_browser=False):
    options = uc.ChromeOptions()
    my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    # extension_path = 'scraper/utils/extensions/pia-unpacked'
    if not open_browser:
        options.add_argument("--headless=new")
    options.add_argument(
        "--no-sandbox --no-first-run --no-service-autorun --password-store=basic"
    )
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    )
    options.add_experimental_option(
        "prefs",
        {
            "extensions.ui.developer_mode": True,
        },
    )
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(f"user-agent={my_user_agent}")
    # options.add_argument(f'--load-extension={extension_path}')
    driver = uc.Chrome(
        driver_executable_path=ChromeDriverManager().install(),
        options=options,
        use_subprocess=False,
    )
    return driver
