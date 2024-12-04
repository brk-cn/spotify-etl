from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os

load_dotenv()

class SeleniumLoginHandler:
    def __init__(self):
        self.username = os.getenv("SPOTIFY_USERNAME")
        self.password = os.getenv("SPOTIFY_PASSWORD")
        self.url = "http://127.0.0.1:8888/"

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        try:
            driver.get(self.url)

            login_spotify_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Login with Spotify")))
            login_spotify_button.click()

            username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-password")))
            username_field.send_keys(os.getenv("SPOTIFY_USERNAME"))
            password_field.send_keys(os.getenv("SPOTIFY_PASSWORD"))

            login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "login-button")))
            login_button.click()

            auth_accept = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="auth-accept"]')))
            auth_accept.click()

        except Exception as e:
            print(e)