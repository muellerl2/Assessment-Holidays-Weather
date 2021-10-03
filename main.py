# This is a sample Python script.
from datetime import datetime
from datetime import date
import json
yearList = [2020, 2022, 2023, 2024]
from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests

# This is our decorator, which prints a delete message for whatever holiday we choose to delete in our
# delete method
def printDelete(decorated_func):
    def inner_fn(*args, **kwargs):
        print("Deleted %s from the list of holidays" % str(args[1]))
        evaluated = decorated_func(*args, **kwargs)
        return evaluated
    return inner_fn

# We use the dataclass module to construct our holiday class. It has two
# attributes, the name of the holiday and the date
@dataclass
class holiday:
    name: str
    date: datetime.date

    def __str__(self):
        displayed = self.name + " " + "(" + str(self.date) + ")"
        return displayed

# This method converts a list of dictionaries to a list of holiday objects
def convertToObject(listDictionaries):
    converted = []
    for i in range(len(listDictionaries)):
        makeConvert = holiday(listDictionaries[i]['name'], listDictionaries[i]['date'])
        converted.append(makeConvert)
    return converted

# This is our deletion method
@printDelete
def deleteObject(listObjects, objectRemoved):
    objectRemoved = objectRemoved.lower()
    found = False
    instance = None
    for i in range(len(listObjects)):
        if listObjects[i].name.lower() == objectRemoved:
            found = True
            instance = i
    if found:
        listObjects.pop(instance)
    if not found:
        print(objectRemoved + "not found.")
    return listObjects

# This is our initial user interface menu, which we can only leave via the exit method
def startmenu(holidays):
    notDone = True
    while notDone:
        print("""Holiday Management
    ===================
    There are %i holidays stored in the system.""" % len(holidays))
        inputImproper = True
        while inputImproper:
            try:
                userInput = int(input("""Holiday Menu
        ================
        1. Add a Holiday
        2. Remove a Holiday
        3. Save Holiday List
        4. View Holidays
        5. Exit
        Please input your selection: """))
                if userInput != 1 and userInput != 2 and userInput != 3 and userInput != 4 and userInput != 5:
                    print("That number is out of range. Input a number from 1-5.")
                else:
                    inputImproper = False
                    if userInput == 1:
                        holidays = addHoliday(holidays)
                    if userInput == 2:
                        holidays = removeHoliday(holidays)
                    if userInput == 3:
                        saveHolidays(holidays)
                    if userInput == 4:
                        viewHolidays(holidays)
                    if userInput == 5:
                        exit(0)
            except ValueError:
                print("That's not a number. Try again.")

# This function takes in a list of holiday objects, and in turn it adds a holiday based on user input.
def addHoliday(holidays):
    print("""Add a Holiday
    =============""")
    notDone = True
    while notDone:
        holidayToAdd = str(input("Holiday Name: "))
        invalidInput = True
        while invalidInput:
            try:
                inputDate = datetime.strptime(input("Holiday Date: "), '%Y-%m-%d').date()
                invalidInput = False
                newHoliday = holiday(holidayToAdd, inputDate)
                holidays.append(newHoliday)
            except ValueError:
                print("""Error:
    Invalid date.  Please try again.""")
        yesNo = str(input("Would you like to input another holiday? [y/n]: ")).lower()
        if yesNo == 'n':
            notDone = False
            return holidays

# This program removes holidays
def removeHoliday(holidays):
    print("""Remove a Holiday
================""")
    notDone = True
    while notDone:
        notAHoliday = True
        while notAHoliday:
            inputHoliday = str(input("Holiday Name: "))
            foundHoliday = False
            # We first make sure that the holiday is actually in the system
            for i in range(len(holidays)):
                if inputHoliday == holidays[i].name:
                    foundHoliday = True
            if not foundHoliday:
                print("Error. %s not found." % inputHoliday)
            else:
                holidays = deleteObject(holidays,inputHoliday)
                # We loop through and allow the removal of multiple holidays
                anotherHoliday = str(input("Would you like to remove another holiday? [y/n]: ")).lower()
                if anotherHoliday == 'n':
                    return holidays

