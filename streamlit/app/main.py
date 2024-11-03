import streamlit as st
import pandas as pd
import json
import requests
import datetime
import os

# Get the current script directory (absolute path)
current_dir = os.path.dirname(os.path.abspath(__file__))

airports = {
    "Atlanta (ATL)": "ATL",
    "Boston (BOS)": "BOS",
    "Denver (DEN)": "DEN",
    "Dallas/Fort Worth (DFW)": "DFW",
    "Newark (EWR)": "EWR",
    "New York (JFK)": "JFK",
    "Los Angeles (LAX)": "LAX",
    "New York LaGuardia (LGA)": "LGA",
    "Miami (MIA)": "MIA",
    "Oakland (OAK)": "OAK",
    "Chicago O'Hare (ORD)": "ORD",
    "Philadelphia (PHL)": "PHL",
    "San Francisco (SFO)": "SFO"
}

#FASTAPI_URL = "https://at2-api.onrender.com"

# Title of the application
st.title(":heavy_check_mark: Save your flight budget")

st.sidebar.header("Flight Details")

# User inputs for flight details
origin_name = st.sidebar.selectbox("Choose origin airport", list(airports.keys()))
origin_code = airports[origin_name]

# Filter out the selected origin for the destination options
destination_options = {name: code for name, code in airports.items() if code != origin_code}

# Destination select box
destination_name = st.sidebar.selectbox("Choose destination airport", list(destination_options.keys()))
destination_code = destination_options[destination_name]

departure_date = st.sidebar.date_input("Enter Departure Date")
departure_time = st.sidebar.time_input("Enter Departure Time")
show_direct = st.sidebar.checkbox("Direct Flights Only", value=True)
show_one_transfer = st.sidebar.checkbox("Allow One Transfer", value=False)

cabin_type = st.sidebar.selectbox("Select Cabin Type", ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"])

# Your prediction function here
#def predict_price(origin, destination, departure_date, departure_time, cabin_type):
 #   # Mock prediction for illustration; replace with your actual model prediction
  #  return 300  # Example predicted price


def get_access_token(client_id, client_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("Access token:", access_token)  # Just for debugging; avoid printing sensitive info in production.
        return access_token
    else:
        print("Error:", response.status_code, response.text)
        return None

# Replace with your actual credentials
client_id = "ZApIceZDoh7BzhlUEIuZxCGQF3iWhKLH"
client_secret = "mrYPZDKlPbaEUrVm"
access_token = get_access_token(client_id, client_secret)



# API call to retrieve actual price
def get_actual_price(access_token, origin, destination, departure_date, cabin_type):
    # Placeholder for API URL and parameters
    url = f"https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": 1,  # Adjust based on your requirements
        "travelClass" : cabin_type,
        "currencyCode" : 'USD'
    }
    response = requests.get(url, headers=headers, params=params)
    
    # Parse response if successful
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None


if st.sidebar.button("Compare Prices"):
    if origin_code and destination_code and departure_date and departure_time and cabin_type and access_token:
        # Define time window
        time_window = datetime.timedelta(minutes=60)
        lower_bound = datetime.datetime.combine(departure_date, departure_time) - time_window
        upper_bound = datetime.datetime.combine(departure_date, departure_time) + time_window

        # Make API call to get actual prices
        actual_price = get_actual_price(access_token, origin_code, destination_code, departure_date, cabin_type)

        # Error handling for the API response
        if actual_price is None or 'data' not in actual_price:
            st.error("Failed to retrieve data from the API. Please check your request parameters.")
        else:
            # Create columns for side-by-side display
            col1, col2, col3 = st.columns(3)

            with col1:
                st.header("Actual Prices")
                
                filtered_offers = []
                
                for offer in actual_price.get('data', []):
                    for itinerary in offer.get('itineraries', []):
                        first_segment = itinerary.get('segments', [])[0]
                        segments = itinerary.get('segments', [])
                        is_direct = len(segments) == 1  # Check if it’s a direct flight

                        departure_time_str = first_segment['departure']['at']
                        departure_time_str = departure_time_str[:16]                 
                        departure_time = datetime.datetime.fromisoformat(departure_time_str) 

                        # Check if departure time is within the specified window
                        if lower_bound <= departure_time <= upper_bound:
                            filtered_offers.append((offer, is_direct))
                            break  # Stop checking segments once a valid one is found

                if filtered_offers:
                    sorted_offers = sorted(filtered_offers, key=lambda x: float(x[0]['price']['total']))
                    limited_offers = sorted_offers[:10]  # Limit the number of results to display

                    # Display the top offers
                    for offer, is_direct in limited_offers:
                        st.write(f"**Offer ID:** {offer['id']}")
                        st.write(f"**Price:** {offer['price']['total']} {offer['price']['currency']}")
                        flight_type = "Direct Flight" if is_direct else "Flight with Transfer(s)"
                        st.write(f"**Flight Type:** {flight_type}")
                        st.write("---")
                else:
                    st.info("No flights found within the specified time window.")

            with col2:
                st.header("Direct Flight Predictions")
                # Logic for displaying direct flight predictions goes here

            with col3:
                st.header("Transfer Flight Predictions")
                # Logic for displaying transfer flight predictions goes here

    else:
        st.warning("Please fill in all required fields before comparing prices.")



        