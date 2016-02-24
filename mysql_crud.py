
def checkAvailabilityID(db, section_id):
    cur = db.cursor()

    cur.execute("SELECT section_id FROM Section_Availability WHERE section_id = %s",
                (section_id,))
    found_id = cur.fetchone()
    cur.close()

    if found_id != None:
        return True

    return False

def checkSessionPeriodID(db, session_id):
    cur = db.cursor()

    cur.execute("SELECT session_id FROM Session_Period WHERE session_id = %s",
                (session_id,))
    found_id = cur.fetchone()
    cur.close()

    if found_id != None:
        return True

    return False

def getCourseID(db, subject, code, year, term):
    cur = db.cursor()

    cur.execute("""SELECT Courses.id FROM Courses LEFT JOIN Semesters ON semester_id = Semesters.id
                WHERE subject = %s AND code = %s AND year = %s AND term = %s""",
                (subject, code, year, term))
    course_id = cur.fetchone()
    cur.close()

    if course_id != None:
        return course_id[0]

    return 0

def getInstructorID(db, name):
    cur = db.cursor()

    cur.execute("SELECT id FROM Instructors WHERE name = %s", (name,))
    name_id = cur.fetchone()
    cur.close()

    if name_id != None:
        return name_id[0]

    return 0

def getLevelID(db, level):
    cur = db.cursor()

    cur.execute("SELECT id FROM Levels WHERE level = %s", (level,))
    level_id = cur.fetchone()
    cur.close()

    if level_id != None:
        return level_id[0]

    return 0

def getCourseLevelID(db, course_id, level_id):
    cur = db.cursor()

    cur.execute("SELECT id FROM Course_Levels WHERE course_id = %s AND level_id = %s",
                (course_id, level_id))
    course_level_id = cur.fetchone()
    cur.close()

    if course_level_id != None:
        return course_level_id[0]

    return 0

def getSectionID(db, course_id, section):
    cur = db.cursor()

    cur.execute("SELECT id FROM Sections WHERE course_id = %s AND section = %s",
                (course_id, section))
    section_id = cur.fetchone()
    cur.close()

    if section_id != None:
        return section_id[0]

    return 0

def getSectionInstructorID(db, section_id, instructor_id):
    cur = db.cursor()

    cur.execute("SELECT id FROM Section_Instructors WHERE section_id = %s AND instructor_id = %s",
                (section_id, instructor_id))
    section_instructor_id = cur.fetchone()
    cur.close()

    if section_instructor_id != None:
        return section_instructor_id[0]

    return 0

def getSemesterID(db, year, term):
    cur = db.cursor()

    cur.execute("SELECT id FROM Semesters WHERE year = %s AND term = %s",
                (year, term))
    semester_id = cur.fetchone()
    cur.close()

    if semester_id != None:
        return semester_id[0]

    return 0

def getSessionID(db, section_id, week, day = None, start_date = None, finish_date = None, start_time = None, finish_time = None):
    cur = db.cursor()

    #Creates sql query (IS for Null, =  for not null)
    cur.execute(''.join(("SELECT * FROM Sessions LEFT JOIN Session_Period ON id = session_id WHERE section_id = %s AND week = %s",
                " AND day", " = %s" if day else " IS %s", " AND start_date", " = %s" if start_date else " IS %s",
                " AND finish_date", " = %s" if finish_date else " IS %s", " AND start_time", " = %s" if start_time else " IS %s",
                " AND finish_time", " = %s" if finish_time else " IS %s")),
                (section_id, week, day, start_date, finish_date, start_time, finish_time))
    session_id = cur.fetchone()
    cur.close()

    if session_id != None:
        return session_id[0]

    return 0

def getTypeID(db, course_type):
    cur = db.cursor()

    cur.execute("SELECT id FROM Types WHERE type = %s", (course_type,))
    type_id = cur.fetchone()
    cur.close()

    if type_id != None:
        return type_id[0]

    return 0

def insertAvailability(db, section_id, capacity, actual, remaining):
    cur = db.cursor()

    #Checks if availability exists before inserting
    availability_found = checkAvailabilityID(db, section_id)

    #Inserts if doesn't exist, otherwise update availability
    if availability_found == False:
        cur.execute("INSERT INTO Section_Availability(section_id, capacity, actual, remaining) VALUES(%s, %s, %s, %s)",
                    (section_id, capacity, actual, remaining))
    else:
        cur.execute("UPDATE Section_Availability SET capacity = %s, actual = %s, remaining = %s WHERE section_id = %s",
                    (capacity, actual, remaining, section_id))

    cur.close()
    return section_id

def insertCourse(db, subject, code, title, year, term, levels):
    cur = db.cursor()

    #Checks if course exists before insertion
    course_id = getCourseID(db, subject, code, year, term)

    #Creates semster if it doesnt exist
    semester_id = getSemesterID(db, year, term)
    if semester_id == 0: semester_id = insertSemester(db, year, term)

    #Creates levels if they dont exist
    level_ids = []
    for level in levels:
        level_id = getLevelID(db, level)
        if level_id == 0: level_id = insertLevel(db, level)
        level_ids.append(level_id)

    #Inserts new course if doesn't exist, otherwise update old course
    if course_id == 0:
        cur.execute("INSERT INTO Courses(semester_id, subject, code, title) VALUES(%s, %s, %s, %s)",
                    (semester_id, subject, code, title))
        course_id = cur.lastrowid
    else:
        cur.execute("UPDATE Courses SET semester_id = %s, subject = %s, code = %s, title = %s WHERE id = %s",
                    (semester_id, subject, code, title, course_id))

    #Inserts new levels to course if they don't exist
    course_level_ids = []
    for level_id in level_ids:
        course_level_id = getCourseLevelID(db, course_id, level_id)
        if course_level_id == 0: course_level_id = insertCourseLevel(db, course_id, level_id)
        course_level_ids.append(course_level_id)

    cur.close()
    return course_id

