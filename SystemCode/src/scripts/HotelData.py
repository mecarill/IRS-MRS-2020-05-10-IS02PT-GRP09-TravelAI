import argparse
import requests
import datetime
import pandas as pd
import math


class HotelData():

    def __init__(self, countries, hotels, ratings, from_date, to_date, adults, client_id, client_secret, base_url):
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
        self.hotels = hotels
        self.ratings = ratings
        self.adults = adults


        format_str = '%Y-%m-%d' # The format
        self.from_date = datetime.datetime.strptime(from_date, format_str)
        self.to_date = datetime.datetime.strptime(to_date, format_str)

        # Initialize empty dataframe
        self.columns = [
                'Hotel',
                'Check In Date',
                'Check Out Date',
                'Category',
                'Number of Beds',
                'Bed Type',
                'Price',
                'City'
                ]
        self.hotel_data_df = pd.DataFrame(columns=self.columns)

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
        rule1: if country is home_country, then dont need to get hotek
        '''
        home_country = self.countries[0]
        rule1 = x[0]!=home_country
        rules = [rule1]
        if any(rules):
            return x


    def _get_hotel_date_pair(self):
        '''
        gets combination of all hotel and date pairs
        '''
        self._get_all_dates()

        self.hotel_date_pair = []
        for country, hotel in zip(self.countries, self.hotels):
            for traveldate in self.travel_dates:
                traveldate = traveldate
                self.hotel_date_pair.append((country, hotel, str(traveldate)[:10]))

        # # filter out irrelevant country_date_pair flights
        # self.hotel_date_pair = [ x for x in self.hotel_date_pair if self._filter_list(x) ]

    def _request_hotel_details(self, country, hotel, check_in_date, adults):
        '''
        gets hotel details from API
        '''

        headers = {
            'Authorization': 'Bearer '+ self.access_token  #,AdMvG4pnMRnuIAlgHfsxFx1XrQKz
        }


        citycode = country
        adults = 1
        radius = 200
        radiusunit = 'KM'
        check_in_date = check_in_date
        room_quantity = math.ceil(adults/2)
        hotel = hotel
        ratings = self.ratings
        best_rate_only= 'true'
        sort = 'PRICE'
        currency = 'SGD'

        params = (
            ('cityCode', citycode),
            ('adults', adults),
            ('radius', radius),
            ('radiusUnit', radiusunit),
            ('checkInDate', check_in_date),
        #    ('checkOutDate','2020-08-02'),
            ('roomQuantity', room_quantity),
            ('hotelName', hotel),
        #    ('ratings', ratings),
        #    ('priceRange', 100),
        #    ('paymentPolicy', 'NONE'),
        #    ('includeClosed', 'false'),
            ('bestRateOnly', best_rate_only),
        #    ('view', 'FULL'),
            ('sort', sort),
            ('currency',currency)
        )

        response = requests.get('https://api.amadeus.com/v2/shopping/hotel-offers', headers=headers, params=params)
        self.response = response.json()
        try:
            self.response['data'][0]['hotel']['name'] # if hotel not found
            #self.response['data']==[]
        except:
            #print(hotel, 'not available in database. We found a new hotel instead.')
            params = (
                ('cityCode', citycode),
                ('adults', adults),
                ('radius', radius),
                ('radiusUnit', radiusunit),
                ('checkInDate', check_in_date),
                ('roomQuantity', room_quantity),
                ('ratings', ratings),
                #('hotelName', hotel), remove hotel name
                ('bestRateOnly', best_rate_only),
                ('sort', sort),
                ('currency',currency)
                    )
            response = requests.get('https://api.amadeus.com/v2/shopping/hotel-offers', headers=headers, params=params)
            self.response = response.json()

    def _parse_response_from_request_hotel_details(self, country):
        self.country = country
        self.hotel = self.response['data'][0]['hotel']['name']
        #print(self.hotel)
        self.check_in_date = self.response['data'][0]['offers'][0]['checkInDate']
        self.check_out_date = self.response['data'][0]['offers'][0]['checkOutDate']
        self.category = self.response['data'][0]['offers'][0]['room']['typeEstimated']['category']
        self.no_of_beds = '-' #self.response['data'][0]['offers'][0]['room']['typeEstimated']['beds']
        self.bed_type = '-' #self.response['data'][0]['offers'][0]['room']['typeEstimated']['bedType']
        self.currency = self.response['data'][0]['offers'][0]['price']['currency']
        try:
            self.exchange_rate_SGD = self.response['dictionaries']['currencyConversionLookupRates'][self.currency]['rate']
            self.price = float(self.response['data'][0]['offers'][0]['price']['base']) * float(self.exchange_rate_SGD)
        except:
            try:
                self.exchange_rate_SGD = self.response['dictionaries']['currencyConversionLookupRates'][self.currency]['rate']
                self.price = float(self.response['data'][0]['offers'][0]['price']['total']) * float(self.exchange_rate_SGD)
            except:
                try:
                    self.price = float(self.response['data'][0]['offers'][0]['price']['base'])
                except:
                    self.price = float(self.response['data'][0]['offers'][0]['price']['total'])

    def save_all_hotel_details_in_df(self):
        self._get_hotel_date_pair()
        for i, (country, hotel, traveldate) in enumerate(self.hotel_date_pair):
            #print('Getting details for:', i, country, hotel, traveldate)
            self._request_hotel_details(country, hotel, traveldate, self.adults)
            self._parse_response_from_request_hotel_details(country)
            new_hotel_data_df = pd.DataFrame(
                                {'Hotel': [self.hotel],
                                'Check In Date': [self.check_in_date],
                                'Check Out Date': [self.check_out_date],
                                'Category': [self.category],
                                'Number of Beds': [self.no_of_beds],
                                'Bed Type': [self.bed_type],
                                'Price': [self.price],
                                'City': [self.country]}
                                )
            self.hotel_data_df =  self.hotel_data_df.append(new_hotel_data_df)
        return self.hotel_data_df


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--countries', nargs='+', default=['SIN', 'BKK', 'TPE', 'TYO', 'ICN'])
    ap.add_argument('--hotels', nargs='+', default=['fullerton hotel','novotel','ximending','shangri la','novotel'])
    ap.add_argument('--ratings', nargs='+', default=[4,5])
    ap.add_argument('--from_date', default='2020-08-01')
    ap.add_argument('--to_date', default='2020-08-10')
    ap.add_argument('--client_id', default='veron')
    ap.add_argument('--client_secret', default='veron')
    ap.add_argument('--adults', default=1)
    ap.add_argument('--base_url', default = 'https://api.amadeus.com')
    args = vars(ap.parse_args())

    countries = args["countries"]
    hotels = args['hotels']
    ratings = args['ratings']
    from_date = args["from_date"]
    to_date = args["to_date"]
    client_id = args['client_id']
    client_secret = args['client_secret']
    base_url = args['base_url']


    hoteldata = HotelData(countries, hotels, ratings, from_date, to_date, client_id, client_secret, base_url)
    hotel_data_df = hoteldata.save_all_hotel_details_in_df()
    #hotel_data_df.to_csv('hotel_data.csv', index=False)
