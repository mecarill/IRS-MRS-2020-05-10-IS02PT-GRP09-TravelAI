from __future__ import print_function
from ortools.sat.python import cp_model
import collections
import pandas as pd
import json
import math
def csvconverter(flightcsv,hotelcsv):
    flight_d=pd.read_csv(flightcsv)
    hotel_d=pd.read_csv(hotelcsv)
    return flight_d,hotel_d

def datetoint(unit):
    return unit.year*100000000+unit.month*1000000+unit.day*10000+unit.hour*100+unit.minute

def flightDfCreator(df_une):
    df_une['Price'] = df_une['Price'].astype(float).astype(int)
    df_une['Departure Date'] = pd.to_datetime(df_une['Departure Date'], format='%Y-%m-%d')
    df_une['Arrival Date'] = pd.to_datetime(df_une['Arrival Date'], format='%Y-%m-%d')
    df_une = df_une.sort_values(by='Departure Date')

    flightData = []
    df = df_une[df_une["Departure City"].isin(df_une["Departure City"].unique()[1:])]
    df = df[df["Arrival City"].isin(df["Departure City"].unique())]

    # creating an empty array for front+back of list
    emptyli = []
    for i in df["Departure City"].unique():
        loclist = []
        for k in df["Departure City"].unique():
            templ = []
            loclist.append(templ)
        emptyli.append(loclist)
    flightData.append(emptyli)
    for i in df["Departure Date"].unique():
        datelist = []
        for j in df["Departure City"].unique():
            loclist = []
            for k in df["Departure City"].unique():
                templ = []
                tempdf = df[(df["Departure Date"] == i) & (df["Departure City"] == j) & (df["Arrival City"] == k)]
                for l in range(len(tempdf)):
                    templ.append(tempdf.iloc[l].Price)
                loclist.append(templ)
            datelist.append(loclist)
        flightData.append(datelist)
    flightData.append(emptyli)
    locations = df["Departure City"].unique()
    num_days = len(df_une["Departure Date"].unique())
    return df_une, flightData, locations, num_days

def startFliList(locations,df_une):
    startlocflight = []
    for i in range(len(locations)):
        some = []
        x = df_une[(df_une["Departure Date"] == df_une["Departure Date"].unique()[0]) & (
                df_une["Departure City"] == df_une["Departure City"].unique()[0]) & (
                           df_une["Arrival City"] == locations[i])]
        for j in range(len(x)):
            startloc1 = x.iloc[j].Price
            some.append(startloc1)
        startlocflight.append(some)
    return startlocflight

def endFliList(locations,df_une):
    endlocflight = []
    for i in range(len(locations)):
        some = []
        x = df_une[(df_une["Departure Date"] == df_une["Departure Date"].unique()[-1]) & (
                df_une["Departure City"] == locations[i]) & (
                           df_une["Arrival Airport"] == df_une["Departure City"].unique()[0])]
        for j in range(len(x)):
            endloc1 = x.iloc[j].Price
            some.append(endloc1)
        endlocflight.append(some)
    return endlocflight

def hotelListCreator(df_hotel, locations):
    # reading the hotel data and putting the price into a nested list for ortools to read
    df_hotel['Price'] = df_hotel['Price'].astype(int).astype(str).astype(int)
    hotelData = []
    for j in locations:
        datelist = []
        for i in df_hotel["Check In Date"].unique():
            selections = df_hotel[(df_hotel["Check In Date"] == i) & (df_hotel["City"] == j)]
            datelist.append(int(selections.Price))
        hotelData.append(datelist)
    return df_hotel, hotelData

def optimiser(locations, num_days, hotelData, df_hotel, flightData,df_une, startlocflight, endlocflight,adults,children):

### Setting up OR-Tools
    task_type = collections.namedtuple('task_type', 'start end interval')
    location_info = {}
    order = []
    durations = []
    model = cp_model.CpModel()
    for loc in range(len(locations)):
        suffix = '_%s' % (locations[loc])
        duration = model.NewIntVar(0, num_days - 1, 'dur' + suffix)
        start_var = model.NewIntVar(0, num_days - 1, 'start' + suffix)
        end_var = model.NewIntVar(0, num_days, 'end' + suffix)
        interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                            'interval' + suffix)
        location_info[loc] = task_type(start=start_var, end=end_var, interval=interval_var)
        durations.append(duration);
        order.append(interval_var)

# setting up constraints for no overlap of days, everyday must be used etc
    model.AddNoOverlap(order)
    model.Add(sum(durations) == num_days)
    for loc in range(len(locations)):
        model.Add(durations[loc] >= 1)
    for loc in range(len(locations)):
        for loc2 in range(len(locations)):
            if loc == loc2:
                pass;
            else:
                model.Add(location_info[loc].start != location_info[loc2].start)

