import streamlit as st
import pandas as pd
import json
import requests
import datetime
from datetime import datetime, timedelta
import os

# Get the current script directory (absolute path)
current_dir = os.path.dirname(os.path.abspath(__file__))

FASTAPI_URL = "https://adv-mla-at3.onrender.com/"

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
st.title(":airplane_departure: :blue[Save Your Flight Budget]")

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


# Adjust +60 days
today = datetime.now().date()
max_date = today + timedelta(days=60)

departure_date = st.sidebar.date_input(
    "Enter Departure Date", 
    value=today, 
    min_value=today, 
    max_value=max_date, 
    help="You can select a date up to 60 days in advance for more accurate information."
)

# Restrict the time selection to show only hourly increments from 5:00 AM to 11:00 PM.

departure_time = st.sidebar.time_input("Enter Departure Time")

the_date = datetime.today().strftime('%Y-%m-%d-%H')
departure_datetime = datetime.combine(departure_date, departure_time)
departure_datetime_str = departure_datetime.strftime("%Y-%m-%d-%H")

show_direct = st.sidebar.checkbox("Direct Flights Only", value=True)
#show_one_transfer = st.sidebar.checkbox("Allow One Transfer", value=False)

cabin_type = st.sidebar.selectbox("Select Cabin Type", ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"])

avg_distance = next(
    (entry['averageDistance'] for entry in avg_distances 
     if entry['startingAirport'] == origin_code and entry['destinationAirport'] == destination_code), 
    "Distance data not available"
)
avg_distance = int(round(avg_distance))

on = st.sidebar.toggle("Activate extra features")

if on:
    AirlineNameScore = st.sidebar.slider(
        "Airline Category",
        min_value=1,
        max_value=4,
        value=4,  
        step=1,
        help="Select an airline score. Encoding reference:\n"
             "- **1**: Spirit Airlines, Frontier Airlines\n"
             "- **2**: JetBlue Airways, Sun Country Airlines\n"
             "- **3**: Key Lime Air, Boutique Air, Contour Airlines, Southern Airways Express, Cape Air\n"
             "- **4**: United, Delta, American Airlines, Alaska Airlines, Hawaiian Airlines"
    )

    # Checkbox for isRefundable option
    refund = st.sidebar.checkbox("Is Refundable", value=False)  

    # Use a checkbox for basic economy
    basic_eco = st.sidebar.checkbox("Basic Economy", value=False)  

else : 
    AirlineNameScore = 4
    refund = False
    basic_eco = False

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
                st.subheader(":blue[Actual Prices]", divider="gray")
                
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
                    direct_offers = [offer for offer, is_direct in filtered_offers if is_direct]
                    transfer_offers = [offer for offer, is_direct in filtered_offers if not is_direct]

                    # Sort by price
                    direct_offers = sorted(direct_offers, key=lambda x: float(x['price']['total']))
                    transfer_offers = sorted(transfer_offers, key=lambda x: float(x['price']['total']))

                    # Determine which offers to display based on checkbox selection
                    try:
                        if show_direct:
                            # Show the two cheapest direct flights
                            limited_offers = direct_offers[:2]
                            direct_price = float(limited_offers[0]['price']['total']) 
                            direct_price_as_strings = str(direct_price)
                        else:
                            # If 'show_direct' is False, you can add logic here to show other options if needed
                            # For example, show the cheapest transfer flights
                            limited_offers = direct_offers[:1] + transfer_offers[:1]
                            direct_price = float(limited_offers[0]['price']['total'])  # First offer in the list is the direct flight
                            transfer_price = float(limited_offers[1]['price']['total'])

                            direct_price_as_strings = str(direct_price)
                            transfer_price_as_strings = str(transfer_price)

                        # Display the offers
                        for idx, offer in enumerate(limited_offers, start=1):
                            st.write(f"**Offer #{idx}:**")
                            st.write(f"**Price:** {offer['price']['total']} {offer['price']['currency']}")
                            flight_type = "Direct Flight" if offer in direct_offers else "Flight with Transfer(s)"
                            st.write(f"**Flight Type:** {flight_type}")
                            st.write("---")
                    except IndexError:
                            st.error("Invalid flight selection. Please adjust your search criteria and try again.")
                else:
                    st.info("No flights found within the specified time window.")


# http://0.0.0.0:8000/flight/predict/?today=2024-11-04-17&lower_time=2024-12-22-10&origin=DEN&des=JFK&cabin=ECONOMY&direct=1&distance=1880

            with col2:
                st.subheader(":blue[Direct Flight Prediction]", divider="gray")
                response = requests.get(
                    f"{FASTAPI_URL}/flight/predict/?today={the_date}"
                    f"&predict_datetime={departure_datetime_str}"
                    f"&origin={origin_code}"
                    f"&des={destination_code}"
                    f"&cabin={cabin_type}"
                    f"&direct={1}"
                    f"&distance={avg_distance}"
                    f"&aircode={AirlineNameScore}"
                    f"&refund={refund}"
                    f"&basic={basic_eco}"
                )
                if response.status_code == 200:
                    predict_data_direct = response.json()
                    non_stop_price = list(predict_data_direct.values())
                    non_stop_price_as_float = float(non_stop_price[0])
                    non_stop_price_as_string = str(non_stop_price[0])
                    st.write(f"**Price:** {non_stop_price_as_string} USD")  # This will display only the values as a list

                else:
                    st.error("Error fetching data.")

            with col3:
                st.subheader(":blue[Transfer Flight Prediction]", divider="gray")
                if not show_direct:
                    # Make the request to the FastAPI endpoint
                    response = requests.get(
                    f"{FASTAPI_URL}/flight/predict/?today={the_date}"
                    f"&predict_datetime={departure_datetime_str}"
                    f"&origin={origin_code}"
                    f"&des={destination_code}"
                    f"&cabin={cabin_type}"
                    f"&direct={0}"
                    f"&distance={avg_distance}"
                    f"&aircode={AirlineNameScore}"
                    f"&refund={refund}"
                    f"&basic={basic_eco}"
                )
                    
                    if response.status_code == 200:
                        predict_data_transfer = response.json()
                        one_stop_price = list(predict_data_transfer.values())
                        one_stop_price_as_float = float(one_stop_price[0])
                        one_stop_price_as_string = str(one_stop_price[0])
                        st.write(f"**Price:** {one_stop_price_as_string} USD")

                    else:
                        st.error("Error fetching data.")


            with st.container():
                st.subheader(":sunglasses: :blue[Your Flight Summary]")
                try:
                    if show_direct:
                        summary_text = (
                        f"For a flight between **{origin_name}** to **{destination_name}** on **{departure_date}** "
                        f"in **{cabin_type}**, we predict:\n\n"
                        f"- A direct flight would cost **{non_stop_price_as_string} USD**. \n\n"
                        f"- Currently, actual price is around **{direct_price_as_strings} USD**. \n\n"
                        )
                        if direct_price > non_stop_price_as_float:
                            comparison_text = "<p style='background-color: #4c6a92; padding: 10px; font-size: 20px; color: white;'><strong>So, maybe try another day or route if possible!</strong></p>"
                        else:
                            comparison_text = "<p style='background-color: #4c6a92; padding: 10px; font-size: 20px; color: white;'><strong>This seems like a reasonable fare for your selection.</strong></p>"

                    else:
                        summary_text = (
                        f"For a flight between **{origin_name}** to **{destination_name}** on **{departure_date}** "
                        f"in **{cabin_type}**, we predict:\n\n"
                        f"- A transfer flight would cost **{one_stop_price_as_string} USD**. \n\n"
                        f"- Currently, actual price is around **{transfer_price_as_strings} USD**. \n\n"
                        )

                    # Provide additional tip based on price comparison
                        if transfer_price > non_stop_price_as_float:
                            comparison_text = "<p style='background-color: #4c6a92; padding: 10px; font-size: 20px; color: white;'><strong>So, maybe try another day or route if possible!</strong></p>"
                        else:
                            comparison_text = "<p style='background-color: #4c6a92; padding: 10px; font-size: 20px; color: white;'><strong>This seems like a reasonable fare for your selection.</strong></p>"

                    # Display the summary in Streamlit
                    st.markdown(summary_text)
                    st.markdown(comparison_text, unsafe_allow_html=True)
                except IndexError:
                    st.error("Sorry, we cannot provide the flight summary due to an invalid flight selection.")
        


