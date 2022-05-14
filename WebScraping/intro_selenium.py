# import relevant libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

import pandas as pd

#  website for extraction
website = 'https://www.adamchoi.co.uk/overs/detailed'

service = ChromeService(executable_path=ChromeDriverManager().install())
options = Options()

# Initialize driver and open webpage
driver = webdriver.Chrome(service=service, options=options)

driver.get(website)
driver.implicitly_wait(0.6)

all_matches_button = driver.find_element(by = By.XPATH, value="//label[@analytics-event='All matches']")
all_matches_button.click()

dropdown = Select(driver.find_element(by=By.ID, value='country'))
dropdown.select_by_visible_text('Spain')

# delay to allow driver load
time.sleep(3)

# Scrape the relevant data table
matches = driver.find_elements(by= By.TAG_NAME, value='tr')
date = []
home_team = []
away_team = []
result = []
for match in matches:
    date.append(match.find_element(by=By.XPATH, value='./td[1]').text)
    home_team.append(match.find_element(by=By.XPATH, value='./td[2]').text)
    result.append(match.find_element(by=By.XPATH, value='./td[3]').text)
    away_team.append(match.find_element(by=By.XPATH, value='./td[4]').text)

driver.quit()

# Save extracted data to .csv file
df = pd.DataFrame({'Date': date, 'home_team': home_team, 'Score': result, 'away_team': away_team})
df.to_csv('football_data.csv', index=False)

print(df)