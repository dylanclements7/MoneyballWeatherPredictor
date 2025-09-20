from datetime import date
from geopy.geocoders import Nominatim
import requests
import json
import time
import os
import pickle
from pathlib import Path
import zipfile

"""
Group Project Name: Moneyball Weather Program
Group Members: Dylan C and Charlie V

!!! TO RUN THE PROGRAM, USER MUST HAVE PIP INSTALLED THEN INSTALL GEOPY AND REQUESTS TO YOUR COMPUTER !!!
(If you do not already have pip installed, go to: https://pip.pypa.io/en/stable/installation/ and install pip)
To install geopy and requests, run these in your terminal before continuing:
geopy: pip install geopy
requests: pip install requests
Make sure you are running kernel Python 3.11.4 (with anaconda)
"""
def zip():
    # This is not for the program this is for zipping the files
    python_filename = 'weather.py'
    text_filename = 'Readme.txt'
    zip_filename = 'unzipme.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        zip_file.write(python_filename)
    with zipfile.ZipFile(zip_filename, 'a') as zip_file:
        zip_file.write(text_filename)

def main():
    """ This will be the only function the user will have to call to use the program. It asks them if it is the start or end of the day and then it runs the corresponding class.
    """
    print('Hello, welcome to Moneyball Weather Program.' + '\n' + 'This application works by taking your location at the start of the day,' + '\n' + 'and telling you what you should wear, then at the end of the day,' + '\n' + 'you give us your feedback about how you felt wearing the stuff' + '\n')
    time.sleep(1)

    today = date.today()
    print("Today's date: " + str(today) + '\n')
    time.sleep(1)
    
    s_input = input('Is it the start or the end of your day?')
    if s_input == 'start':
        time.sleep(1)
        l = input('What city are you in?')
        c = l.lower()
        city = c.capitalize()
        start = Start(city)
        if start.lat_long != None:
            print(start)
        return start.save()

    elif s_input == 'end':
        feedback = input('How did you feel about what you wore today?' +  '\n' + '[1]: too hot' + '\n' + '[2]: too cold' + '\n' + '[3]: just right')
        if feedback == '1':
            end = End('too hot')
            end.change()
            print('Thank you for your feedback.' + '\n' + '\n' + 'Make sure to come back in the morning!')
            return end.save()
        elif feedback == '2':
            end = End('too cold')
            end.change()
            print('Thank you for your feedback.' + '\n' + '\n' + 'Make sure to come back in the morning!')
            return end.save()
        elif feedback == '3':
            end = End('just right')
            end.change()
            print('Thank you for your feedback.' + '\n' + '\n' + 'Make sure to come back in the morning!')
            return end.save()
        else:
            print('Invalid input. Please retry with a correct input.' + '\n')
            main()
    else:
        print("invalid input, please enter 'start' or 'end'" + '\n')
        main()

