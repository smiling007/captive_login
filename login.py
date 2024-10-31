import requests
import re

get_url = "http://connectivitycheck.gstatic.com/generate_204"
post_url = "https://netaccess.iitpkd.ac.in:1442/"

username = ""  # Enter username here
password = ""  # Enter password here

session = requests.Session()

# Send a GET request to the specified URL
try:
    response = session.get(get_url)
    response.raise_for_status()  # Check if the request was successful
except requests.exceptions.RequestException as e:
    print(f"Error while trying to access {get_url}: {e}\nNo Internet connection.")
    exit(1)  # Exit the script if the GET request fails

# Check for token in the response if the status code is not 204
match = re.search(r'"https://netaccess\.iitpkd\.ac\.in:1442/fgtauth\?([^"]+)', response.text)

if match:
    token = match.group(1)  # This will capture the token
    print(f"Token extracted: {token}")   
    
    # Construct the new URL for the GET request with the token
    get_url_with_token = f"https://netaccess.iitpkd.ac.in:1442/fgtauth?{token}"
    print(f"Requesting URL: {get_url_with_token}")
    
    # Send a GET request to the new URL
    try:
        response = session.get(get_url_with_token)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        print(f"Error while trying to access {get_url_with_token}: {e}")
        exit(1)  # Exit the script if the GET request fails

    # Check if the GET request was successful
    if response.status_code == 200:
        print("Successfully accessed the token URL.")
        
        # Define the payload with the required data
        payload = {
            'magic': token,
            'username': username,
            'password': password
        }
        
        # Send the POST request
        try:
            post_response = session.post(post_url, data=payload)
            post_response.raise_for_status()  # Check if the request was successful
            print(f"POST request sent. Response status code: {post_response.status_code}")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")  # Output error if it occurs
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")  # Output general request errors
    else:
        print(f"Failed to access the token URL, status code: {response.status_code}")
        print(response.text)  # Print response for debugging
else:
    print("Token not found in the response. Already Connected")