# setting up constraints for hotel selection
    box = []
    box2 = []
    costs = []
    for loc in range(len(locations)):
        box1 = []
        box3 = []
        for day in range(num_days):
            b = model.NewBoolVar(str(day) + 'b')
            box1.append(b)
            c = model.NewBoolVar(str(day) + 'c')
            box3.append(c)
        box2.append(box3)
        box.append(box1)
    for day in range(num_days):
        ld = []
        for loc in range(len(locations)):
            ld.append(hotelData[loc][day])
        cost = model.NewIntVarFromDomain(cp_model.Domain.FromValues(ld), str(day))
        costs.append(cost)
    for loc in range(len(locations)):
        for day in range(num_days):
            model.Add(location_info[loc].start <= day).OnlyEnforceIf(box[loc][day])
            model.Add(location_info[loc].end > day).OnlyEnforceIf(box2[loc][day])

            model.Add(costs[day] != hotelData[loc][day]).OnlyEnforceIf(box[loc][day].Not())
            model.Add(costs[day] != hotelData[loc][day]).OnlyEnforceIf(box2[loc][day].Not())

# setting homelocation as first and last
    startflight=model.NewIntVar(0, 40000, 'startflight')
    endflight=model.NewIntVar(0, 40000, 'endflight')
    startflightint2=model.NewIntVar(0, 4, 'startflight')
    endflightint2=model.NewIntVar(0, 4, 'endflight')


    SFIr2=[]
    EFIr2=[]
    for j in range(len(startlocflight[0])):
        S1=model.NewBoolVar(str(j)+' SFI')
        E1=model.NewBoolVar(str(j)+' EFI')
        SFIr2.append(S1)
        EFIr2.append(E1)

# Setting up constraints for flight selection

    dayR = []
    dayR2 = []
    dayXOR = []
    for day in range(num_days):
        locR = []
        locR2 = []
        locXOR = []
        for loc in range(len(locations)):
            loc2R = []
            loc2R2 = []
            locXOR2 = []
            for loc2 in range(len(locations)):
                rul = model.NewBoolVar(str(day) + ' ' + str(loc) + ' ' + str(loc2))
                loc2R.append(rul)
                rul2 = model.NewBoolVar(str(day) + ' ' + str(loc) + ' ' + str(loc2))
                loc2R2.append(rul2)
                xor = model.NewBoolVar(str(day) + ' ' + str(loc) + ' ' + str(loc2))
                locXOR2.append(xor)
            locR.append(loc2R)
            locR2.append(loc2R2)
            locXOR.append(locXOR2)
        dayR.append(locR)
        dayR2.append(locR2)
        dayXOR.append(locXOR)
    flightcosts = []
    for day in range(num_days):
        flightcost = model.NewIntVar(0, 40000, 'day_' + str(day))
        flightcosts.append(flightcost)


    for day in range(num_days):
        for loc in range(len(locations)):
           for loc2 in range(len(locations)):

                model.Add((location_info[loc].end == day)).OnlyEnforceIf(dayR[day][loc][loc2])
                model.Add((location_info[loc].end != day)).OnlyEnforceIf(dayR[day][loc][loc2].Not())

                model.Add((location_info[loc2].start == day)).OnlyEnforceIf(dayR2[day][loc][loc2])
                model.Add((location_info[loc2].start != day)).OnlyEnforceIf(dayR2[day][loc][loc2].Not())

                model.AddBoolOr([dayR[day][loc][loc2].Not(), dayR2[day][loc][loc2].Not()]).OnlyEnforceIf(dayXOR[day][loc][loc2].Not())
                model.AddBoolAnd([dayR[day][loc][loc2], dayR2[day][loc][loc2]]).OnlyEnforceIf(dayXOR[day][loc][loc2])

                if len(flightData[day][loc][loc2]) > 0:
                    daycost = min(flightData[day][loc][loc2])
                else:
                    daycost = 0
                model.Add(flightcosts[day] == daycost).OnlyEnforceIf(dayXOR[day][loc][loc2])
                model.Add(flightcosts[day] != 0).OnlyEnforceIf(dayXOR[day][loc][loc2])



    startrule = []
    endrule = []
    XORStart = []
    XOREnd = []
    for loc in range(len(locations)):
        rul = model.NewBoolVar(str(loc) + ' startflight')
        rul2 = model.NewBoolVar(str(loc) + ' endflight')
        startrule.append(rul)
        endrule.append(rul2)
        XS = []
        XE = []
        for i in range(len(startlocflight[loc])):
            xor = model.NewBoolVar(str(loc) + ' xors')
            xor2 = model.NewBoolVar(str(loc) + ' xore')
            XS.append(xor)
            XE.append(xor2)
        XORStart.append(XS)
        XOREnd.append(XE)

    for loc in range(len(locations)):

        for j in range(len(startlocflight[loc])):
            model.Add(startflightint2 == j).OnlyEnforceIf(SFIr2[j])
            model.Add(startflightint2 != j).OnlyEnforceIf(SFIr2[j].Not())
            model.Add(endflightint2 == j).OnlyEnforceIf(EFIr2[j])
            model.Add(endflightint2 != j).OnlyEnforceIf(EFIr2[j].Not())

            model.Add(location_info[loc].start == 0).OnlyEnforceIf(startrule[loc])
            model.Add(location_info[loc].end == num_days).OnlyEnforceIf(endrule[loc])

            model.Add(location_info[loc].start != 0).OnlyEnforceIf(startrule[loc].Not())
            model.Add(location_info[loc].end != num_days).OnlyEnforceIf(endrule[loc].Not())

        model.Add(startflight != 0)
        model.Add(endflight != 0)
        for i in range(len(startlocflight[loc])):
            model.AddBoolOr([SFIr2[i].Not(), startrule[loc].Not()]).OnlyEnforceIf(XORStart[loc][i].Not())
            model.AddBoolAnd([SFIr2[i], startrule[loc]]).OnlyEnforceIf(XORStart[loc][i])

            model.AddBoolOr([EFIr2[i].Not(), endrule[loc].Not()]).OnlyEnforceIf(XOREnd[loc][i].Not())
            model.AddBoolAnd([EFIr2[i], endrule[loc]]).OnlyEnforceIf(XOREnd[loc][i])
            model.Add(startflight == startlocflight[loc][i]).OnlyEnforceIf(XORStart[loc][i])
            model.Add(endflight == endlocflight[loc][i]).OnlyEnforceIf(XOREnd[loc][i])


