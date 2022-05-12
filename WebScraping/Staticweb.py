import requests

url = 'https://www.indeed.com/jobs?q=python&l=new+york/'

response = requests.get(url)

print(response.content[111190:111350])

loc = str(response.content).find('python')
print(loc)


print(response.content[loc-10:loc+10])

import re
print(len(re.findall(r'python', str(response.content)))) 