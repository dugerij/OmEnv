from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

website = 'https://www.adamchoi.co.uk/overs/detailed'
options = Options()
driver = webdriver.Chrome(options=options)
driver.get(website)

driver.quit()