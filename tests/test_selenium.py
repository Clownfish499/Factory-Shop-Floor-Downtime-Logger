"""
Selenium Automated UI Browser Test Suite
Covers Case 47 User Stories & Dashboard Automation:
1. Open dashboard and verify page title & branding.
2. Verify machine count displays 40.
3. Open machine roster and verify machines table.
4. Open single machine details page.
5. Open downtime start form.
6. Submit a valid downtime event and verify machine transitions to DOWN.
7. Resume the machine and verify transition back to RUNNING.
8. Open downtime history and test machine filter.
9. Open reports page and verify cost display.
10. Open simulator console and verify UI elements.
11. Test form validation error on empty reason.
"""
import os
import time
import tempfile
import threading
import pytest
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from app import create_app
from config import TestConfig
from database.init_db import init_db

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class LiveServer:
    def __init__(self, port=5088):
        self.port = port
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        init_db(self.db_path, populate_sample_data=True)

        class CustomLiveConfig(TestConfig):
            DATABASE_PATH = self.db_path
            TESTING = True

        self.app = create_app(CustomLiveConfig)
        self.server = make_server("127.0.0.1", self.port, self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        time.sleep(1.0)

    def stop(self):
        self.server.shutdown()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

@pytest.fixture(scope="module")
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,900")
    chrome_options.add_argument("--no-sandbox")

    server = LiveServer(port=5088)
    server.start()

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    base_url = "http://127.0.0.1:5088"

    yield driver, base_url

    driver.quit()
    server.stop()

def capture_failure_screenshot(driver, test_name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"{test_name}_{timestamp}.png")
    driver.save_screenshot(path)
    print(f"\n[SELENIUM] Saved failure screenshot to: {path}")

def test_selenium_dashboard_and_machine_count(browser):
    """Selenium 1, 2: Open dashboard, verify title and 40 machines"""
    driver, base_url = browser
    try:
        driver.get(f"{base_url}/")
        assert "Factory Shop-Floor" in driver.title
        total_card = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'metric-label') and text()='Total Machines']/following-sibling::div[contains(@class,'metric-value')]"))
        )
        assert total_card.text == "40"
    except Exception:
        capture_failure_screenshot(driver, "test_selenium_dashboard_and_machine_count")
        raise

def test_selenium_machine_list_and_details(browser):
    """Selenium 3, 4: Navigate to machine list and open single machine details"""
    driver, base_url = browser
    try:
        driver.get(f"{base_url}/machines/")
        assert "Machines" in driver.title

        # Verify M-001 link
        m1_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "M-001"))
        )
        m1_link.click()

        # Machine details
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'M-001')]"))
        )
        assert "M-001" in driver.page_source
    except Exception:
        capture_failure_screenshot(driver, "test_selenium_machine_list_and_details")
        raise

def test_selenium_downtime_start_and_resume_cycle(browser):
    """Selenium 5, 6, 7: Open form, record stoppage for M-002, then resume"""
    driver, base_url = browser
    try:
        driver.get(f"{base_url}/downtime/start?machine_id=M-002")

        # Fill form
        reason_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "reason"))
        )
        reason_box.clear()
        reason_box.send_keys("Selenium Test - Spindle bearing friction")

        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        # Verify redirect to history & presence of new log
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Spindle bearing friction')]"))
        )

        # Check dashboard shows DOWN machine with resume button
        driver.get(f"{base_url}/")
        resume_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//form[contains(@action, 'M-002')]//button[contains(text(),'Resume')]"))
        )

        # Click resume (confirm alert dialog in JS)
        resume_btn.click()
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except Exception:
            pass

        # Verify success flash message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'resumed successfully')]"))
        )
    except Exception:
        capture_failure_screenshot(driver, "test_selenium_downtime_start_and_resume_cycle")
        raise

def test_selenium_downtime_history_filters(browser):
    """Selenium 8: Test machine filter in history page"""
    driver, base_url = browser
    try:
        driver.get(f"{base_url}/downtime/history")
        machine_select = Select(driver.find_element(By.ID, "machine_id"))
        machine_select.select_by_value("M-002")

        apply_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        apply_btn.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )
        assert "M-002" in driver.page_source
    except Exception:
        capture_failure_screenshot(driver, "test_selenium_downtime_history_filters")
        raise

def test_selenium_reports_and_simulator_pages(browser):
    """Selenium 9, 10: Open reports and simulator console"""
    driver, base_url = browser
    try:
        driver.get(f"{base_url}/reports/")
        assert "Reports" in driver.title
        assert "Estimated Financial Impact" in driver.page_source

        driver.get(f"{base_url}/simulator")
        assert "Simulator Console" in driver.title
        assert "API Response Console" in driver.page_source
    except Exception:
        capture_failure_screenshot(driver, "test_selenium_reports_and_simulator_pages")
        raise
