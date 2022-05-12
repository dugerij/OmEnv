import lxml
from bs4 import BeautifulSoup
import requests

url = "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation= "
html_text = requests.get(url).text

soup = BeautifulSoup(html_text, 'lxml')
job = soup.find('li', class_='clearfix job-bx wht-shd-bx')
company_name = job.find('h3', class_="joblist-comp-name").text.replace('  ', '')
skills = job.find('span', 'srp-skills').text.replace('  ', '')
published_date = job.find('span',  class_="sim-posted").text
print(published_date)
# print(f'''
# Company Name: {company_name},
# Required Skills: {skills}
# ''')