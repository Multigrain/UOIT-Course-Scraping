import time
import MySQLdb
import mysql_crud as dbCrud
from dateutil import parser
from mycampus_parser import parseCourses, findSubjects

config_location = "~/.my.cnf"
selected_database = "mycampus"
term_key = {'Winter' : '01', 'Spring/Summer' : '05', 'Fall' : '09'}

#Replace with arguments for reusability on different semesters
cur_year = '2016'
cur_term = '01'

#Finds all the subjects for the specified semester
subjects = findSubjects(cur_year, cur_term)

#Find courses for each subject and add to database
db = MySQLdb.connect(read_default_file=config_location, db=selected_database)
for subject in subjects:
    courses = parseCourses(cur_year, cur_term, subject)

    for course in courses:
        #Parses levels
        course_levels = course['level'].split(", ")

        #Parses instructors determining if they are primary instructor
        instructors = []
        course_instructors = course['instructors'].split(", ")
        for instructor in course_instructors:
            primary_instr = instructor.find('(P)')

            if instructor == 'TBA':
                continue
            #If primary instructor remove tag and register as primary
            if primary_instr > 0:
                instructors.append([instructor[:primary_instr - 1], True])
            else:
                instructors.append([instructor, False])

        #Inserts course and section data
        course_id = dbCrud.insertCourse(db, course['subject'], course['code'], course['title'], course['year'], term_key[course['term']], course_levels)
        section_id = dbCrud.insertSection(db, course_id, course['sessions'][0]['type'], course['section'], instructors, course['crn'])
        dbCrud.insertAvailability(db, section_id, int(course['capacity']), int(course['actual']), int(course['remaining']))

        for session in course['sessions']:
            #Parses week
            if session['week'] == 'W1':
                session_week = 1;
            elif session['week'] == 'W2':
                session_week = 2;
            else:
                session_week = 0;

            #Parses start/end date/time
            if session['day'] != '':
                session_day = session['day']
            else:
                session_day = None

            if session['start_day'] != 'TBA':
                session_startD = parser.parse(session['start_day']).strftime("%Y-%m-%d")
            else:
                session_startD = None

            if session['finish_day'] != 'TBA':
                session_finishD = parser.parse(session['finish_day']).strftime("%Y-%m-%d")
            else:
                session_finishD = None

            if session['start_time'] != 'TBA':
                session_startT = parser.parse(session['start_time']).strftime("%H:%M")
            else:
                session_startT = None

            if session['finish_time'] != 'TBA':
                session_finishT = parser.parse(session['finish_time']).strftime("%H:%M")
            else:
                session_finishT = None

            #Inserts session data
            session_id = dbCrud.insertSession(db, section_id, session_week, session_day, session['location'], session_startD, session_finishD, session_startT, session_finishT)

    #Commits changes
    db.commit()

    #Ensures not to query endpoint too quickly if short amount of courses
    time.sleep(2)

db.close()
