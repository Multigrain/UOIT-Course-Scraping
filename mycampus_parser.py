from bs4 import BeautifulSoup
import re
import urllib
#import os FOR TESTING
from expressions import *


def generateURL(year, semester, subject):
    url = 'https://ssbp.mycampus.ca/prod/bwckschd.p_get_crse_unsec'
    url += '?TRM=U&term_in='
    url += year
    url += semester
    url += '&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj='
    url += subject
    url += '&sel_crse=&sel_title=&sel_schd=%25&sel_insm=%25&sel_from_cred=&sel_to_cred=&sel_camp=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a'
    return url

def readURL(url):
    webpage = BeautifulSoup(urllib.urlopen(url).read(), 'html5lib')
    return webpage

def parseCourseHeader(webpage_contents, course_info):
    for course in webpage_contents.find_all('th', {'class' : "ddheader", 'scope' : "col"}):
        current_course = {}
        matches = re.search(regex_course_header, str(course.next))

        #TESTING
        #if not matches:
        #    print str(course.next)
        #    os.system('read -s -n 1 -p "Press any key to continue..."')

        current_course['title'] = matches.group(1)
        current_course['crn'] = matches.group(2)
        current_course['subject'] = matches.group(3)
        current_course['code'] = matches.group(4)
        current_course['section'] = matches.group(5)

        course_info.append(current_course)

def parseCourseInfo(webpage_contents, course_info):
    course_index = 0

    for course in webpage_contents.find_all('td', {'class' : 'dddefault'}):

        #ignores fields containing information such as checkboxes & prereqs
        if not course.parent.has_attr('align'):
            #reads information before tables
            for field in course.find_all('span', {'class' : 'fieldlabeltext'}):
                if str(field.next).strip().find('Associated Term') >= 0:
                    matches = re.search(regex_course_term, str(field.next.next).strip())

                    course_info[course_index]['institution'] = matches.group(1)
                    course_info[course_index]['term'] = matches.group(2)
                    course_info[course_index]['year'] = matches.group(3)
                elif str(field.next).strip().find('Registration Dates') >= 0:
                    matches = re.search(regex_course_registration, str(field.next.next).strip())

                    course_info[course_index]['registration_from'] = matches.group(1)
                    course_info[course_index]['registration_to'] = matches.group(2)
                elif str(field.next).strip().find('Levels') >= 0:
                    course_info[course_index]['level'] = str(field.next.next).strip()

            #reads course availability table table
            course_reg_table = course.find('table', {'class' : 'bordertable', 'summary' : 'This layout table is used to present the seating numbers.'})

            course_availability = course_reg_table.find_all('td', {'class' : 'dbdefault'})
            course_info[course_index]['capacity'] = str(course_availability[0].text)
            course_info[course_index]['actual'] = str(course_availability[1].text)
            course_info[course_index]['remaining'] = str(course_availability[2].text)

            #reads course info table
            course_sched_table = course.find('table', {'class' : 'bordertable', 'summary' : 'This table lists the scheduled meeting times and assigned instructors for this class.'})

            if course_sched_table:
                course_info[course_index]['sessions'] = []

                for row in course_sched_table.find_all('tr')[1:]:
                    elements = row.find_all('td', {'class' : 'dbdefault'})
                    current_session = {}

                    if str(elements[0].text.strip()):
                        current_session['week'] = str(elements[0].text.strip())
                    else:
                        current_session['week'] = ''

                    matches = re.search(regex_timerange ,str(elements[2].text).strip())
                    if matches:
                        current_session['start_time'] = matches.group(1)
                        current_session['finish_time'] = matches.group(4)
                    else:
                        current_session['start_time'] = 'TBA'
                        current_session['finish_time'] = 'TBA'

                    current_session['day'] = str(elements[3].text.strip())
                    current_session['location'] = str(elements[4].text.strip())

                    matches = re.search(regex_daterange ,str(elements[5].text).strip())
                    if matches:
                        current_session['start_day'] = matches.group(1)
                        current_session['finish_day'] = matches.group(2)
                    else:
                        current_session['start_day'] = 'TBA'
                        current_session['finish_day'] = 'TBA'

                    current_session['type'] = str(elements[6].text.strip())
                    current_session['instructor'] = str(elements[7].text.strip())

                    #sets course instructors if lecture
                    if current_session['type'] == 'Lecture':
                        course_info[course_index]['instructor'] = current_session['instructor']

                    course_info[course_index]['sessions'].append(current_session)

            course_index += 1

def parseCourses(year, sem, subject):
    courses = []

    webpage_response = readURL(generateURL(year, sem, subject))

    main_table = webpage_response.find('table', {'class' : 'datadisplaytable', 'summary' : 'This layout table is used to present the sections found'})

    #checks that their are courses available for the specified subject
    if not main_table:
        return

    #parses course header info
    parseCourseHeader(main_table, courses)

    #parses course contents info
    parseCourseInfo(main_table, courses)

    return courses