# This function shows us holidays for a selected series of years
def viewHolidays(holidays):
    global yearList
    not2021 = False
    invalidInput = True
    inputYear = 0
    filteredByYear = []

    # We Yihua-proof the inputs, so that only integers are accepted
    while invalidInput:
        try:
            inputYear = int(input("Which year?: "))
            if inputYear == 2021:
                invalidInput = False
                filteredByYear = list(filter(lambda x: x.date.year == inputYear, holidays))
            # We retrieve data from other years
            elif inputYear in yearList:
                invalidInput = False
                not2021 = True
                holidays = parseHolidays(inputYear)
                holidays = convertToObject(holidays)
                filteredByYear = list(filter(lambda x: x.date.year == inputYear, holidays))
            else:
                print("That's not a valid year.")
        except ValueError:
            print("That's not a year!")
    print(len(filteredByYear))
    invalidInput = True

    #We have to make sure that the input is valid so there isn't an error
    while invalidInput:
        getWeather = False
        listWeeks = range(1,53)
        inputWeek = input("Which week? #[1-52, Leave blank for the current week]: ")
        if inputWeek != '':
            inputWeek = int(inputWeek)

        if inputWeek == '' and not not2021:
            inputWeek = date.today().isocalendar()[1]
            yesNo = str(input("Would you like to see this week's weather? [y/n]: ")).lower()
            if yesNo == 'y':
                getWeather = True
            invalidInput = False
        elif inputWeek == '' and not2021:
            print("Sorry, you have to select an integer week if you're not in the current year.")
        elif inputWeek in listWeeks:
            invalidInput = False
        else:
            print("That's not a valid week, try again.")
    filteredByWeek = list(filter(lambda x: x.date.isocalendar()[1] == inputWeek, filteredByYear))
    if getWeather:
        weatherList = queryAPI()
    #We check to see if there are still upcoming holidays this week, since our API cannot actually
    # get dates in the past.
    triggered = False
    for i in range(len(filteredByWeek)):
        print(filteredByWeek[i], end = '')
        if getWeather:
            triggered = weatherPrint(weatherList, filteredByWeek[i].date)
        elif not2021:
            print(" ")
    if not triggered:
        # Our API doesn't have historical data, so we print off the holidays and give an explanation
        # for why we can't get the weather: either the data is too far out in the past or the future
        # or it is from earlier in the week, which we also can't get data for.
        if not2021:
            print("We can't get weather for non-2021 years, sorry!")
        else:
            print("Sorry we couldn't get weather, but all the holidays for this week have already happened!")

# This helper function prints the weather, assuming that there are holidays upcoming for weather
# to print
def weatherPrint(weatherList, holidayDate):
    triggered = False
    for i in range(len(weatherList)):
        if holidayDate == weatherList[i]['date']:
            print(" - " + weatherList[i]['weather'])
            triggered = True
            break
    if not triggered:
        print(" ")
    return triggered

def getHTML(url):
    response = requests.get(url)
    return response.text

# This is our web scraping function.
# We parse in a given list of holidays. We specifically take in a year.
def parseHolidays(inputYear):
    htmlInput = "https://www.timeanddate.com/holidays/us/" + str(inputYear)
    html = getHTML(htmlInput)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('tbody')
    holidays = []
    listNames = []
    for row in table.find_all_next('tr'):
        holidayName = row.find_next('a').string
        # 'let us know' is not a holiday, and we also want to avoid duplicate holidays
        if holidayName not in listNames and holidayName != 'let us know':
            holiday = {}
            holiday['name'] = holidayName
            listNames.append(holidayName)
            if row.find_next('th') is not None:
                # We convert to a date
                holiday['date'] = datetime.strptime(row.find_next('th').string
                                                        + ' ' + str(inputYear), '%b %d %Y').date()
            holidays.append(holiday)
    return holidays
# Press the green button in the gutter to run the script.

def saveHolidays(holidays):
    invalidInput = True
    while invalidInput:
        yesNo = str(input("""Saving Holiday List
    ====================
    Are you sure you want to save your changes? [y/n]: """)).lower()
        if yesNo == 'y':
            jsonDumper(holidays)
            print("""Success:
    Your changes have been saved.""")
            invalidInput = False
        elif yesNo == 'n':
            print("""Canceled:
    Holiday list file save canceled.""")
            invalidInput = False
        else:
            print("Invalid input. Please input yes or no.")