class Start:
    """ This class contains code that is for the start of the day part of the program
    """
    def __init__(self, city):
        """ This method initializes the city variable that is input into the class. 
        It also sets self.current_data and self.daily_data to the correct corresponding 
        text file of weather data in the API. We do this in the __init__ so that we only call the API 
        once per run, leading to shorter load times
        """
        self.city = city
        self.lat_long = self.place(self.city)
        api_key = '1a3e16bed418476caf4175831230412'
        self.current_weather_data = requests.get(f'https://api.weatherapi.com/v1/current.json?key={api_key}&q={self.lat_long}&aqi=no')
        self.daily_weather_data = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={self.lat_long}&aqi=no')
        self.current_data = self.current_weather_data.text
        self.daily_data = self.daily_weather_data.text

    
    def __repr__(self):
        """ This method constructs the string that will be returned to the user containing 
        information about the average temperature, precipitation, and what they should wear that day,
        """
        if self.lat_long != None:
            s = ''
            s += 'Average temperature today: ' + str(self.ave_temp()) + ' degrees fahrenheit.' + '\n' + '\n'
            if self.precipitation() == 'neither':
                s += 'It will not rain or snow today.' + '\n' + '\n'
            elif self.precipitation() == 'both':
                s += 'It will somehow rain and snow today.' + '\n' + '\n'
            elif self.precipitation() == 'rain':
                s += 'It will rain today.' + '\n' + '\n'
            else:
                s += 'It will snow today.' + '\n' + '\n'
            s += 'We reccomend that you wear '
            s += self.recommendation()
            s += ' today for maximum comfort.' + '\n' + '\n' + 'Make sure to submit your feedback tonight!'
            return s

    def save(self):
        """ This method saves the temperature for that day as a key in a dictionary in a pickle file. 
        If the pickle file has not been made yet, it makes the file, if it has, it will just add a new key. 
        It then fills the value for the key as 'empty' so we can change 'empty' later when we get their feedback in the end class
        """
        path = str(Path.cwd()) + '/user_data.pk'
        if os.path.exists(path):
            filename = 'user_data.pk'
            with open(filename, 'rb') as fi:
                user_dict = pickle.load(fi)
            if str(self.ave_temp()) in user_dict.keys():
                user_dict[str(self.ave_temp())].append('empty')
            else:
                user_dict[str(self.ave_temp())] = ['empty']
            with open(filename, 'wb') as fi:
                pickle.dump(user_dict, fi)
        else:
            open('user_data.pk', 'x')
            user_dict = {}
            filename = 'user_data.pk'
            user_dict[str(self.ave_temp())] = ['empty']
            with open(filename, 'wb') as fi:
                pickle.dump(user_dict, fi)
    
    def place(self, city):
        """ This method finds the longitude and latitude from the city the user input. 
        If they do not input a valid city, it will return an error message and run the main function again.
        """
        geolocator = Nominatim(user_agent = 'MyApp')
        try:
            location = geolocator.geocode(city)
            lat_long = str(location.latitude) + ',' + str(location.longitude)
            return lat_long
        except:
            print('Invalid city name entered, please try again' + '\n')
            time.sleep(1)
            main()

    def api_get(self, req):
        """ This method will load and return the correct API dictionary using the requested text file from the init method.
        """
        current_weather_dict = json.loads(self.current_data)
        daily_weather_dict = json.loads(self.daily_data)
        if req == 'current':
            return current_weather_dict
        elif req == 'daily':
            return daily_weather_dict
        else:
            #for if we need to use different dictionaries
            return 'error'
        
    def current_temp(self):
        """ This method returns the current_temp from the correct API dictionary
        """
        current_weather_dict = self.api_get('current')
        current_temp = (current_weather_dict['current']['temp_f'])
        return current_temp
    
    def ave_temp(self):
        """ This method returns the avg_temp from the correct API dictionary
        """
        daily_weather_dict = self.api_get('daily')
        avg_temp = daily_weather_dict['forecast']['forecastday'][0]['day']['avgtemp_f']
        return avg_temp
    
    def precipitation(self):
        """ This method returns if it is raining, snowing, neither, or both 
        using the data in the correct API dictionary
        """
        daily_weather_dict = self.api_get('daily')
        will_rain = (daily_weather_dict['forecast']['forecastday'][0]['day']['daily_will_it_rain'])
        will_snow = (daily_weather_dict['forecast']['forecastday'][0]['day']['daily_will_it_snow'])
        if will_rain == 0:
            if will_snow == 0:
                return 'neither'
            else:
                return 'snow'
        else:
            if will_snow == 0:
                return 'rain'
            else:
                return 'both'
        
    def recommendation(self):
        """ This method returns the correct recommendation for what the user should wear today. 
        It has two parts, one if there is no data therefor it is the user's first day, and one 
        using the user's data to change the baseline ranges, making what we suggest more to their liking"""
        path = str(Path.cwd()) + '/user_data.pk'
        if os.path.exists(path) is False:
            if self.ave_temp() <= 32 and self.ave_temp() >= 0:
                layers = 3
            elif self.ave_temp() >= 60:
                layers = 1
            elif self.ave_temp() < 0:
                return 'good luck'
            else:
                layers = 2
            
            if layers == 3:
                if self.ave_temp() <= 25:
                    if self.precipitation() == 'snow':
                        return 'a shirt, a hoodie, pants, a winter jacket, and cold accessories (hat, gloves, scarf, etc)'
                    elif self.precipitation() == 'both':
                        return 'a shirt, a hoodie, pants, a winter jacket, and cold accessories (hat, gloves, scarf, etc)'
                    else:
                        return 'a shirt, a hoodie, pants, and a winter jacket'
                else:
                    if self.precipitation() == 'rain':
                        return 'a shirt, a hoodie, pants, and a rain jacket'
                    elif self.precipitation() == 'snow':
                        return 'a shirt, a hoodie, pants, a light jacket, and cold accessories (hat, gloves, scarf, etc)'
                    elif self.precipitation() == 'both':
                        return 'a shirt, a hoodie, pants, a rain jacket, and cold accessories (hat, gloves, scarf, etc)'
                    else:
                        return 'a shirt, a hoodie, pants, and a light jacket'
            elif layers == 1:
                if self.ave_temp() <= 75:
                    return 'a long sleeve shirt and shorts'
                elif self.ave_temp() <= 100:
                    return 'a short sleeve shirt and shorts'
                else:
                    return 'good luck'
            else:
                if self.ave_temp() <= 52:
                    if self.precipitation() == 'rain':
                        return 'a shirt, a rain jacket, and pants'
                    else:
                        return 'a shirt, a hoodie, and pants'
                else:
                    if self.precipitation() == 'rain':
                        return 'a shirt, a rain jacket, and shorts'
                    else:
                        return 'a shirt, a hoodie, and shorts'
        else:
            filename = 'user_change_data.pk'
            with open(filename, 'rb') as fi:
                change = pickle.load(fi)
            with open(filename, 'wb') as fi:
                pickle.dump(change, fi)
        
            if self.ave_temp() <= 32 + change and self.ave_temp() >= 0 + change:
                layers = 3
            elif self.ave_temp() >= 60 + change:
                layers = 1
            elif self.ave_temp() < 0 + change:
                return 'good luck'
            else:
                layers = 2
            
            if layers == 3:
                if self.ave_temp() <= 25 + change:
                    if self.precipitation() == 'snow':
                        return 'a shirt, a hoodie, pants, a winter jacket, and cold accessories (hat, gloves, scarf, etc)'
                    elif self.precipitation() == 'both':
                        return 'a shirt, a hoodie, pants, a winter jacket, and cold accessories (hat, gloves, scarf, etc)'
                    else:
                        return 'a shirt, a hoodie, pants, and a winter jacket'
                else:
                    if self.precipitation() == 'rain':
                        return 'a shirt, a hoodie, pants, and a rain jacket'
                    elif self.precipitation() == 'snow':
                        return 'a shirt, a hoodie, pants, a light jacket, and cold accessories (hat, gloves, scarf, etc)'
                    elif self.precipitation() == 'both':
                        return 'a shirt, a hoodie, pants, a rain jacket, and cold accessories (hat, gloves, scarf, etc)'
                    else:
                        return 'a shirt, a hoodie, pants, and a light jacket'
            elif layers == 1:
                if self.ave_temp() <= 75 + change:
                    return 'a long sleeve shirt, and shorts'
                elif self.ave_temp() <= 100 + change:
                    return 'a short sleeve shirt, and shorts'
                else:
                    return 'good luck'
            else:
                if self.ave_temp() <= 52 + change:
                    if self.precipitation() == 'rain':
                        return 'a shirt, a rain jacket, and pants'
                    else:
                        return 'a shirt, a hoodie, and pants'
                else:
                    if self.precipitation() == 'rain':
                        return 'a shirt, a rain jacket, and shorts'
                    else:
                        return 'a shirt, a hoodie, and shorts'

