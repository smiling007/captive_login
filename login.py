import requests
import re
import os
import json
from cryptography.fernet import Fernet
import getpass

# Define the URLs
get_url = "http://connectivitycheck.gstatic.com/generate_204"
post_url = "https://netaccess.iitpkd.ac.in:1442/"

# Define the path for the credentials file in the user's home directory
home_directory = os.path.expanduser("~")
credentials_folder = os.path.join(home_directory, 'captive_login')
credentials_file = os.path.join(credentials_folder, 'credentials.json')

# Create the folder if it doesn't exist
os.makedirs(credentials_folder, exist_ok=True)

# Function to generate a key for encryption and decryption
def generate_key():
    return Fernet.generate_key()

# Function to save credentials to a file (encrypted)
def save_credentials(username, password):
    # Generate a key for encryption
    key = generate_key()
    cipher = Fernet(key)

    # Encrypt the credentials
    encrypted_username = cipher.encrypt(username.encode())
    encrypted_password = cipher.encrypt(password.encode())

    credentials = {
        'username': encrypted_username.decode(),  # Store as string
        'password': encrypted_password.decode(),  # Store as string
        'key': key.decode()  # Store the encryption key (not secure, but necessary here)
    }
    
    with open(credentials_file, 'w') as file:
        json.dump(credentials, file)

# Function to load credentials from a file (decrypted)
def load_credentials():
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as file:
            credentials = json.load(file)
            # Use the stored key for decryption
            cipher = Fernet(credentials['key'].encode())
            username = cipher.decrypt(credentials['username'].encode()).decode()
            password = cipher.decrypt(credentials['password'].encode()).decode()
            return username, password
    return None, None

# Load credentials if they exist
username, password = load_credentials()

# If no credentials are found, ask for them
if username is None or password is None:
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")  # Secure password input
    
    # Save the credentials for future use
    save_credentials(username, password)

# Use a session for better management of requests
session = requests.Session()

## Step 1: Send a GET request to the specified URL
try:
    response = session.get(get_url)
    response.raise_for_status()  # Check if the request was successful
except requests.exceptions.RequestException as e:
    print(f"Error while trying to access {get_url}: {e}\nNo Internet connection.")
    exit(1)  # Exit the script if the GET request fails

# Check if the response was successful
if response.status_code != 204:
    # Step 2: Look for the token in the response
    match = re.search(r'"https://netaccess\.iitpkd\.ac\.in:1442/fgtauth\?([^"]+)', response.text)

    if match:
        token = match.group(1)  # This will capture the token
        print(f"Token (magic key) extracted: {token}")
        
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
                'magic': token,  # Use the extracted token
                'username': username,  # Use loaded username
                'password': password   # Use loaded password
            }

            # Send the POST request
            try:
                post_response = session.post(post_url, data=payload)

                # Check if the request was successful
                post_response.raise_for_status()  # Raises an HTTPError for bad responses

                # Print the status code and response content
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
        # print(response.text)  # Print response for debugging
else:
    print(f"No Captive Portal, status code: {response.status_code}")
    print(response.text)  # Print response for debugging
