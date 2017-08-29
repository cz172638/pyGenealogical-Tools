'''
Created on 26 ago. 2017

@author: Val
'''
import unittest
from datetime import date
from pyGenealogy.gen_utils import is_year, get_children_surname, get_name_from_fullname, checkDateConsistency, getBestDate
from tests.FIXTURES import RIGHT_YEAR, RIGHT_YEAR_IN_A_TEXT, WRONG_YEAR, JUST_TEXT, RIGHT_YEAR_IN_A_DATE
from tests.FIXTURES import FATHER_SURNAME, MOTHER_SURNAME, SPANISH_CHILD_SURNAME
from tests.FIXTURES import FULL_NAME, FULL_NAME_SPANISH, ACTUAL_NAME

class Test(unittest.TestCase):
    '''
    This module tests all functions inside pyGenealogy, but excluding the main
    class common_profile
    '''


    def test_correct_year_detection(self):
        '''
        Tests correct year detection
        '''
        assert(is_year(RIGHT_YEAR))
        self.assertFalse(is_year(RIGHT_YEAR_IN_A_DATE))
        self.assertFalse(is_year(RIGHT_YEAR_IN_A_TEXT))
        self.assertFalse(is_year(WRONG_YEAR))
        self.assertFalse(is_year(JUST_TEXT))
    
    def test_children_surname(self):
        '''
        Test output of children surname
        '''
        assert(get_children_surname(FATHER_SURNAME, MOTHER_SURNAME, "father_surname") == FATHER_SURNAME)
        assert(get_children_surname(FATHER_SURNAME, MOTHER_SURNAME, "spanish_surname") == SPANISH_CHILD_SURNAME)
        assert(get_children_surname(FATHER_SURNAME, MOTHER_SURNAME, "wrong_input") == "")
    
    def test_get_name(self):
        '''
        Test getting name out of complete name
        '''
        #Surnames
        list_father = [FATHER_SURNAME]
        list_mother = [MOTHER_SURNAME]
        assert(get_name_from_fullname(FULL_NAME, list_father, list_mother) == ACTUAL_NAME)
        assert(get_name_from_fullname(FULL_NAME_SPANISH, list_father, list_mother) == ACTUAL_NAME)
    
    def test_date_check(self):
        '''
        Test of the function for date check
        '''
        date1 = date(2017,1,1)
        date2 = date(2016,1,1)
        date3 = date(2015,1,1)
        date2b = date(2014,2,1)
        date4 = date(2014,1,1)
        assert(checkDateConsistency("",date2b, "","","",""))
        assert(checkDateConsistency(date4,"", "","","",""))
        assert(checkDateConsistency(date4,"", "","","",date1))
        assert(checkDateConsistency(date4,"", date3,date2,date1,""))
        
        assert(not checkDateConsistency(date1,"", "","",date4,""))
        assert(not checkDateConsistency("","", date1,"",date4,""))
        assert(not checkDateConsistency(date1,"", date4,"","",""))
        #Checking that about dates are ok although the date2b is later than date4
        assert(checkDateConsistency(date2b, "", "", "", date4, date4, accuracy_death = "ABOUT", accuracy_burial = "ABOUT"))
    
    def test_getting_a_date(self):
        '''
        Test the module for merging dates
        '''
        date1 = date(2018,1,1)
        date2 = date(2016,1,1)
        date3, accuracy3 = getBestDate(date1, "EXACT", date2, "EXACT")
        assert(date3 == date1)
        assert(accuracy3 == "EXACT")
        
        date4, accuracy4 = getBestDate(date1, "AFTER", date2, "EXACT")
        assert(date4 == date2)
        assert(accuracy4 == "EXACT")
        
        date5, accuracy5 = getBestDate(date1, "AFTER", date2, "BEFORE")
        assert(date5 == date1)
        assert(accuracy5 == "AFTER")
        
        date6, accuracy6 = getBestDate(date1, "ABOUT", date2, "BEFORE")
        assert(date6 == date2)
        assert(accuracy6 == "BEFORE")
        
        date7, accuracy7 = getBestDate(date1, "ABOUT", date2, "ABOUT")
        assert(date7 == date(2017,1,1))
        assert(accuracy7 == "ABOUT")
        
        date8, accuracy8 = getBestDate(date1, "LALALA", date2, "ABOUT")
        assert(date8 == None)
        assert(accuracy8 == None)
        
        
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()