#No flights next day
    noflightrule=[]
    noflightrule2=[]
    for day in range(num_days):
        noflight = model.NewBoolVar(str(day) + ' noflight')
        noflightrule.append(noflight)
        noflight2 = model.NewBoolVar(str(day) + ' noflight')
        noflightrule2.append(noflight2)

        if day>1:
            model.Add(flightcosts[day] > 0).OnlyEnforceIf(noflightrule[day])
            model.Add(flightcosts[day] == 0).OnlyEnforceIf(noflightrule[day].Not())

            model.Add(flightcosts[day-1] > 0).OnlyEnforceIf(noflightrule2[day])
            model.Add(flightcosts[day-1] == 0).OnlyEnforceIf(noflightrule2[day].Not())

            model.AddBoolOr([noflightrule[day].Not(),noflightrule2[day].Not()])

    model.Add(flightcosts[0] == 0)
    model.Add(flightcosts[1] == 0)
    model.Add(flightcosts[-2] == 0)
    model.Add(flightcosts[-1] == 0)

# solving the model
    lowdur = model.NewIntVar(0, 2000, 'lowdur')
    maxdur = model.NewIntVar(0, 2000, 'maxdur')

    model.AddMinEquality(lowdur, durations)
    model.AddMaxEquality(maxdur, durations)

    model.Minimize(sum(costs*math.ceil(adults/2) + flightcosts*(adults+children)) + (maxdur - lowdur) * 100 + startflight + endflight)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assigned_jobs = collections.defaultdict(list)

    jsonlist = []
    for day in range(num_days):
        dict1 = {}
        for loc in range(len(locations)):
            if (solver.Value(location_info[loc].start) <= day) & (solver.Value(location_info[loc].end) > day):
                dict1['date'] = str(df_hotel["Check In Date"].unique()[day])
                dict1['location'] = locations[loc]
                dict1['hotel_cost'] = solver.Value(costs[day])
                dict1['hotel_name'] = \
                    df_hotel[(df_hotel['Check In Date'] == df_hotel["Check In Date"].unique()[day]) & (
                                df_hotel['City'] == locations[loc])]['Hotel'].to_string(index=False)[1:]
                dict1['flight_cost'] = solver.Value(flightcosts[day])
                if solver.Value(flightcosts[day]) == 0:
                    if day == 0:
                        dict1['flight_cost'] = solver.Value(startflight)
                        item = df_une[(df_une['Departure City'] == df_une['Departure City'].unique()[0]) & (
                                    df_une['Arrival City'] == locations[loc]) & (
                                                  df_une['Price'] == solver.Value(startflight)) & (
                                                  df_une['Departure Date'] == df_une["Departure Date"].unique()[day])]
                        item = item.iloc[0]

                        if type(item['Airline']) == str:
                            dict1['flight_name'] = item['Airline']
                        else:
                            dict1['flight_name'] = item['Airline'].to_string(index=False)

                        if type(df_une['Departure City'].unique()[0]) == str:
                            dict1['flight_departure_loc'] =  df_une['Departure City'].unique()[0] # .to_string(index=False)
                        else:
                            dict1['flight_departure_loc'] = df_une['Departure City'].unique()[0].to_string(index=False)

                        if type(locations[loc]) == str:
                            dict1['flight_arrival_loc'] = locations[loc]
                        else:
                            dict1['flight_arrival_loc'] = str(locations[loc])

                        if type(item['Departure Time']) == str:
                            dict1['flight_departure'] = item['Departure Time']
                        else:
                            dict1['flight_departure'] = item['Departure Time'].to_string(index=False)

                        if type(item['Arrival Time']) == str:
                            dict1['flight_arrival'] = item['Arrival Time']
                        else:
                            dict1['flight_arrival'] = item['Arrival Time'].to_string(index=False)

                    elif day == num_days - 1:
                        dict1['flight_cost'] = solver.Value(endflight)
                        item = df_une[(df_une['Departure City'] == locations[loc]) & (
                                df_une['Arrival City'] == df_une['Departure City'].unique()[0]) & (
                                              df_une['Price'] == solver.Value(endflight)) & (
                                              df_une['Departure Date'] == df_une["Departure Date"].unique()[day])]
                        item = item.iloc[0]

                        if type(item['Airline']) == str:
                            dict1['flight_name'] = item['Airline']
                        else:
                            dict1['flight_name'] = item['Airline'].to_string(index=False)

                        if type(locations[loc]) == str:
                            dict1['flight_departure_loc'] = locations[loc]
                        else:
                            dict1['flight_departure_loc'] = str(locations[loc])

                        if type(df_une['Departure City'].unique()[0]) == str:
                            dict1['flight_arrival_loc'] = df_une['Departure City'].unique()[0]
                        else:
                            dict1['flight_arrival_loc'] = df_une['Departure City'].unique()[0].to_string(index=False)

                        if type(item['Departure Time']) == str:
                            dict1['flight_departure'] = item['Departure Time']
                        else:
                            dict1['flight_departure'] = item['Departure Time'].to_string(index=False)

                        if type(item['Arrival Time']) == str:
                            dict1['flight_arrival'] = item['Arrival Time']
                        else:
                            dict1['flight_arrival'] = item['Arrival Time'].to_string(index=False)

                    else:
                        dict1['flight_name'] = ''
                        dict1['flight_departure_loc'] = ''
                        dict1['flight_arrival_loc'] = ''
                        dict1['flight_departure'] = ''
                        dict1['flight_arrival'] = ''
                else:
                    item = df_une[
                        (df_une['Departure City'] == jsonlist[day - 1]["location"]) & (
                                    df_une['Arrival City'] == locations[loc]) & (
                                    df_une['Price'] == solver.Value(flightcosts[day])) & (
                                    df_une['Departure Date'] == df_une["Departure Date"].unique()[day])]
                    item = item.iloc[0]
                    if type(item['Airline']) == str:
                        dict1['flight_name'] = item['Airline']
                    else:
                        dict1['flight_name'] = item['Airline'].to_string(index=False)

                    dict1['flight_departure_loc'] = jsonlist[day - 1]["location"]

                    if type(locations[loc]) == str:
                        dict1['flight_arrival_loc'] = locations[loc]
                    else:
                        dict1['flight_arrival_loc'] = str(locations[loc])

                    if type(item['Departure Time']) == str:
                        dict1['flight_departure'] = item['Departure Time']
                    else:
                        dict1['flight_departure'] = item['Departure Time'].to_string(index=False)

                    if type(item['Arrival Time']) == str:
                        dict1['flight_arrival'] = item['Arrival Time']
                    else:
                        dict1['flight_arrival'] = item['Arrival Time'].to_string(index=False)
                jsonlist.append(dict1)
    jsonlist = json.dumps(jsonlist)
    return jsonlist

def Optimiser(flight_d='testdata/flight_data (2).csv',hotel_d='testdata/hotel_data (1).csv',adults=1,children=0):
    if type(flight_d)==str:
        flight_d,hotel_d=csvconverter(flight_d,hotel_d)
    df_une, flightData, locations, num_days = flightDfCreator(flight_d)
    startlocflight = startFliList(locations,df_une)
    endlocflight= endFliList(locations,df_une)
    df_hotel, hotelData = hotelListCreator(hotel_d, locations)
    jsonlist = optimiser(locations, num_days, hotelData, df_hotel, flightData,df_une, startlocflight, endlocflight,adults,children)
    return jsonlist

if __name__ == '__main__':
    Optimiser()
