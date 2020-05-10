import os
import pandas as pd
from durable.lang import ruleset, when_all, m, post, _main_host, assert_fact


def recommend_poi(age, sex, travel_type):

    if age < 18:
        age = 'Less than 18'
    elif 18 <= age <=  24:
        age = '18-24'
    elif 25 <= age <= 34:
        age = '25-34'
    elif 35 <= age <= 44:
        age = '35-44'
    elif 45 <= age <= 54:
        age = '45-54'
    elif 55 <= age:
        age = '55 and over' 

    # clear existing rules
    if _main_host is not None:
        _main_host._ruleset_directory.clear()

    file_path = os.path.join(os.getcwd(),'POI.txt')

    # rules
    with ruleset('POI'):
        # Less than 18 male
        @when_all((m.age == 'Less than 18') & (m.sex == 'male') & (m.travel_type == 'solo'))
        def poi(c):
            print("shopping, tours, fun & games, outdoor activites, concerts & shows, sights & landmarks", file=open(file_path, 'w'))
        @when_all((m.age == 'Less than 18') & (m.sex == 'male') & (m.travel_type == 'family'))
        def poi(c):
            print("zoos & aquariums, fun & games, shopping, nature & parks", file=open(file_path, 'w'))
        @when_all((m.age == 'Less than 18') & (m.sex == 'male') & (m.travel_type == 'friends'))
        def poi(c):
            print("museum, sights & landmarks, nature & parks", file=open(file_path, 'w'))      

        # Less than 18 female
        @when_all((m.age == 'Less than 18') & (m.sex == 'female') & (m.travel_type == 'solo')) # empty use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : '18-24', 'sex' : 'female' , 'travel_type' : 'solo'})
        @when_all((m.age == 'Less than 18') & (m.sex == 'female') & (m.travel_type == 'family')) # empty use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : '45-54', 'sex' : 'female' , 'travel_type' : 'family'})      # assuming travelling with parents aged 45-54
        @when_all((m.age == 'Less than 18') & (m.sex == 'female') & (m.travel_type == 'friends')) # empty use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : 'Less than 18', 'sex' : 'male' , 'travel_type' : 'friends'})       # assuming some of the friends they travel with are less than 18 males
            
            
        # 18-24 male
        @when_all((m.age == '18-24') & (m.sex == 'male') & (m.travel_type == 'solo'))
        def poi(c):
            print("sights & landmarks", file=open(file_path, 'w'))
        @when_all((m.age == '18-24') & (m.sex == 'male') & (m.travel_type == 'family'))
        def poi(c):
            print("sights & landmarks", file=open(file_path, 'w'))
        @when_all((m.age == '18-24') & (m.sex == 'male') & (m.travel_type == 'friends'))
        def poi(c):
            print("nature & parks, tours, water & amusement parks, zoos & aquariums", file=open(file_path, 'w'))      

        # 18-24 female
        @when_all((m.age == '18-24') & (m.sex == 'female') & (m.travel_type == 'solo'))
        def poi(c):
            print("shopping, tours, museum, sights & landmarks, nature & parks", file=open(file_path, 'w'))
        @when_all((m.age == '18-24') & (m.sex == 'female') & (m.travel_type == 'family'))
        def poi(c):
            print("nature & parks, tours, sights & landmarks, water & amusement parks, zoos & aquariums", file=open(file_path, 'w'))
        @when_all((m.age == '18-24') & (m.sex == 'female') & (m.travel_type == 'friends'))
        def poi(c):
            print("tours, nature & parks, water & amusement parks, zoos & aquariums", file=open(file_path, 'w'))  
            
            
        # 25-34 male
        @when_all((m.age == '25-34') & (m.sex == 'male') & (m.travel_type == 'solo'))
        def poi(c):
            print("sights & landmarks , nature & parks", file=open(file_path, 'w'))
        @when_all((m.age == '25-34') & (m.sex == 'male') & (m.travel_type == 'family'))
        def poi(c):
            print("zoos & aquariums, sights & landmarks, fun & games, shopping ", file=open(file_path, 'w'))
        @when_all((m.age == '25-34') & (m.sex == 'male') & (m.travel_type == 'friends'))
        def poi(c):
            print("shopping, tours, museum, sights & landmarks", file=open(file_path, 'w'))

        # 25-34 female
        @when_all((m.age == '25-34') & (m.sex == 'female') & (m.travel_type == 'solo'))
        def poi(c):
            print("shopping, zoos & aquariums, nature & parks", file=open(file_path, 'w'))
        @when_all((m.age == '25-34') & (m.sex == 'female') & (m.travel_type == 'family'))
        def poi(c):
            print("nature & parks, zoos & aquariums, fun & games, tours, shopping, concerts & shows", file=open(file_path, 'w'))
        @when_all((m.age == '25-34') & (m.sex == 'female') & (m.travel_type == 'friends'))
        def poi(c):
            print("sights and landmarks, tours, concerts & shows", file=open(file_path, 'w'))      


        # 35-44 male
        @when_all((m.age == '35-44') & (m.sex == 'male') & (m.travel_type == 'solo'))  ### missing data, use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : '25-34', 'sex' : 'male' , 'travel_type' : 'solo'})
        @when_all((m.age == '35-44') & (m.sex == 'male') & (m.travel_type == 'family')) ### missing data, use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : '25-34', 'sex' : 'male' , 'travel_type' : 'family'})
        @when_all((m.age == '35-44') & (m.sex == 'male') & (m.travel_type == 'friends'))
        def poi(c):
            print("tours, nature & parks, fun & games", file=open(file_path, 'w'))      

        # 35-44 female
        @when_all((m.age == '35-44') & (m.sex == 'female') & (m.travel_type == 'solo'))
        def poi(c):
            print("shopping, tours, museum, sights & landmarks, outdoor activities, concerts & shows", file=open(file_path, 'w'))
        @when_all((m.age == '35-44') & (m.sex == 'female') & (m.travel_type == 'family'))
        def poi(c):
            print("tours, shopping, fun & games", file=open(file_path, 'w'))
        @when_all((m.age == '35-44') & (m.sex == 'female') & (m.travel_type == 'friends'))
        def poi(c):
            print("tours, outdoor activities, sights & landmarks", file=open(file_path, 'w'))   
            
            

        # 45-54 male
        @when_all((m.age == '45-54') & (m.sex == 'male') & (m.travel_type == 'solo'))
        def poi(c):
            print("sights & landmarks, nature & parks, water & amusement parks, outdoor activities, museums, shopping", file=open(file_path, 'w'))
        @when_all((m.age == '45-54') & (m.sex == 'male') & (m.travel_type == 'family'))
        def poi(c):
            print("fun & games, shopping, outdoor activities", file=open(file_path, 'w'))
        @when_all((m.age == '45-54') & (m.sex == 'male') & (m.travel_type == 'friends'))
        def poi(c):
            print("nature & parks, outdoor activities, fun & games, sights & landmarks", file=open(file_path, 'w'))      

        # 45-54 female
        @when_all((m.age == '45-54') & (m.sex == 'female') & (m.travel_type == 'solo'))
        def poi(c):
            print("shopping, tours, museums", file=open(file_path, 'w'))
        @when_all((m.age == '45-54') & (m.sex == 'female') & (m.travel_type == 'family'))
        def poi(c):
            print("shopping, tours, museum, fun & games", file=open(file_path, 'w'))
        @when_all((m.age == '45-54') & (m.sex == 'female') & (m.travel_type == 'friends'))
        def poi(c):
            print("fun & games, museum, sights & landmarks", file=open(file_path, 'w'))       



        # 55 and over
        @when_all((m.age == '55 and over') & (m.sex == 'male') & (m.travel_type == 'solo')) # missing data, use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : '45-54', 'sex' : 'male' , 'travel_type' : 'solo'})
        @when_all((m.age == '55 and over') & (m.sex == 'male') & (m.travel_type == 'family'))
        def poi(c):
            print("tours, museum, sights & landmarks", file=open(file_path, 'w'))
        @when_all((m.age == '55 and over') & (m.sex == 'male') & (m.travel_type == 'friends'))
        def poi(c):
            print("fun & games, tours, museum, sights & landmarks, outdoor activities, water & amusement parks", file=open(file_path, 'w'))      

        # 55 and over
        @when_all((m.age == '55 and over') & (m.sex == 'female') & (m.travel_type == 'solo'))  # missing data, use forward chainingg
        def poi(c):
            c.assert_fact({ 'age' : '45-54', 'sex' : 'female' , 'travel_type' : 'solo'})
        @when_all((m.age == '55 and over') & (m.sex == 'female') & (m.travel_type == 'family')) # missing data, use forward chaining
        def poi(c):
            c.assert_fact({ 'age' : '45-54', 'sex' : 'female' , 'travel_type' : 'family'})
        @when_all((m.age == '55 and over') & (m.sex == 'female') & (m.travel_type == 'friends'))
        def poi(c):
            print("shopping, tours, museum, sights & landmarks", file=open(file_path, 'w'))   


    assert_fact('POI',{ 'age': age, 'sex': sex, 'travel_type': travel_type })
    # assert_fact('POI',{ 'age': '25-34', 'sex': 'male', 'travel_type': 'solo' })

    # read recommended poi
    with open('POI.txt','r') as f:
        pois = f.read()
    pois = [x.strip(' ') for x in pois.strip('\n').split(',')]

    # read all poi
    attractions = pd.read_csv('attraction.csv')

    # save recommended poi into dictionary
    recommended_poi = {}

    for i in attractions['City'].unique():
        recommended_poi[i]=[{}] #[]

    for i in range(len(attractions)):
        for poi in pois:
            if poi in attractions['Category1'][i].lower():
                recommended_poi[attractions['City'][i]][0][attractions['Name'][i]] = {}
                recommended_poi[attractions['City'][i]][0][attractions['Name'][i]]['Website'] = attractions['Website'][i]
                recommended_poi[attractions['City'][i]][0][attractions['Name'][i]]['Image'] = attractions['Image'][i]


    # for i in range(len(attractions)):
    #     for poi in pois:
    #         if poi in attractions['Category1'][i].lower():
    #             x = {}
    #             attraction = attractions['Name'][i]
    #             x[attraction] = {}
    #             x[attraction]['Website'] = attractions['Website'][i]
    #             x[attraction]['Image'] = attractions['Image'][i]
    #             if x not in recommended_poi[attractions['City'][i]]:
    #                 recommended_poi[attractions['City'][i]].append(x)
                
    #             recommended_poi[attractions['City'][i]][attractions['Name'][i]] = {}
    #             recommended_poi[attractions['City'][i]][attractions['Name'][i]]['Website'] = attractions['Website'][i]
    #             recommended_poi[attractions['City'][i]][attractions['Name'][i]]['Image'] = attractions['Image'][i]

    return recommended_poi