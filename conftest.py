import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost/DamnCRUD-main")

@pytest.fixture(scope="function")
def driver():
    """
    Fixture WebDriver Chrome — dibuat fresh untuk setiap test function
    agar test benar-benar terisolasi satu sama lain (tidak berbagi sesi/cookies)
    """
    options = Options()
    options.add_argument("--headless")              # wajib di CI/CD (tidak ada display)
    options.add_argument("--no-sandbox")            # wajib di GitHub Actions runner
    options.add_argument("--disable-dev-shm-usage") # cegah crash di container
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    yield driver  # berikan driver ke test

    # Teardown: tutup browser setelah setiap test selesai
    driver.quit()


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """
    Fixture turunan: driver yang sudah dalam kondisi login.
    Digunakan oleh test yang membutuhkan autentikasi.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    import time

    driver.get(f"{BASE_URL}/login.php")
    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("nimda666!" + Keys.RETURN)
    time.sleep(2)

    yield driver


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL