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
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver


class TestEduTrack(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, 15)

    def tearDown(self):
        self.driver.quit()

    # 🔧 Helper functions
    def wait_input(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_click(self, locator):
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", el)

    def login(self, email_val, pass_val):
        self.driver.get(BASE_URL)

        email = self.wait_input((By.CSS_SELECTOR, "input[type='email']"))
        password = self.wait_input((By.CSS_SELECTOR, "input[type='password']"))

        email.clear()
        email.send_keys(email_val)

        password.clear()
        password.send_keys(pass_val)

        self.wait_click((By.CSS_SELECTOR, "button[type='submit']"))
        time.sleep(2)

    def open_register(self):
        self.driver.get(BASE_URL)
        self.wait_click((By.XPATH, "//*[contains(text(),'Register') or contains(text(),'Sign')]"))
        time.sleep(1)

    def fill_register(self, name, email_val, password_val):
        inputs = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input")))

        for inp in inputs:
            if not inp.is_displayed():
                continue

            t = inp.get_attribute("type")
            placeholder = (inp.get_attribute("placeholder") or "").lower()

            try:
                if "name" in placeholder:
                    inp.send_keys(name)
                elif t == "email":
                    inp.send_keys(email_val)
                elif t == "password":
                    inp.send_keys(password_val)
            except:
                pass

    # ✅ TESTS

    def test_01_page_loads(self):
        self.driver.get(BASE_URL)
        self.assertIn("EduTrack", self.driver.title)

    def test_02_login_form_visible(self):
        self.driver.get(BASE_URL)
        self.assertTrue(self.wait_input((By.CSS_SELECTOR, "input[type='email']")).is_displayed())
        self.assertTrue(self.wait_input((By.CSS_SELECTOR, "input[type='password']")).is_displayed())

    def test_03_invalid_login(self):
        self.login("wrong@test.com", "wrong123")
        self.assertIn("invalid", self.driver.page_source.lower())

    def test_04_admin_login(self):
        self.login("admin@school.com", "admin123")
        self.assertTrue("dashboard" in self.driver.page_source.lower())

    def test_05_admin_dashboard(self):
        self.login("admin@school.com", "admin123")
        self.assertTrue("student" in self.driver.page_source.lower())

    def test_06_empty_login(self):
        self.driver.get(BASE_URL)
        self.wait_click((By.CSS_SELECTOR, "button[type='submit']"))
        self.assertTrue("login" in self.driver.page_source.lower())

    def test_07_register_link(self):
        self.driver.get(BASE_URL)
        self.assertIn("register", self.driver.page_source.lower())

    def test_08_register_form(self):
        self.open_register()
        self.assertIn("register", self.driver.page_source.lower())

    def test_09_duplicate_email(self):
        self.open_register()
        self.fill_register("Test", "admin@school.com", "test123")
        self.wait_click((By.CSS_SELECTOR, "button[type='submit']"))
        self.assertTrue("exist" in self.driver.page_source.lower())

    def test_10_new_student(self):
        self.open_register()
        email = f"user{int(time.time())}@test.com"
        self.fill_register("Student", email, "test123")
        self.wait_click((By.CSS_SELECTOR, "button[type='submit']"))
        self.assertTrue("success" in self.driver.page_source.lower() or "login" in self.driver.page_source.lower())

    def test_11_title(self):
        self.driver.get(BASE_URL)
        self.assertTrue(len(self.driver.title) > 0)

    def test_12_logout(self):
        self.login("admin@school.com", "admin123")
        self.wait_click((By.XPATH, "//*[contains(text(),'Logout')]"))
        self.assertIn("login", self.driver.page_source.lower())

    def test_13_user_list(self):
        self.login("admin@school.com", "admin123")
        self.assertTrue("student" in self.driver.page_source.lower())

    def test_14_teacher_register(self):
        self.open_register()
        email = f"teacher{int(time.time())}@test.com"
        self.fill_register("Teacher", email, "test123")
        self.wait_click((By.CSS_SELECTOR, "button[type='submit']"))
        self.assertTrue("success" in self.driver.page_source.lower())

    def test_15_elements(self):
        self.driver.get(BASE_URL)
        page = self.driver.page_source.lower()
        self.assertIn("email", page)
        self.assertIn("password", page)

    def test_16_responsive(self):
        self.driver.get(BASE_URL)
        self.driver.set_window_size(375, 812)
        self.assertTrue(self.wait_input((By.CSS_SELECTOR, "input[type='email']")).is_displayed())

    def test_17_multiple_failed(self):
        for _ in range(3):
            self.login("wrong@test.com", "wrong")
        self.assertIn("invalid", self.driver.page_source.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)