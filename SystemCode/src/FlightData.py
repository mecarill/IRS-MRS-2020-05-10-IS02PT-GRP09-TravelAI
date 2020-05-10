#import argparse
import requests
import datetime
import pandas as pd
import sys

class FlightData():

    def __init__(self, countries, from_date, to_date, adults, children, client_id, client_secret, base_url):
        """
        defines flight search terms that user input
        initialize empty dataframe
        initialize api by requesting token
        :param countries: [list] in iata country_code format
        :param from_date: string in yyyy-mm-dd
        :param to_date: string in yyyy-mm-dd
        :param client_id: client_id generated from amadeus webpage
        :param client_secret: client_secret generated from amadeus webpage
        :param base_url: test or production url
        
        """

        # Get user request
        self.countries = countries
        self.adults = adults
        self.children = children

        format_str = '%Y-%m-%d' # The format
        self.from_date = datetime.datetime.strptime(from_date, format_str)
        self.to_date = datetime.datetime.strptime(to_date, format_str)

        # Initialize empty dataframe
        self.columns = [
                'Departure Date', 
                'Arrival Date',
                'Departure Time',
                'Arrival Time',
                'Duration',
                'Type of Flight',
                'Price',
                'Airline',
                'Departure Airport',
                'Arrival Airport',
                'Departure City',
                'Arrival City'
                ]
        self.flight_data_df = pd.DataFrame(columns=self.columns)

        # Initialize API by requesting token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
        'grant_type': 'client_credentials',
        'client_id': self.client_id, 
        'client_secret': self.client_secret 
        }

        response = requests.post(self.base_url+'/v1/security/oauth2/token', headers=headers, data=data)
        self.access_token = response.json()['access_token']




    def _get_countries_pair(self):
        '''
        gets all permutations of country pairs
        '''
    
        pairs_of_countries = [(i,j) for i in self.countries for j in self.countries]
        repeated_countries = pairs_of_countries[0::len(self.countries)+1]
        self.pairs_of_countries = [x for x in pairs_of_countries if not x in repeated_countries ]

    def _get_all_dates(self):
        '''
        gets range of dates from start date to end date
        '''

        delta = self.to_date - self.from_date       # as timedelta

        self.travel_dates = []
        for i in range(delta.days + 1):
            day = self.from_date + datetime.timedelta(days=i)
            self.travel_dates.append(day)
    
    def _filter_list(self,x):
        '''
        filters get_country_date_pairs according to following rules:
        rule1: if date is startdate, then get flight from home country to other countries only
        rule2: if date is enddate, then get flight from other countries to home countries only
        rule3: if date is not startdate, and not end date, then get fligths that are not in home countries
        '''
        home_country = self.countries[0]

        from_date = str(self.from_date)[:10]
        to_date = str(self.to_date)[:10]
        rule1 = (x[2]==from_date) and (x[0]==home_country)
        rule2 = (x[2]==to_date) and (x[1]==home_country)
        rule3 = (x[2] != from_date and x[2] != to_date and x[0]!=home_country and x[1]!=home_country)
        rules = [rule1, rule2, rule3]
        if any(rules):     
            return x

    def _get_country_date_pair(self):
        '''
        gets permutations of country pairs and range of dates
        '''

        self._get_countries_pair()
        self._get_all_dates()

        self.country_date_pair = []
        for country in self.pairs_of_countries:
            for traveldate in self.travel_dates:
                origin = country[0]
                destination = country[1]
                traveldate = traveldate
                self.country_date_pair.append((origin, destination, str(traveldate)[:10]))

        # filter out irrelevant country_date_pair flights
        self.country_date_pair = [ x for x in self.country_date_pair if self._filter_list(x) ] 
        

    def _request_flight(self, origin, destination, depdate, adults, children):
        '''
        request flights from amadeus for one set of origin, destination, depdate
        :params origin: string
        :params destination: string
        :params depdate: string in yyyy-mm-dd
        '''
        headers = {
            'Authorization': 'Bearer '+ self.access_token
        }

        # to put in argsparse
        adults = 1
        children = 0
        travelclass = 'ECONOMY'
        non_stop = 'true'
        currency = 'SGD'
        max_result = 5

        params = (
            ('originLocationCode', origin),
            ('destinationLocationCode', destination),
            ('departureDate', depdate),
            ('adults', adults),
            ('children', children),
            ('travelClass', travelclass),
            ('nonStop', non_stop),
            ('currencyCode', currency),
            ('max', max_result),
        )

        response = requests.get(self.base_url + '/v2/shopping/flight-offers', headers=headers, params=params)
        self.response = response.json()



    def _parse_response_from_request_flight(self, origin, destination):

        # Get required fields from response
        self.duration = []
        self.departure_airport = []
        self.departure_date = []
        self.departure_time = []
        self.arrival_airport = []
        self.arrival_date = []
        self.arrival_time = []
        self.airline_code = []
        self.price = []
        self.departure_city = []
        self.arrival_city = []

        for data in self.response['data']:
            x = data['itineraries'][0]['duration'][2:]
            self.duration.append(x)

            x = data['itineraries'][0]['segments'][0]['departure']['iataCode']
            self.departure_airport.append(x)
            x = data['itineraries'][0]['segments'][0]['departure']['at'][:10]
            self.departure_date.append(x)
            x = data['itineraries'][0]['segments'][0]['departure']['at'][11:]
            self.departure_time.append(x)
            
            x = data['itineraries'][0]['segments'][0]['arrival']['iataCode']
            self.arrival_airport.append(x)
            x = data['itineraries'][0]['segments'][0]['arrival']['at'][:10]
            self.arrival_date.append(x)
            x = data['itineraries'][0]['segments'][0]['arrival']['at'][11:]
            self.arrival_time.append(x)
            
            x = data['itineraries'][0]['segments'][0]['carrierCode']
            self.airline_code.append(x)
            
            x = data['price']['grandTotal']
            self.price.append(x)

            self.departure_city.append(origin)
            self.arrival_city.append(destination)



        airline_dict = self.response['dictionaries']['carriers']
        self.airline = list(map(airline_dict.get, self.airline_code))


    def save_all_flights_in_df(self):
        self._get_country_date_pair()
        for i, (origin, destination, depdate) in enumerate(self.country_date_pair):
            #print('Getting flight data for:', i, origin, destination, depdate)
            self._request_flight(origin, destination, depdate, self.adults, self.children)
            self._parse_response_from_request_flight(origin, destination)
            new_flight_data_df = pd.DataFrame(
                    {'Departure Date': self.departure_date,
                    'Arrival Date': self.arrival_date,
                    'Departure Time': self.departure_time,
                    'Arrival Time': self.arrival_time,
                    'Duration': self.duration,
                    'Type of Flight': 'direct',
                    'Price': self.price,
                    'Airline': self.airline,
                    'Departure Airport': self.departure_airport,
                    'Arrival Airport': self.arrival_airport,
                    'Departure City': self.departure_city,
                    'Arrival City': self.arrival_city
                    }
                )

            self.flight_data_df =  self.flight_data_df.append(new_flight_data_df)
        return self.flight_data_df

    
