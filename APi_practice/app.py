import requests

url = "https://api.github.com"

response = (requests.get(url))
print(response.status_code)

url_invalid = 'https://api.github.com/invalid'

response_2 = requests.get(url_invalid)

print(response_2) 