#This function puts a list of holiday objects into a json by converting them into a list of dictionaries, then
# putting that list of dictionaries into another dictionary, as required
def jsonDumper(holidays):
    listHolidays = []
    for i in range(len(holidays)):
        newDic = {}
        newDic['name'] = holidays[i].name
        newDic['date'] = str(holidays[i].date)
        listHolidays.append(newDic)
    emptyDic = {}
    emptyDic['holidays'] = listHolidays
    listJSON = json.dumps(emptyDic, indent = 4)
    with open(r"C:\Users\muell\PycharmProjects\scraper\sample.json", "w") as outfile:
        outfile.write(listJSON)

def readJson():
    with open("holidays.json") as f:
        jsonFile = json.load(f)
        listHolidays = jsonFile['holidays']
        for i in range(len(listHolidays)):
            listHolidays[i]['date'] = datetime.strptime(listHolidays[i]['date'], '%Y-%m-%d').date()
        return listHolidays
    f.close()

# This merges together two lists of holidays
def mergeHolidays(holiday1, holiday2):
    for i in range(len(holiday1)):
        holiday2.append(holiday1[i])
    return holiday2

def queryAPI():
    response = requests.get('https://api.tomorrow.io/v4/timelines?location=-90,45&fields=weatherCode&timesteps=1d&units=metric&apikey=8ikCjPV4TolYqlj9Ad805by2mxaDp2Wq')
    weatherDic = response.json()
    cutWeather = weatherDic['data']['timelines'][0]['intervals']
    listWeather = []
    for i in range(7):
        newDic = {}
        day = cutWeather[i]
        #We slice off any excess tags that would make it impossible to convert to a date format
        day['startTime'] = day['startTime'][0:10]
        newDic['date'] = datetime.strptime(day['startTime'], '%Y-%m-%d').date()
        weatherCode = day['values']['weatherCode']
        weather = ''
        if weatherCode == 1000:
            weather = 'Clear'
        elif weatherCode == 1001:
            weather = 'Cloudy'
        elif weatherCode == 1100:
            weather = 'Mostly Clear'
        elif weatherCode == 1101:
            weather = 'Partly Cloudy'
        elif weatherCode == 1102:
            weather = 'Mostly Cloudy'
        elif weatherCode == 2000:
            weather = 'Fog'
        elif weatherCode == 2100:
            weather = 'Light Fog'
        elif weatherCode == 3000:
            weather = 'Light Wind'
        elif weatherCode == 3001:
            weather = 'Wind'
        elif weatherCode == 3002:
            weather = 'Strong Wind'
        elif weatherCode == 4000:
            weather = 'Drizzle'
        elif weatherCode == 4001:
            weather = 'Rain'
        elif weatherCode == 4200:
            weather = 'Light Rain'
        elif weatherCode == 4201:
            weather = 'Heavy Rain'
        elif weatherCode == 5000:
            weather = 'Snow'
        elif weatherCode == 5001:
            weather = 'Flurries'
        elif weatherCode == 5100:
            weather = 'Light Snow'
        elif weatherCode == 5101:
            weather = 'Heavy Snow'
        elif weatherCode == 6000:
            weather = 'Freezing Drizzle'
        elif weatherCode == 6001:
            weather = 'Freezing Rain'
        elif weatherCode == 6200:
            weather = 'Light Freezing Rain'
        elif weatherCode == 6201:
            weather = 'Heavy Freezing Rain'
        elif weatherCode == 7000:
            weather = 'Ice Pellets'
        elif weatherCode == 7101:
            weather = 'Heavy Ice Pellets'
        elif weatherCode == 7102:
            weather = 'Light Ice Pellets'
        elif weatherCode == 8000:
            weather = 'Thunderstorm'

        newDic['weather'] = weather
        listWeather.append(newDic)
    return listWeather

if __name__ == '__main__':
    queryAPI()
    holidaysInit = readJson()
    holidays = parseHolidays(2021)
    merged = mergeHolidays(holidays, holidaysInit)
    listObjects = convertToObject(merged)
    startmenu(listObjects)
    #jsonDumper(merged)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
