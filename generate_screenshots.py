#!/usr/bin/env python
"""
Generate UI screenshots for documentation.
"""

import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    """Set up Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def take_screenshot(driver, url, filename, wait_element=None):
    """Take a screenshot of a page."""
    driver.get(url)
    time.sleep(2)  # Wait for page to load
    
    if wait_element:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(wait_element)
            )
        except:
            pass
    
    screenshot_dir = 'screenshots'
    os.makedirs(screenshot_dir, exist_ok=True)
    
    filepath = os.path.join(screenshot_dir, filename)
    driver.save_screenshot(filepath)
    print(f"✓ Screenshot saved: {filepath}")
    return filepath


def generate_screenshots():
    """Generate all UI screenshots."""
    print("=" * 80)
    print("Generating UI Screenshots")
    print("=" * 80)
    
    # Start Flask app in background
    print("\nStarting Flask application...")
    flask_process = subprocess.Popen(
        ['python', '-m', 'app.web_app'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Flask to start
    time.sleep(5)
    
    try:
        driver = setup_driver()
        base_url = 'http://localhost:5000'
        
        print("\nCapturing screenshots...\n")
        
        # Home page
        take_screenshot(driver, base_url, '01_home.png')
        
        # Login page
        take_screenshot(driver, f'{base_url}/login', '02_login.png')
        
        # Login and navigate
        driver.get(f'{base_url}/login')
        driver.find_element(By.ID, 'user_id').send_keys('testuser')
        driver.find_element(By.ID, 'email').send_keys('test@example.com')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(2)
        
        # Dashboard
        take_screenshot(driver, f'{base_url}/dashboard', '03_dashboard.png')
        
        # Create KB page
        take_screenshot(driver, f'{base_url}/kb/create', '04_create_kb.png')
        
        print("\n" + "=" * 80)
        print("Screenshot generation complete!")
        print("Screenshots saved in ./screenshots/")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error generating screenshots: {e}")
    finally:
        driver.quit()
        flask_process.terminate()
        flask_process.wait()


if __name__ == '__main__':
    # Check if selenium and chromedriver are available
    try:
        from selenium import webdriver
        generate_screenshots()
    except ImportError:
        print("Selenium not installed. Install with: pip install selenium")
        print("Also ensure chromedriver is installed and in PATH")
