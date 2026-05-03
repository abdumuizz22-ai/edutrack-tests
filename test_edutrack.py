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
    driver.implicitly_wait(5)
    return driver


class TestEduTrack(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def tearDown(self):
        self.driver.quit()

    # 🔹 Utility functions (IMPORTANT)
    def wait_and_send(self, locator, value):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
        el.clear()
        el.send_keys(value)

    def wait_and_click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
        el.click()

    # ─────────────────────────────────────────────────────────

    def test_01_page_loads(self):
        self.driver.get(BASE_URL)
        self.assertIn("EduTrack", self.driver.title)

    def test_02_login_form_visible(self):
        self.driver.get(BASE_URL)
        email = self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[type='email']")))
        password = self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[type='password']")))
        self.assertTrue(email.is_displayed())
        self.assertTrue(password.is_displayed())

    def test_03_invalid_login(self):
        self.driver.get(BASE_URL)

        self.wait_and_send((By.CSS_SELECTOR, "input[type='email']"), "wrong@email.com")
        self.wait_and_send((By.CSS_SELECTOR, "input[type='password']"), "wrongpassword")
        self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertTrue("invalid" in page or "error" in page)

    def test_04_admin_login(self):
        self.driver.get(BASE_URL)

        self.wait_and_send((By.CSS_SELECTOR, "input[type='email']"), "admin@school.com")
        self.wait_and_send((By.CSS_SELECTOR, "input[type='password']"), "admin123")
        self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertTrue("dashboard" in page or "welcome" in page)

    def test_05_admin_dashboard(self):
        self.test_04_admin_login()
        page = self.driver.page_source.lower()
        self.assertTrue("student" in page or "teacher" in page)

    def test_06_empty_login_fields(self):
        self.driver.get(BASE_URL)
        self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        page = self.driver.page_source.lower()
        self.assertTrue("required" in page or BASE_URL in self.driver.current_url)

    def test_07_register_link_visible(self):
        self.driver.get(BASE_URL)
        page = self.driver.page_source.lower()
        self.assertTrue("register" in page or "sign up" in page)

    def test_08_register_form_loads(self):
        self.driver.get(BASE_URL)
        self.wait_and_click((By.XPATH, "//*[contains(text(),'Register') or contains(text(),'Sign')]"))

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input")))
        page = self.driver.page_source.lower()
        self.assertTrue("register" in page or "name" in page)

    def fill_register_form(self, name, email, password, role=None):
        inputs = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input")))

        for inp in inputs:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", inp)
            inp_type = inp.get_attribute("type")
            placeholder = (inp.get_attribute("placeholder") or "").lower()

            if "name" in placeholder:
                inp.send_keys(name)
            elif inp_type == "email":
                inp.send_keys(email)
            elif inp_type == "password":
                inp.send_keys(password)

        if role:
            selects = self.driver.find_elements(By.CSS_SELECTOR, "select")
            for sel in selects:
                options = sel.find_elements(By.TAG_NAME, "option")
                for opt in options:
                    if role.lower() in opt.text.lower():
                        opt.click()

    def test_09_duplicate_email_registration(self):
        self.driver.get(BASE_URL)
        self.wait_and_click((By.XPATH, "//*[contains(text(),'Register')]"))

        self.fill_register_form("Test User", "admin@school.com", "test123")

        self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        page = self.driver.page_source.lower()
        self.assertTrue("exist" in page or "already" in page or "error" in page)

    def test_10_register_new_student(self):
        self.driver.get(BASE_URL)
        self.wait_and_click((By.XPATH, "//*[contains(text(),'Register')]"))

        email = f"student{int(time.time())}@test.com"
        self.fill_register_form("Student", email, "test123")

        self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        page = self.driver.page_source.lower()
        self.assertTrue("success" in page or "login" in page or "registered" in page)

    def test_11_page_title(self):
        self.driver.get(BASE_URL)
        self.assertTrue(len(self.driver.title) > 0)

    def test_12_logout(self):
        self.test_04_admin_login()

        self.wait_and_click((By.XPATH, "//*[contains(text(),'Logout') or contains(text(),'Sign Out')]"))

        page = self.driver.page_source.lower()
        self.assertTrue("login" in page or "sign in" in page)

    def test_13_admin_user_list(self):
        self.test_04_admin_login()
        page = self.driver.page_source.lower()
        self.assertTrue("student" in page or "teacher" in page)

    def test_14_register_new_teacher(self):
        self.driver.get(BASE_URL)
        self.wait_and_click((By.XPATH, "//*[contains(text(),'Register')]"))

        email = f"teacher{int(time.time())}@test.com"
        self.fill_register_form("Teacher", email, "test123", role="teacher")

        self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        page = self.driver.page_source.lower()
        self.assertTrue("success" in page or "registered" in page)

    def test_15_login_page_elements(self):
        self.driver.get(BASE_URL)
        page = self.driver.page_source.lower()
        self.assertTrue("email" in page)
        self.assertTrue("password" in page)

    def test_16_app_responsive(self):
        self.driver.get(BASE_URL)
        self.driver.set_window_size(375, 812)

        email = self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[type='email']")))
        self.assertTrue(email.is_displayed())

    def test_17_multiple_failed_logins(self):
        for i in range(3):
            self.driver.get(BASE_URL)
            self.wait_and_send((By.CSS_SELECTOR, "input[type='email']"), f"wrong{i}@test.com")
            self.wait_and_send((By.CSS_SELECTOR, "input[type='password']"), "wrong")
            self.wait_and_click((By.CSS_SELECTOR, "button[type='submit']"))

        page = self.driver.page_source.lower()
        self.assertTrue("invalid" in page or "error" in page)


if __name__ == "__main__":
    unittest.main(verbosity=2)