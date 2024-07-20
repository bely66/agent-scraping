from bs4 import BeautifulSoup

# Read the HTML file
with open('html_data/1.html', 'r') as file:
    html_data = file.read()

# Create a BeautifulSoup object
soup = BeautifulSoup(html_data, 'html.parser')

# Find all div containers
div_containers = soup.find_all('div')

# find all divs containing data-component paymentDetails or shipments
# div_containers = soup.find_all('div', {'data-component': ['paymentDetails', 'shipments']})

# print length of div_containers
print(len(div_containers))

# print the concatenated text length of all div containers
print(len(''.join([container.text for container in div_containers]).split()))