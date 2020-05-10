import json
import requests
import datetime
import pandas as pd
import sys
from FlightData import FlightData
from HotelData import HotelData
# from TripAdvisor import TripAdvisor
from traopti import Optimiser
# from POIrules import recommend_poi

if __name__ == '__main__':
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    cities = json.loads(sys.argv[3])
    from_date = sys.argv[4]
    to_date = sys.argv[5]
    hotels = [] #sys.argv[6]
    ratings = json.loads(sys.argv[7])
    adults = sys.argv[8]
    children = sys.argv[9]
    base_url = sys.argv[10]
    # age = 'Less than 18'#sys.argv[8]
    # sex = 'female'#sys.argv[9]
    # travel_type = 'solo'#sys.argv[10]

    adults = int(adults)
    children = int(children)

    # load json dict containing city:iata code
    with open('./scripts/iata.json', 'r') as f:
        iata_dict = json.load(f)

    # clean user input for cities and convert them into iata codes
    cities = [x.title().strip() for x in cities]
    cities_code = [iata_dict[x] for x in cities]

    for i in range(len(cities)):
        hotels.append('')

    #error
    message={}
    message['error']=''

    # data pulling
    try:
        flightdata = FlightData(cities_code, from_date, to_date, adults, children, client_id, client_secret, base_url='https://api.amadeus.com')
        flightdata=flightdata.save_all_flights_in_df()
    except Exception as e:
        message['error']=message['error']+'Flightdata error: ' + str(e) +'     | '

    try:
        hoteldata = HotelData(cities_code[1:], hotels, ratings, from_date, to_date, adults, client_id, client_secret, base_url='https://api.amadeus.com')
        hoteldata= hoteldata.save_all_hotel_details_in_df()
    except Exception as e:
        message['error'] = message['error']+'Hoteldata error: ' + str(e)+'     | '

    # try:
    #     tripadvisor = TripAdvisor(cities[1:], client_id='21de580a3bmsh132ae5369dedabdp10ee13jsn21861668958f', base_url='tripadvisor1.p.rapidapi.com')
    #     POIdata = tripadvisor.save_food_attraction_data()
    # except Exception as e:
    #     message['error'] = message['error'] + 'tripadvisor error: ' + str(e)+'     | '

    # try:
    #     POI_dict = recommend_poi(age=age, sex=sex, travel_type=travel_type)
    #     POI_json=json.dumps(POI_dict)
    # except Exception as e:
    #     message['error'] = message['error'] + 'RBS error: ' + str(e) +'     | '
    #     POI_json='{}'

    # optimiser
    try:
        optimiseddata=Optimiser(flightdata,hoteldata,adults,children)
    except Exception as e:
        message['error'] = message['error'] + 'Optimiser error: ' + str(e) +'     | '
        optimiseddata='[]'

    errordata=json.dumps(message)
    sys.stderr.write(errordata)
    jsonoutput=optimiseddata #+ POI_json+',' #',' + errordata+
    print(jsonoutput)


    # to use in cli:
    # python TravelAI.py a a 'taipei','bangkok' '2020-08-01' '2020-08-03' 'fullerton','novotel' 4,5 '25-34' 'male' 'solo'