if __name__ == '__main__':
    #ap=argparse.ArgumentParser()
    #ap.add_argument('--countries', nargs='+', default=['SIN', 'BKK', 'TPE', 'TYO', 'ICN']) #
    #ap.add_argument('--from_date', default='2020-08-01')
    #ap.add_argument('--to_date', default='2020-08-10')
    #ap.add_argument('--client_id', default='veron') 
    #ap.add_argument('--client_secret', default='veron')
    #ap.add_argument('--base_url', default = 'https://test.api.amadeus.com')
    #args = vars(ap.parse_args())

    
    countries = sys.argv[3]
    from_date = sys.argv[4]
    to_date = sys.argv[5]
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    base_url = 'https://test.api.amadeus.com'
        

    flightdata = FlightData(countries, from_date, to_date, client_id, client_secret, base_url)
    flight_data_df = flightdata.save_all_flights_in_df()
    
    #flight_data_df.to_csv('flight_data.csv', index=False)
    
    #print("Output from Python") 
    #print("client_id: " + client_id)
    #print("client_secret: " + client_secret)
    #print("countries: " + countries) 
    #print("from_date: " + from_date)    
    #print("to_date: " + to_date) 
    flight_data_df.to_csv('flight_data.csv', index=False)
    
    print("Output from Python") 
    print("client_id: " + client_id)
    print("client_secret: " + client_secret)
    print("countries: " + countries) 
    print("from_date: " + from_date)    
    print("to_date: " + to_date) 

