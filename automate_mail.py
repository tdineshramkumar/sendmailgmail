
"""
This python script automates sending E-Mail via gmail using selenium framework
NOTE: 
    1. Current Script takes input via standard input 
    2. To fully automate take input from command line arguments  
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from getpass import getpass
import time
import logging

# Take User Inputs from Standard Inputs
# To automate either hard code them or take from CLI
username = input("Username: ")
password = getpass("Password({}): ".format(username))
to = input("To: ")
subject = input("Subject: ")
message_body = input("Message Body: ")

# Configure Wait Time Out
WAIT_TIMEOUT = 100   # seconds
EXIT_TIMEOUT = 5     # seconds
# Configure LOGGER
logging.basicConfig(level=logging.INFO, format="%(asctime)s:LINE %(lineno)d:%(name)s:%(levelname)s: %(message)s ")
logger = logging.getLogger("G-MAIL")

# Open Firefox 
driver = webdriver.Firefox()    
logger.info("Opened Firefox")
try:
    # Visit www.gmail.com
    driver.get("http://www.gmail.com")  # Open GMAIL
    logger.info("Opened Gmail")

    # Enter username details and click next
    driver.find_element_by_id("identifierId").send_keys(username)
    # driver.find_element_by_id('identifierNext').click()
    driver.find_element_by_id("identifierId").send_keys(Keys.ENTER)
    logger.info("Entered Username Details")

    # Wait for password page to load
    # Then enter password and click next
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.visibility_of_element_located((By.NAME, "password")))
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_name("password").send_keys(Keys.ENTER)
    # driver.find_element_by_id("passwordNext").click()
    logger.info("Entered Password Details")

    # Wait for COMPOSE button to load and then click it
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".T-I-KE")))
    driver.find_element_by_css_selector('.T-I-KE').click()
    logger.info("Clicked Compose")

    # Wait till New Message window opens
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.visibility_of_element_located((By.NAME, "to")))
    # Enter the To, Subject and Message
    driver.find_element_by_name('to').send_keys(to)
    driver.find_element_by_name("subjectbox").send_keys(subject)
    driver.find_element_by_xpath("(.//*[@aria-label='Message Body'])[2]").send_keys(message_body)
    logger.info("Entered To, Subject and Message")

    # Send the message
    driver.find_element_by_class_name("aoO").click()
    logger.info("Sending the message")

finally:
    time.sleep(EXIT_TIMEOUT)
    driver.close()
    logger.info("Closing the browser")
