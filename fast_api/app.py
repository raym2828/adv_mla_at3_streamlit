from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
from joblib import load
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import logging


app = FastAPI()


model_path1 = os.path.join(os.path.dirname(__file__), '../models/xgb_pipeline.joblib')
model1 = load(model_path1)


logging.basicConfig(level=logging.INFO)

cabin_class_encoding = {
    "ECONOMY": 1,
    "PREMIUM_ECONOMY": 2,
    "BUSINESS": 3,
    "FIRST": 4,
}


@app.get("/")
async def root():
    return {
        "project": "Flight Predcition API",
        "description": "This API provides flight prices prediction with users inputs.",
        "endpoints": {
            "/": "API Overview",
            "/health/": "API Health Check",
            "/flight/predict/": "Flight Price prediction",
        },
        "expected_input": {
            "/flight/predict//": {"today": "YYYY-MM-DD-HH", "predict_datetime": "YYYY-MM-DD-HH", "origin": "str", "des": "str", "cabin": "str",\
                                  "direct": "int", "aircode": "int", "refund": "bool", "basic": "bool"}
        },
        "output_format": "JSON"
    }

@app.get('/health', status_code=200)
def healthcheck():
    return 'Your best model is all ready to go!'


#{FASTAPI_URL}/flight/predict/?today={the_date}&lower_time={lower_bound}\
# &upper_time={upper_bound}&origin={origin_code}&des={destination_code}&cabin={cabin_type}&direct={1}")

@app.get("/flight/predict/")
def predict_flight_price(today: str, predict_datetime: str, origin: str, des: str, cabin: str, direct: int, distance: int, aircode: int, refund: bool, basic: bool):
    try:
        # Convert the input date strings into datetime objects
        today_date = datetime.strptime(today, "%Y-%m-%d-%H")
        predict_date = datetime.strptime(predict_datetime, "%Y-%m-%d-%H")

        date_diff_days = (predict_date - today_date).days

        logging.info(f"Parsed dates - Today: {today_date}, Lower: {predict_date}")
        logging.info(f"Date difference in days: {date_diff_days}")

        # Extract relevant date features
        weekday = predict_date.weekday()

        # Cabin code mapping
        cabin_code = cabin_class_encoding.get(cabin)
        if cabin_code is None:
            logging.error(f"Invalid cabin class: {cabin}")
            raise HTTPException(status_code=400, detail="Invalid cabin class.")

        predictions = []

        # Iterate through the time window (−1, 0, +1 hour)
        for hour_offset in range(-1, 2):  # This will cover -1, 0, +1 hour
            predict_time = predict_date + timedelta(hours=hour_offset)
            hr = predict_time.hour

            # Prepare the input data
            input_data = pd.DataFrame({
                'date_diff_days': [date_diff_days],
                'weekday': [weekday],
                'CabinCode': [cabin_code],
                'DepartureTimeHour': [hr],
                'startingAirport': [origin],
                'destinationAirport': [des],
                'isNonStop': [direct],
                'totalTravelDistance': [distance],
                'AirlineNameScore': [aircode],
                'isRefundable': [refund],
                'isBasicEconomy': [basic]
            })

            # Predict the price using the best model
            try:
                prediction = model1.predict(input_data).item()
                predictions.append(prediction)
                logging.info(f"Predicted price for {predict_time}: {prediction}")
            except ValueError as e:
                logging.error(f"Error in model prediction for {predict_time}: {e}")
                continue  # Skip this iteration if there's an error

        # Determine the minimum predicted price
        if predictions:
            min_price = min(predictions)
            return {"The price": round(min_price, 2)}
        else:
            raise HTTPException(status_code=404, detail="No predictions were made.")

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail="Invalid date format or parameters.")
    except KeyError as ke:
        logging.error(f"KeyError: {ke}")
        raise HTTPException(status_code=400, detail="Invalid origin or destination airport.")
