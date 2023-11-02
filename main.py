import requests

# LinkedIn API endpoints
API_URL = 'https://api.linkedin.com/v2'
SEARCH_URL = f'{API_URL}/people-search'
CONNECTIONS_URL = f'{API_URL}/people/URN/connections'
LOCATIONS_URL = f'{API_URL}/geoRegions?q='

# Your LinkedIn API credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
ACCESS_TOKEN = 'your_access_token'

# Accept user input for the search query and locations
search_query = input("Enter the search query (e.g., 'Python Flask developer'): ")
locations = input("Enter the locations (e.g., 'New York Metropolitan Area,Chicago'): ").split(',')

# Set up the headers, including the access token
headers = {
    "Authorization": f'Bearer {ACCESS_TOKEN}',
    "Content-Type": "application/json",
}

# Iterate through the list of locations
for location_name in locations:
    location_name = location_name.strip()

    # Find the location code for the specified location
    locations_response = requests.get(LOCATIONS_URL + location_name, headers=headers)

    if locations_response.status_code == 200:
        locations_data = locations_response.json()

        # Find the location code for the specified location
        location_code = None
        for location in locations_data.get('elements', []):
            if location_name.lower() in location.get('localizedName', '').lower():
                location_code = location.get('entityUrn', '')
                break

        if location_code:
            # Define the search query and location in the search query parameters
            search_query_params = {
                "origin": "AUTOCOMPLETE_ORIGIN_OTHER",
                "keywords": search_query,
                "facetGeoRegion": [location_code],
            }

            # Perform the search
            search_response = requests.get(SEARCH_URL, headers=headers, params=search_query_params)

            if search_response.status_code == 200:
                search_results = search_response.json()

                # Extract and iterate through the search results
                for result in search_results.get('elements', []):
                    # Extract the URN of the matching user
                    user_urn = result.get('targetUrn', None)

                    if user_urn:
                        # Define the connection request data
                        connection_request_data = {
                            "recipients": [
                                {"person": {"_path": f'/people/{user_urn}'}
                            }],
                            "message": {
                                "subject": "Connect with me on LinkedIn",
                                "body": "Hi, I'd like to connect with you on LinkedIn."
                            }
                        }

                        # Send the connection request
                        connection_response = requests.post(CONNECTIONS_URL.replace("URN", user_urn), headers=headers, json=connection_request_data)

                        if connection_response.status_code == 201:
                            print(f"Connection request sent successfully to {user_urn} in {location_name}")
                        else:
                            print(f"Error sending connection request to {user_urn}: {connection_response.status_code} - {connection_response.text}")
            else:
                print(f"Error with search request in {location_name}: {search_response.status_code} - {search_response.text}")
        else:
            print(f"Location code for '{location_name}' not found.")
    else:
        print(f"Error with location code search for {location_name}: {locations_response.status_code} - {locations_response.text}")
