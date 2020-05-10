import argparse
import requests
import datetime
import pandas as pd


class TripAdvisor():

    def __init__(self, countries, client_id, base_url):
        self.headers = {
            'x-rapidapi-host': base_url,
            'x-rapidapi-key': client_id
            }
        self.countries = countries

    def _get_location_id(self,country):
        url = "https://tripadvisor1.p.rapidapi.com/locations/search"

        self.query = country
        querystring = {
            "limit":"2",
            "sort":"relevance",
            "lang":"en_US",
            "query":self.query}

        response = requests.request("GET", url, headers=self.headers, params=querystring)
        response = response.json()
        #print('---Debugging----')
        #print(response)
        self.location_id = response['data'][0]['result_object']['location_id']

        # print('.....running.........')

    def _make_food_df(self):
        # Initialize empty dataframe
        columns = [
                'Name', 
                'Latitude',
                'Longitude',
                'Address',
                'Phone',
                'Website',
                'Image',
                'Ranking',
                'Price level',
                'Description',
                'Cuisine',
                'Establishment type',
                'City'
                ]
        self.food_df = pd.DataFrame(columns=columns)

    def _make_attraction_df(self):
        # Initialize empty dataframe
        columns = [
                'Name', 
                'Latitude',
                'Longitude',
                'Address',
                'Phone',
                'Website',
                'Image',
                'Ranking',
                'Description',
                'Category1',
                'Category2',
                'City'
                ]
        self.attraction_df = pd.DataFrame(columns=columns)

    # def _get_food_data(self):
    #     url = "https://tripadvisor1.p.rapidapi.com/restaurants/list"
    #     querystring = {
    #         "limit":"20",
    #         "min_rating":4,
    #         "currency":"SGD",
    #         "lang":"en_US",
    #         "location_id":self.location_id,
    #                 }
    #     response = requests.request("GET", url, headers=self.headers, params=querystring)
    #     self.food_response = response.json()

    def _get_attraction_data(self):
        url = "https://tripadvisor1.p.rapidapi.com/attractions/list"

        querystring = {
            "lang":"en_US",
            "currency":"SGD",
            "sort":"recommended",
            "limit":"20",
            "location_id":self.location_id
                    }
        response = requests.request("GET", url, headers=self.headers, params=querystring)
        self.attraction_response = response.json()

    # def _parse_food_data(self):
    #     try:
    #         for x in self.food_response['data']:
    #             name = x['name']
    #             latitude = x['latitude']
    #             longitude = x['latitude']
    #             address = x['address']
    #             phone = x['phone']
    #             website = x['website']
    #             image_url = x['photo']['images']['medium']['url']
    #             ranking = x['ranking'] #.split('of')[0]
    #             price_level = x['price_level']
    #             description = x['description']
    #             cuisine = []
    #             establishment_type = []
    #             for y in x['cuisine']:
    #                 cuisine.append(y['name'])
    #             for y in x['establishment_types']:
    #                 establishment_type.append(y['name'])
    #             city = self.query

    #             # appending into dataframe
    #             food_df_new  = pd.DataFrame({
    #                             'Name': name,
    #                             'Latitude': latitude,
    #                             'Longitude': longitude,
    #                             'Address': address,
    #                             'Phone': phone,
    #                             'Website': website,
    #                             'Image': image_url,
    #                             'Ranking': ranking,
    #                             'Price level': price_level,
    #                             'Description': description,
    #                             'Cuisine': [cuisine],
    #                             'Establishment type': [establishment_type],
    #                             'City': city
    #                             })
    #             self.food_df = self.food_df.append(food_df_new)
    #     except:
    #         pass

    def _parse_attraction_data(self):
            for x in self.attraction_response['data']:
                try:
                    name = x['name']
                    latitude = x['latitude']
                    longitude = x['latitude']
                    address = x['address']
                    phone = x['phone']
                    website = x['website']
                    image_url = x['photo']['images']['medium']['url']
                    ranking = x['ranking'] #.split('of')[0]
                    description = x['description']
                    category1 = []
                    category2 = []
                    for y in x['subcategory']:
                        category1.append(y['name'])
                    for y in x['subtype']:
                        category2.append(y['name'])
                    city = self.query
                    
                    # appending into dataframe
                    attraction_df_new  = pd.DataFrame({
                                    'Name': name,
                                    'Latitude': latitude,
                                    'Longitude': longitude,
                                    'Address': address,
                                    'Phone': phone,
                                    'Website': website,
                                    'Image': image_url,
                                    'Ranking': ranking,
                                    'Description': description,
                                    'Category1': [category1],
                                    'Category2': [category2],
                                    'City': city
                                    })
                    self.attraction_df = self.attraction_df.append(attraction_df_new)
                except:
                    pass
            
    def save_food_attraction_data(self):
        self._make_food_df()
        self._make_attraction_df()
        for country in self.countries:
            self._get_location_id(country)

            # self._get_food_data()
            self._get_attraction_data()

            # self._parse_food_data()
            self._parse_attraction_data()

            #self.food_df.to_csv('food.csv', index=False)
            self.attraction_df.to_csv('attraction.csv', index=False)

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--countries', nargs='+', default=['singapore', 'bangkok', 'taipei', 'tokyo', 'seoul']) #
    ap.add_argument('--client_id', default='ask veron') 
    ap.add_argument('--base_url', default = 'tripadvisor1.p.rapidapi.com')
    args = vars(ap.parse_args())

    countries = args["countries"]
    client_id = args['client_id']
    base_url = args['base_url']

    tripadvisor = TripAdvisor(countries, client_id, base_url)
    tripadvisor.save_food_attraction_data()
