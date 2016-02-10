import MySQLdb
from mycampus_parser import *
from dateutil import parser

cur_year = '2016'
cur_sem = '01'
cur_subject = 'ALSU&sel_subj=AEDT&sel_subj=ANTH&sel_subj=APBS&sel_subj=AUTE&sel_subj=BIOL&sel_subj=BUSI&sel_subj=CHEM&sel_subj=CHIN&sel_subj=COMM&sel_subj=CDPS&sel_subj=CSCI&sel_subj=ECON&sel_subj=EDUC&sel_subj=ELEE&sel_subj=ENGR&sel_subj=ENGL&sel_subj=ENVS&sel_subj=FSCI&sel_subj=FREN&sel_subj=GRMN&sel_subj=HLSC&sel_subj=HSST&sel_subj=HIST&sel_subj=INFR&sel_subj=LGLS&sel_subj=MANE&sel_subj=MITS&sel_subj=MTSC&sel_subj=MATH&sel_subj=MECE&sel_subj=MLSC&sel_subj=MCSC&sel_subj=NUCL&sel_subj=NURS&sel_subj=PHIL&sel_subj=PHY&sel_subj=POSC&sel_subj=PSYC&sel_subj=RADI&sel_subj=SCCO&sel_subj=SSCI&sel_subj=SOCI&sel_subj=SOFE&sel_subj=STAT'
term_key = {'Winter' : 1, 'Spring/Summer' : 2, 'Fall' : 3}
type_key = {'Lecture & Lab' : 1, 'Lecture' : 1, 'Thesis/Project' : 1, 'Seminar' : 1, 'Field Placement' : 1, 'Independent Study' : 1, 'Other' : 1, 'Work Term' : 1, 'Tutorial' : 2, 'Laboratory' : 3}

#Loads all of the coarse data locally
courses = parseCourses(cur_year, cur_sem, cur_subject)

#Opens DB Connection
db = MySQLdb.connect(host="localhost", user="root", passwd="Root123**", db="test")

#itterates over courses
for course in courses:
    cur = db.cursor()

    #Selects appropriate information for database
    course_subject = course['subject']
    course_code = course['code']
    course_title = course['title']
    #converts term to numerical value: Winter = 1, Summer = 2, Fall = 3
    course_term = term_key[course['term']]
    course_year = course['year']

    #Section info
    section_crn = int(course['crn'])
    #converts type to numerical value: Lecture, Lecture & Lab, other Primary Course tags = 1, Tutorial = 2, Lab = 3
    section_type = type_key[course['sessions'][0]['type']]
    section_section = course['section']

    cur.execute("INSERT IGNORE INTO Courses VALUES (%s, %s, %s, %s, %s);", (course_subject, course_code, course_title, course_term, course_year))
    cur.execute("INSERT INTO Sections VALUES (%s, %s, %s, %s, %s);", (section_crn, section_section, section_type, course_subject, course_code))

    #Session Info
    for session in course['sessions']:
        session_location = session['location']

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

        cur.execute("INSERT INTO Sessions(crn, location, day_of_week, start_date, finish_date, start_time, finish_time) VALUES (%s, %s, %s, %s, %s, %s, %s);", (section_crn, session_location, session_day,session_startD, session_finishD, session_startT, session_finishT))

    db.commit()
    cur.close()

db.close()
