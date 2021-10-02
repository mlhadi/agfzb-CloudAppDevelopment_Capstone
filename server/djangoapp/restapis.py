import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if 'api_key' in kwargs:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=params,
                auth = HTTPBasicAuth('apikey', kwargs.get('api_key', None))
            )
            status_code = response.status_code
            print("With status {} ".format(status_code))
            print(response.text)
            json_data = json.loads(response.text)
            return json_data
        else:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=kwargs,
            )
            status_code = response.status_code
            print("With status {} ".format(status_code))
            json_data = json.loads(response.text)
            return json_data
    except BaseException as e:
        # If any error occurs
        print(f"Network exception occurred {e}")
        return {}

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"], city=dealer_doc["city"],
                full_name=dealer_doc["full_name"], id=dealer_doc["id"],
                lat=dealer_doc["lat"], long=dealer_doc["long"],
                short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                zip=dealer_doc["zip"], state=dealer_doc['state'])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"], city=dealer_doc["city"],
                full_name=dealer_doc["full_name"], id=dealer_doc["id"],
                lat=dealer_doc["lat"], long=dealer_doc["long"],
                short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                zip=dealer_doc["zip"], state=dealer_doc['state'])
            results.append(dealer_obj)

    return results


def get_dealer_by_state_from_cf(url, state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(f"{url}?state={state}")
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships_list"]
        # For each dealer object
        for dealer_doc in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"], city=dealer_doc["city"],
                full_name=dealer_doc["full_name"], id=dealer_doc["id"],
                lat=dealer_doc["lat"], long=dealer_doc["long"],
                short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                zip=dealer_doc["zip"], state=dealer_doc['state'])
            results.append(dealer_obj)

    return results


def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result['dealers']
        reviews = [
            DealerReview(
                dealership = dealer.get('dealership', None),
                name = dealer.get('name', None),
                purchase = dealer.get('purchase', None),
                review = dealer.get('review', None),
                purchase_date = dealer.get('purchase_date', None),
                car_make = dealer.get('car_make', None),
                car_model = dealer.get('car_model', None),
                car_year = dealer.get('car_year', None),
                sentiment = analyze_review_sentiments(dealer.get('review', None)),
                id = dealer.get('id', None)
            ) for dealer in dealers
            if dealer.get('dealership', None) == dealer_id
        ]
    return reviews

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    url = 'https://api.jp-tok.natural-language-understanding.watson.cloud.ibm.com/instances/fcdb64c1-9cfc-4025-8547-a2f2d804a25a/v1/analyze?version=2019-07-12'
    api_key = 'V9qx5qpuWa04eP6NYa5sTOvfnIR_uxb13t6zeNUxx4_z'
    version = "2020-08-01"
    features = "sentiment"
    return_analyzed_text = True
    json_data = get_request(
        url, api_key=api_key, text=dealerreview, version=version,
        features=features, return_analyzed_text=return_analyzed_text,
    )
    try:
        return json_data['sentiment']['document']['label']
    except BaseException as e:
        return f'{e}'

