import json
import requests
import datetime
import pandas as pd
import sys
from TripAdvisor import TripAdvisor
from POIrules import recommend_poi

client_id = sys.argv[1]
cities = json.loads(sys.argv[2])
age = sys.argv[3]
sex = sys.argv[4]
travel_type = sys.argv[5]

#error
message={}
message['error']=''

age = int(age)

try:
    tripadvisor = TripAdvisor(cities[1:], client_id, base_url='tripadvisor1.p.rapidapi.com')
    POIdata = tripadvisor.save_food_attraction_data()
except Exception as e:
    message['error'] = message['error'] + 'tripadvisor error: ' + str(e)+'     | '

try:
    POI_dict = recommend_poi(age=age, sex=sex, travel_type=travel_type)
    POI_json=json.dumps(POI_dict)
except Exception as e:
    message['error'] = message['error'] + 'RBS error: ' + str(e) +'     | '
    POI_json='{}'

errordata=json.dumps(message)
jsonoutput=POI_json
print(jsonoutput)