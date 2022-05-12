import requests

url = 'https://api.github.com/'

response = requests.get(url)

if response:
    print('Success!')
else:
    print('Not found. An Error occured')