def insertInstructor(db, name):
    cur = db.cursor()

    cur.execute("INSERT INTO Instructors(name) VALUES(%s)", (name,))
    name_id = cur.lastrowid
    cur.close()

    return name_id

def insertLevel(db, level):
    cur = db.cursor()

    cur.execute("INSERT INTO Levels(level) VALUES(%s)", (level,))
    level_id = cur.lastrowid
    cur.close()

    return level_id

def insertCourseLevel(db, course_id, level_id):
    cur = db.cursor()

    cur.execute("INSERT INTO Course_Levels(course_id, level_id) VALUES(%s, %s)",
                (course_id, level_id))
    course_level_id = cur.lastrowid
    cur.close()

    return course_level_id

def insertSection(db, course_id, course_type, section, instructors):
    cur = db.cursor()

    #Checks if section exists before insert
    section_id = getSectionID(db, course_id, section)

    #Creates types if they don't exist
    type_id = getTypeID(db, course_type)
    if type_id == 0: type_id = insertType(db, course_type)

    #Creates instructors if they don't exist
    instructor_ids = []
    for instructor in instructors:
        instructor_id = getInstructorID(db, instructor[0])
        if instructor_id == 0: instructor_id = insertInstructor(db, instructor[0])
        instructor_ids.append(instructor_id)

    #Inserts new section if doesn't exist, otherwise update old section
    if section_id == 0:
        cur.execute("INSERT INTO Sections(course_id, type_id, section) VALUES(%s, %s, %s)",
                    (course_id, type_id, section))
        section_id = cur.lastrowid
    else:
        cur.execute("UPDATE Sections SET course_id = %s, type_id = %s, section = %s WHERE id = %s",
                    (course_id, type_id, section, section_id))

    #Inserts new instructors to course if doesn't exist
    section_instructor_ids = []
    for idx, instructor_id in enumerate(instructor_ids):
        section_instructor_id = getSectionInstructorID(db, section_id, instructor_id)
        if section_instructor_id == 0: section_instructor_id = insertSectionInstructor(db, section_id, instructor_id, instructors[idx][1])
        section_instructor_ids.append(section_instructor_id)

    cur.close()
    return section_id

def insertSectionInstructor(db, section_id, instructor_id, primary_instructor):
    cur = db.cursor()

    cur.execute("INSERT INTO Section_Instructors(section_id, instructor_id, primary_instructor) VALUES(%s, %s, %s)",
                (section_id, instructor_id, primary_instructor))
    section_instructor_id = cur.lastrowid
    cur.close()

    return section_instructor_id

def insertSemester(db, year, term):
    cur = db.cursor()

    cur.execute("INSERT INTO Semesters(year, term) VALUES(%s, %s)", (year, term))
    semester_id = cur.lastrowid
    cur.close()

    return semester_id

def insertSession(db, section_id, week, day = None, location = None, start_date = None, finish_date = None, start_time = None, finish_time = None):
    cur = db.cursor()

    #Determines if session exists before insert
    session_id = getSessionID(db, section_id, week, day, start_date, finish_date, start_time, finish_time)

    #Inserts session if doesn't exist, otherwise update session
    if session_id == 0:
        cur.execute("INSERT INTO Sessions(section_id, week, day, location) VALUES(%s, %s, %s, %s)",
                    (section_id, week, day, location))
        session_id = cur.lastrowid
    else:
        cur.execute("UPDATE Sessions SET section_id = %s, week = %s, day = %s, location = %s WHERE id = %s",
                    (section_id, week, day, location, session_id))

    #Inserts new time period
    insertSessionPeriod(db, session_id, start_date, finish_date, start_time, finish_time)

    cur.close()
    return session_id

def insertSessionPeriod(db, session_id, start_date = None, finish_date = None, start_time = None, finish_time = None):
    cur = db.cursor()

    #Determines if period already exists
    period_found = checkSessionPeriodID(db, session_id)

    #Inserts new entry if doesn't exist or updates old
    if period_found == False:
        cur.execute("INSERT INTO Session_Period(session_id, start_date, finish_date, start_time, finish_time) VALUES(%s, %s, %s, %s, %s)",
                    (session_id, start_date, finish_date, start_time, finish_time))
    else:
        cur.execute("UPDATE Session_Period SET start_date = %s, finish_date = %s, start_time = %s, finish_time = %s WHERE session_id = %s",
                    (start_date, finish_date, start_time, finish_time, session_id))

    cur.close()
    return session_id

def insertType(db, course_type):
    cur = db.cursor()

    cur.execute("INSERT INTO Types(type) VALUES(%s)", (course_type,))
    type_id = cur.lastrowid
    cur.close()

    return type_id
