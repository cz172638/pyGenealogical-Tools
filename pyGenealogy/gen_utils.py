'''
Created on 26 ago. 2017

@author: Val
'''
import logging
from messages.pyGenealogymessages import NO_VALID_CONVENTION, NO_VALID_ACCURACY
from messages.pyGenealogymessages import NO_VALID_BIRTH_DATE, NO_VALID_DEATH_DATE, NO_VALID_DEATH_AND_BURIAL
from datetime import date
from pyGenealogy import VALUES_ACCURACY
import requests

GOOGLE_GEOLOCATION_ADDRESS = "https://maps.googleapis.com/maps/api/geocode/json?"

naming_conventions = ["father_surname", "spanish_surname"]

def is_year(my_potential_year):
    '''
    A simple module to detect if a given string is a year. Notice than when using
    datetime module is not possible to make the difference and detect if 1894 is just
    a year compared to 1st Jan 1894 when using strptime
    '''
    try: 
        year = int(my_potential_year)
        if year > 2990: return False
        return True
    except ValueError:
        return False

#TODO: include further naming conventions
def get_children_surname(father_surname, mother_surname, selected_convention):
    '''
    Simple function that provides the surname of children given the surname of 
    both parents
    '''
    if (selected_convention == "father_surname"):
        return father_surname
    elif (selected_convention == "spanish_surname"):
        return father_surname + " " + mother_surname
    else:
        logging.error(NO_VALID_CONVENTION) 
        return ""
def get_name_from_fullname(full_name, list_father_surnames, list_mother_surnames):
    '''
    Given a full name, including surname, this function will provide out the first name of
    the person removing the surname of the person
    '''
    name_string = full_name
    merged_list = list_father_surnames + list_mother_surnames
    for surname in merged_list:
        name_string = name_string.replace(" " + surname, "")
    return name_string
def checkDateConsistency(birth_date, residence_date, baptism_date, marriage_date, death_date, burial_date,
                         accuracy_birth = "EXACT", accuracy_residence = "EXACT", accuracy_baptism = "EXACT", 
                         accuracy_marriage = "EXACT", accuracy_death = "EXACT", accuracy_burial = "EXACT"):
    '''
    Checker of the different dates are consistent
    '''
    #birth date is always the earliest date
    dates_death_check = []
    dates_birth_check = []
    burial_death = []
    #If there is no birth date included there is no need for the check
    if (birth_date != None):
        dates_birth_check.append(birth_date)
        check_dates_in_birth = [residence_date, baptism_date, marriage_date, death_date, burial_date]
        accuracy_in_birth = [accuracy_residence, accuracy_baptism, accuracy_marriage, accuracy_death, accuracy_burial]
        for index in range(0, len(check_dates_in_birth)):
            if (check_dates_in_birth[index] != None):
                if (accuracy_in_birth[index] == "ABOUT"):
                    #If we have an "about" the event has been around that year, with some margin, in this case, we just include
                    #the last date of the year for the check
                    dates_birth_check.append(date(check_dates_in_birth[index].year,12,31))
                else:
                    dates_birth_check.append(check_dates_in_birth[index])
        #Now we check here the data consistency
        if(min(dates_birth_check) < birth_date):
            logging.error(NO_VALID_BIRTH_DATE) 
            return False
    #Burial and Death dates are the latests ones
    if (burial_date != None): 
        if (accuracy_burial == "ABOUT"):
            burial_death.append(date(burial_date.year,12,31))
        else:
            burial_death.append(burial_date)
    if (death_date != None):
        intermediate_death = death_date  
        if (accuracy_death == "ABOUT"):
            intermediate_death = date(death_date.year,12,31)
        burial_death.append(intermediate_death)
        #Burial is never before than death date... unless in vampires, but out of scope
        if (intermediate_death > min(burial_death)):
            logging.error(NO_VALID_DEATH_AND_BURIAL) 
            return False
    if ( len(burial_death) > 0):
        check_dates_in_db = [residence_date, baptism_date, marriage_date]
        accuracy_in_db = [accuracy_residence, accuracy_baptism, accuracy_marriage]
        for index in range(0, len(check_dates_in_db)):
            if (check_dates_in_db[index] != None):
                if (accuracy_in_db[index] == "ABOUT"):
                    #If we have an "about" the event has been around that year, with some margin, in this case, we just include
                    #the first date of the  year
                    dates_death_check.append(date(check_dates_in_db[index].year,1,1))
                else:
                    dates_death_check.append(check_dates_in_db[index])
        #Now we check here the data consistency
        if (len(dates_death_check) > 0):
            if (max(dates_death_check) > max(burial_death)):
                logging.error(NO_VALID_DEATH_DATE) 
                return False
    return True

def getBestDate(date1, accuracy1, date2, accuracy2):
    '''
    This method takes 2 dates with their accuracy and returns the most probable
    date
    '''
    #TODO: we need to change the model fo the data to allow the inclusion of 2 values
    #in such case we will have the possibility of having before and after
    #Wrong accuracy provided will provide None data
    if (not accuracy1 in VALUES_ACCURACY) or (not accuracy2 in VALUES_ACCURACY):
        logging.error(NO_VALID_ACCURACY) 
        return None, None
    #If we have an exact date, that's the one!
    if (accuracy1 == "EXACT"):
        return date1, accuracy1
    elif (accuracy2 == "EXACT"):
        return date2, accuracy2
    #Ok, now AFTER or BEFORE becomes more precise
    if (accuracy1 in ["BEFORE", "AFTER"]):
        return date1, accuracy1
    elif (accuracy2 in ["BEFORE", "AFTER"]):
        return date2, accuracy2
    else:
        #The only option is having 2 abouts... we get the middle value
        newyear = int((date1.year +date2.year)/2)
        return date(newyear,1,1), accuracy1
    
def get_formatted_location(location_string, language="en"):
    '''
    This function will provide a standard location based on google maps service
    online
    '''
    output = {}
    output["raw"] = location_string
    url = GOOGLE_GEOLOCATION_ADDRESS + language + "&address=" + location_string
    r = requests.get(url)
    data = r.json()
    if (data["status"] == "OK"):
        #Received data is ok, we can proceed
        for result_input in data["results"][0].keys():
            if(result_input == "geometry"):
                #As we got the location details, let's get them
                output["latitude"] = data["results"][0]["geometry"]["location"]["lat"]
                output["longitude"] = data["results"][0]["geometry"]["location"]["lng"]
            elif(result_input == "address_components"):  
                #This is the data of the name of the location
                for level in  data["results"][0]["address_components"]:
                    if "locality" in level["types"]: output["city"] = level["long_name"]
                    elif "administrative_area_level_2" in level["types"]: output["county"] = level["long_name"]
                    elif "administrative_area_level_1" in level["types"]: output["state"] = level["long_name"]
                    elif "country" in level["types"]: output["country"] = level["long_name"]
    else:
        return None
    if (not location_string.split(",")[0] in output.values()):
        output["place_name"] = location_string.split(",")[0]
    return output
