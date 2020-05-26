import requests
import csv
import xml.etree.ElementTree as ET
import http.client
import urllib
from datetime import datetime
from loguru import logger

def loadYR():
    url = 'https://www.yr.no/sted/Norge/Oslo/Oslo/Oslo/varsel_time_for_time.xml'
    r = requests.get(url)
    with open('yrweather.xml', 'wb') as f:
        f.write(r.content)

def parseXML(xmlfile):
    # create element tree object
    tree = ET.parse(xmlfile)

    # get root element
    root = tree.getroot()
    print(root.text)
    # empty list for hour-by-hour weather data
    weather_data = []

    #iterate through hour weather data
    for time in root.findall('forecast/tabular/time'):
        weather_hour = {}
        #get the hour of day
        time_of_hour = time.get('from')
        #get the temperature and rainfall for the hour
        temp = time.find('temperature').get('value')
        rain = time.find('precipitation').get('value')

        try: #only gives '0', fix
            rain_max = time.find('precipication').get('maxvalue')

        except:
            rain_max = '0'
        try: #only gives '0', fix
            rain_min = time.find('precipication').get('minvalue')
        except:
            rain_min = '0'
        #add weatherdata to a list, and add list to dictionary with hour as key and list as value
        hour_data = [temp,rain, rain_max, rain_min]
        weather_hour[time_of_hour] = hour_data
        #append dict of hour weather data, to list of all weather data
        weather_data.append(weather_hour)
    return weather_data

'''        #Iterate child elements of item (Iterate through weather data in each weather hour)
        for child in item:
            weather_hour[child.tag] = child.text
            print(child.tag)
            print(weather_hour)
        weather_data.append(weather_hour)'''



def isitrain_today(weather_data):
    rain_hour = []
    #Get date from datetime, convert to string in order to compare with yr data
    time = str(datetime.now()) #use datetime to only get weather data from the same date (or 24 hours?)
    today = time.split(' ')[0]


    # now we can use "today" to compare with "date" and get todays yr data
    #print(date)
    for hour in weather_data:
        #print(hour)
        date_with_time = next(iter(hour))
        date = date_with_time.split('T')[0]
        #print(date)

        if date == today:
            for time,weather in hour.items():
                t = time[11:13]
                rain_number = float(weather[1])
                if rain_number>0:
                    print(t + ': RAIN')
                    rain_hour.append(t)
                else:
                    print('no rain')
                    None

    print(rain_hour)
    return rain_hour



def rain_message(rain_hour):
    rain_message = ''
    rain_text = ''
    for hour in rain_hour:
        rain_text = rain_text + str(hour) + ', '
    rain_message = 'Det blir regn klokken: ' + rain_text
    print(rain_message)
    return rain_message

def send_push(rain_message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")


    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({"token": "ax924yb7p1pbq8gqz5gn1682sg4xz7",
                     "user": "unsjti74smnqhabswtpuypeonk7goh",
                     "message": rain_message,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()





loadYR()
weather_data = parseXML('yrweather.xml')

rain_hour = isitrain_today(weather_data)

rain_message = rain_message(rain_hour)
send_push(rain_message)

logger.add('file_{time}.log')