class End:
    """ This class contains code that is for the end of the day part of the program 
    """
    def __init__(self, feedback):
        """ This method initializes the input feedback into self.feedback
        """
        self.feedback = feedback
        
    def save(self):
        """ This method replaces the dictionary value 'empty' we made as a filler in the 
        start class with the user's feedback (if they were too hot, too cold, or just right). 
        The key of this value in the dictionary is the average temperature that day. 
        It has to opening and taking the dictionary out of the pickle file, changing it, 
        then putting the dictionary back in and closing it
        """
        filename = 'user_data.pk'
        with open(filename, 'rb') as fi:
            user_dict = pickle.load(fi)
        for parts in user_dict.keys():
            for i in range(len(user_dict[parts])):
                if user_dict[parts][i] == 'empty':
                    user_dict[parts][i] = self.feedback
                    continue
        with open(filename, 'wb') as fi:
            pickle.dump(user_dict, fi)
    
    def change(self):
        """ This method makes two local variables, hot count and cold count that are 
        integers of how many times they were too cold or too hot. It then returns a 
        variable 'change' that is how many degrees the ranges of the baseline temperatures we made 
        should change to fit the user's preference
        """
        filename = 'user_data.pk'
        with open(filename, 'rb') as fi:
            user_dict = pickle.load(fi)
            hot_count = 0
            cold_count = 0
        for parts in user_dict.keys():
            for i in user_dict[parts]:
                if i == 'too hot':
                    hot_count += 1
                elif i == 'too cold':
                    cold_count += 1

        with open(filename, 'wb') as fi:
            pickle.dump(user_dict, fi)
        if hot_count > cold_count:
            change = -3.5
        elif cold_count > hot_count:
            change = 3.5
        else:
            change = 0
        self.save_change(change)
        return change
            
    def save_change(self, change):
        """ This method saves the change variable we made in the method above in its own pickle file 
        so that it can be kept between uses of the program. It uses the same technique as the above save functions, 
        by checking if the file exists, creating it, opening it, changing it, then dumping it and closing it. It also adds the current value of the 
        change variable to the value already in the file.
        """
        path = str(Path.cwd()) + '/user_change_data.pk'
        filename = 'user_change_data.pk'
        if os.path.exists(path):
            with open(filename, 'rb') as fi:
                user_change = pickle.load(fi)
            user_change += change
            with open(filename, 'wb') as fi:
                pickle.dump(user_change, fi)
        else:
            open(filename, 'x')
            with open(filename, 'wb') as fi:
                pickle.dump(change, fi)