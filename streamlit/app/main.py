import streamlit as st
import pandas as pd
import json
import requests
import datetime
from datetime import datetime, timedelta
import os

# Get the current script directory (absolute path)
current_dir = os.path.dirname(os.path.abspath(__file__))

FASTAPI_URL = "http://0.0.0.0:8000"

with open('average_distances.json', 'r') as json_file:
    avg_distances = json.load(json_file)

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

destination_airports = {
    "Charlotte (CLT)": "CLT",
    "Detroit (DTW)": "DTW",
    "Washington Dulles (IAD)": "IAD",
    "Boston (BOS)": "BOS",
    "Denver (DEN)": "DEN",
    "Dallas/Fort Worth (DFW)": "DFW",
    "Los Angeles (LAX)": "LAX",
    "Miami (MIA)": "MIA",
    "Oakland (OAK)": "OAK",
    "Chicago O'Hare (ORD)": "ORD",
    "Philadelphia (PHL)": "PHL",
    "San Francisco (SFO)": "SFO",
    "Atlanta (ATL)": "ATL",
    "New York LaGuardia (LGA)": "LGA",
    "Newark (EWR)": "EWR",
    "New York (JFK)": "JFK"
}

#FASTAPI_URL = "https://at2-api.onrender.com"

# Title of the application
st.title(":heavy_check_mark: Save your flight budget")

st.sidebar.header("Flight Details")

# User inputs for flight details
origin_name = st.sidebar.selectbox("Choose origin airport", list(airports.keys()))
origin_code = airports[origin_name]

# Filter available destination options based on selected origin
destination_options = [
    dest['destinationAirport'] for dest in avg_distances 
    if dest['startingAirport'] == origin_code
]

# Map destination codes back to airport names
destination_airports = {name: code for name, code in destination_airports.items() if code in destination_options}

# Select destination
destination_name = st.sidebar.selectbox("Choose destination airport", list(destination_airports.keys()))
destination_code = destination_airports[destination_name]

departure_date = st.sidebar.date_input("Enter Departure Date")
departure_time = st.sidebar.time_input("Enter Departure Time")

the_date = datetime.today().strftime('%Y-%m-%d-%H')
departure_datetime = datetime.combine(departure_date, departure_time)
departure_datetime_str = departure_datetime.strftime("%Y-%m-%d-%H")

show_direct = st.sidebar.checkbox("Direct Flights Only", value=True)
show_one_transfer = st.sidebar.checkbox("Allow One Transfer", value=False)

cabin_type = st.sidebar.selectbox("Select Cabin Type", ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"])

avg_distance = next(
    (entry['averageDistance'] for entry in avg_distances 
     if entry['startingAirport'] == origin_code and entry['destinationAirport'] == destination_code), 
    "Distance data not available"
)
avg_distance = int(round(avg_distance))

print(f"Origin: {origin_code}, Destination: {destination_code}, Date: {departure_date}, Cabin: {cabin_type}, Distance: {avg_distance}")

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
        time_window = timedelta(minutes=60)

        lower_bound = datetime.combine(departure_date, departure_time) - time_window
        upper_bound = datetime.combine(departure_date, departure_time) + time_window

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
                        departure_time = datetime.fromisoformat(departure_time_str) 

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


# http://0.0.0.0:8000/flight/predict/?today=2024-11-04-17&lower_time=2024-12-22-10&origin=DEN&des=JFK&cabin=ECONOMY&direct=1&distance=1880

            with col2:
                st.header("Direct Flight Predictions")
                response = requests.get(f"{FASTAPI_URL}/flight/predict/?today={the_date}&predict_datetime={departure_datetime_str}&origin={origin_code}&des={destination_code}&cabin={cabin_type}&direct={1}&distance={avg_distance}")
                if response.status_code == 200:
                    predict_data = response.json()
                    st.dataframe(predict_data)
            #st.json(predict_data)
                else:
                    st.error("Error fetching data.")

            with col3:
                st.header("Transfer Flight Predictions")
            #    if show_one_transfer == True:
                    
