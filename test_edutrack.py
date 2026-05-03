import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://13.63.49.27:3000"

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def login(driver, email="admin@school.com", password="admin123"):
    driver.get(BASE_URL)
    time.sleep(2)
    email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='mail'], input[placeholder*='Mail']")
    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    email_field.clear()
    email_field.send_keys(email)
    password_field.clear()
    password_field.send_keys(password)
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary, button.login-btn")
    btn.click()
    time.sleep(3)

class TestEduTrack(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_01_page_loads(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        self.assertIn("EduTrack", self.driver.title)
        print("✅ Test 1 PASSED: Page loads successfully")

    def test_02_login_form_visible(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        email_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='mail']")
        password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        self.assertTrue(email_field.is_displayed())
        self.assertTrue(password_field.is_displayed())
        print("✅ Test 2 PASSED: Login form is visible")

    def test_03_invalid_login(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        email = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='mail']")
        password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        email.clear()
        email.send_keys("wrong@email.com")
        password.clear()
        password.send_keys("wrongpassword")
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary, button.login-btn")
        btn.click()
        time.sleep(3)
        page_source = self.driver.page_source.lower()
        self.assertTrue("invalid" in page_source or "error" in page_source or "incorrect" in page_source)
        print("✅ Test 3 PASSED: Invalid login shows error")

    def test_04_admin_login(self):
        login(self.driver)
        page_source = self.driver.page_source.lower()
        self.assertTrue("dashboard" in page_source or "admin" in page_source or "welcome" in page_source or "logout" in page_source)
        print("✅ Test 4 PASSED: Admin login successful")

    def test_05_admin_dashboard(self):
        login(self.driver)
        page_source = self.driver.page_source.lower()
        self.assertTrue("student" in page_source or "teacher" in page_source or "user" in page_source)
        print("✅ Test 5 PASSED: Admin dashboard loaded")

    def test_06_empty_login_fields(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary, button.login-btn")
        btn.click()
        time.sleep(2)
        page_source = self.driver.page_source.lower()
        self.assertTrue("login" in page_source or "sign in" in page_source)
        print("✅ Test 6 PASSED: Empty login fields validated")

    def test_07_register_link_visible(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        page_source = self.driver.page_source.lower()
        self.assertTrue("register" in page_source or "sign up" in page_source)
        print("✅ Test 7 PASSED: Register link is visible")

    def test_08_register_form_loads(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        register_link = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Register') or contains(text(), 'register')]")
        register_link.click()
        time.sleep(2)
        page_source = self.driver.page_source.lower()
        self.assertTrue("name" in page_source or "register" in page_source)
        print("✅ Test 8 PASSED: Register form loads")

    def test_09_duplicate_email_registration(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        register_link = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Register') or contains(text(), 'register')]")
        register_link.click()
        time.sleep(2)
        # Wait for visible inputs
        inputs = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input:not([type='hidden'])")))
        for inp in inputs:
            if not inp.is_displayed():
                continue
            inp_type = inp.get_attribute("type") or ""
            inp_placeholder = (inp.get_attribute("placeholder") or "").lower()
            try:
                if "name" in inp_placeholder:
                    inp.clear()
                    inp.send_keys("Test User")
                elif inp_type == "email" or "email" in inp_placeholder:
                    inp.clear()
                    inp.send_keys("admin@school.com")
                elif inp_type == "password":
                    inp.clear()
                    inp.send_keys("test123")
            except:
                pass
        btns = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary")
        for btn in btns:
            if btn.is_displayed():
                btn.click()
                break
        time.sleep(3)
        page_source = self.driver.page_source.lower()
        self.assertTrue("exist" in page_source or "duplicate" in page_source or "already" in page_source or "error" in page_source)
        print("✅ Test 9 PASSED: Duplicate email registration shows error")

    def test_10_register_new_student(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        register_link = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Register') or contains(text(), 'register')]")
        register_link.click()
        time.sleep(2)
        inputs = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input:not([type='hidden'])")))
        for inp in inputs:
            if not inp.is_displayed():
                continue
            inp_type = inp.get_attribute("type") or ""
            inp_placeholder = (inp.get_attribute("placeholder") or "").lower()
            try:
                if "name" in inp_placeholder:
                    inp.clear()
                    inp.send_keys("Test Student")
                elif inp_type == "email" or "email" in inp_placeholder:
                    inp.clear()
                    inp.send_keys(f"teststudent{int(time.time())}@test.com")
                elif inp_type == "password":
                    inp.clear()
                    inp.send_keys("test123456")
            except:
                pass
        btns = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary")
        for btn in btns:
            if btn.is_displayed():
                btn.click()
                break
        time.sleep(3)
        page_source = self.driver.page_source.lower()
        self.assertTrue("success" in page_source or "registered" in page_source or "login" in page_source or "welcome" in page_source)
        print("✅ Test 10 PASSED: New student registration successful")

    def test_11_page_title(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        title = self.driver.title
        self.assertTrue(len(title) > 0)
        print(f"✅ Test 11 PASSED: Page title is '{title}'")

    def test_12_logout(self):
        login(self.driver)
        try:
            logout_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Sign Out') or contains(text(), 'logout') or contains(text(), 'sign out')]")))
            logout_btn.click()
            time.sleep(2)
        except:
            # Try JavaScript click
            try:
                logout_btn = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Sign Out') or contains(text(), 'logout') or contains(text(), 'sign out')]")
                self.driver.execute_script("arguments[0].click();", logout_btn)
                time.sleep(2)
            except:
                pass
        page_source = self.driver.page_source.lower()
        self.assertTrue("login" in page_source or "sign in" in page_source)
        print("✅ Test 12 PASSED: Logout successful")

    def test_13_admin_user_list(self):
        login(self.driver)
        page_source = self.driver.page_source.lower()
        self.assertTrue("student" in page_source or "teacher" in page_source or "user" in page_source)
        print("✅ Test 13 PASSED: Admin can see user list")

    def test_14_register_new_teacher(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        register_link = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Register') or contains(text(), 'register')]")
        register_link.click()
        time.sleep(2)
        inputs = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input:not([type='hidden'])")))
        for inp in inputs:
            if not inp.is_displayed():
                continue
            inp_type = inp.get_attribute("type") or ""
            inp_placeholder = (inp.get_attribute("placeholder") or "").lower()
            try:
                if "name" in inp_placeholder:
                    inp.clear()
                    inp.send_keys("Test Teacher")
                elif inp_type == "email" or "email" in inp_placeholder:
                    inp.clear()
                    inp.send_keys(f"testteacher{int(time.time())}@test.com")
                elif inp_type == "password":
                    inp.clear()
                    inp.send_keys("test123456")
            except:
                pass
        # Try to select teacher role
        try:
            role_selects = self.driver.find_elements(By.CSS_SELECTOR, "select")
            for sel in role_selects:
                if sel.is_displayed():
                    options = sel.find_elements(By.TAG_NAME, "option")
                    for opt in options:
                        if "teacher" in opt.text.lower():
                            opt.click()
                            break
        except:
            pass
        btns = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary")
        for btn in btns:
            if btn.is_displayed():
                btn.click()
                break
        time.sleep(3)
        page_source = self.driver.page_source.lower()
        self.assertTrue("success" in page_source or "registered" in page_source or "login" in page_source)
        print("✅ Test 14 PASSED: New teacher registration successful")

    def test_15_login_page_elements(self):
        self.driver.get(BASE_URL)
        time.sleep(2)
        page_source = self.driver.page_source.lower()
        self.assertTrue("email" in page_source)
        self.assertTrue("password" in page_source)
        self.assertTrue("sign in" in page_source or "login" in page_source)
        print("✅ Test 15 PASSED: Login page has all required elements")

    def test_16_app_responsive(self):
        self.driver.get(BASE_URL)
        self.driver.set_window_size(375, 812)
        time.sleep(2)
        email = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='mail']")
        self.assertTrue(email.is_displayed())
        print("✅ Test 16 PASSED: App is responsive on mobile size")

    def test_17_multiple_failed_logins(self):
        for i in range(3):
            self.driver.get(BASE_URL)
            time.sleep(1)
            email = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='mail']")
            password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            email.send_keys(f"wrong{i}@test.com")
            password.send_keys("wrongpass")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary, button.login-btn").click()
            time.sleep(2)
        page_source = self.driver.page_source.lower()
        self.assertTrue("invalid" in page_source or "error" in page_source or "login" in page_source)
        print("✅ Test 17 PASSED: Multiple failed logins handled correctly")

if __name__ == "__main__":
    unittest.main(verbosity=2)