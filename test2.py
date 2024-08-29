import requests

# The IPv6 address with brackets
ipv6_address = "2606:4700:4400::ac40:930b"
url = f"https://[{ipv6_address}]"

# Make a GET request
response = requests.get(url)

# Print the status code and response text
print("Status Code:", response.status_code)
print("Response Text:", response.text)
