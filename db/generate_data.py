from faker import Faker 

fake = Faker()

STUDENTS = 100000
COURSES = 200
LECTURERS = 40
ADMINS = 10
BATCH_SIZE = 1000  # Number of rows per batch insert

student_ids = []
lecturer_ids = []
admin_ids = []
course_codes = []
# =========================
# FIXED TEST DATA
# =========================

TEST_STUDENT_ID = 888888
TEST_LECTURER_ID = 777777
TEST_ADMIN_ID = 999999

TEST_COURSE_CODE = "MATH0010"
TEST_COURSE_NAME = "Pre-Calculus"

departments = ["Computing", "Chemistry", "Physics", "Mathematics", "Biology"]

levels = [
    "Introduction to",
    "Advanced",
    "Fundamentals of",
    "Principles of",
    "Applied",
    "Intermediate",
    "Experimental",
    "Theoretical",
    "Modern",
    "Practical",
    "Computational",
    "Classical",
    "Research Methods in", 
    "Special Topics in"
]
subjects = {
    "Algorithms": "CS",
    "Data Structures": "CS",
    "Organic Chemistry": "CHEM",
    "Quantum Mechanics": "PHYS",
    "Linear Algebra": "MATH",
    "Thermodynamics": "PHYS",
    "Statistics": "MATH",
    "Operating Systems": "CS",
    "Calculus": "MATH",
    "Fluid Dynamics": "PHYS",
    "Physical Chemistry": "CHEM",
    "Molecular Biology": "BIO",
    "Genetics": "BIO",
    "Cell Biology": "BIO",
    "Chemical Analysis": "CHEM",
}


def batch_inserts(file, table_name, columns, values_list):
    if not values_list:
        return
    
    for i in range(0, len(values_list), BATCH_SIZE):
        batch = values_list[i:i + BATCH_SIZE]
        file.write(f"INSERT INTO {table_name} ({columns}) VALUES\n")
        for j, values in enumerate(batch):
            if j < len(batch) - 1:
                file.write(f"{values},\n")
            else:
                file.write(f"{values};\n")
        file.write("\n")


with open('db/data.sql', 'w') as file:    
    users = []

    # =========================
    # FIXED USERS FOR POSTMAN
    # =========================

    users.append((
        TEST_STUDENT_ID,
        'password@123',
        'Beres',
        'Hammond',
        'Student'
    ))
    student_ids.append(TEST_STUDENT_ID)

    users.append((
        TEST_LECTURER_ID,
        'exp3ctop@troNum',
        'Professor',
        'Snape',
        'Lecturer'
    ))
    lecturer_ids.append(TEST_LECTURER_ID)

    users.append((
        TEST_ADMIN_ID,
        'admin123',
        'Violet',
        'Bridgerton',
        'Admin'
    ))
    admin_ids.append(TEST_ADMIN_ID)
    
    # Generate Student Users
    for student in range(1, STUDENTS + 1):
        while True:
            sid = fake.unique.random_number(digits=6, fix_len=True)
            if sid not in [TEST_STUDENT_ID, TEST_LECTURER_ID, TEST_ADMIN_ID]:
                break
        student_ids.append(sid)
        fname = fake.first_name().replace("'", "''")  
        lname = fake.last_name().replace("'", "''")  
        pwd = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True).replace("'", "''")
        users.append((sid, pwd, fname, lname, 'Student'))

    # Generate Lecturer Users
    for lecturer in range(1, LECTURERS + 1):
        while True:
            lid = fake.unique.random_number(digits=6, fix_len=True)
            if lid not in [TEST_STUDENT_ID, TEST_LECTURER_ID, TEST_ADMIN_ID]:
                break
        lecturer_ids.append(lid)
        fname = fake.first_name().replace("'", "''")  
        lname = fake.last_name().replace("'", "''") 
        pwd = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True).replace("'", "''")
        users.append((lid, pwd, fname, lname, 'Lecturer'))

    # Generate Admin Users
    for admin in range(1, ADMINS + 1):
        while True:
            aid = fake.unique.random_number(digits=6, fix_len=True)
            if aid not in [TEST_STUDENT_ID, TEST_LECTURER_ID, TEST_ADMIN_ID]:
                break
        admin_ids.append(aid)
        fname = fake.first_name().replace("'", "''")  
        lname = fake.last_name().replace("'", "''") 
        pwd = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True).replace("'", "''")
        users.append((aid, pwd, fname, lname, 'Admin'))

    # Batch insert users
    file.write("-- Insert Users\n")
    user_values = [f"({uid}, '{pwd}', '{fname}', '{lname}', '{role}')" 
                   for uid, pwd, fname, lname, role in users]
    batch_inserts(file, "User", "userID, password, firstName, lastName, role", user_values)

    # Batch insert students
    file.write("-- Insert Students\n")
    student_values = [f"({sid})" for sid in student_ids]
    batch_inserts(file, "Student", "studentID", student_values)

    # Batch insert lecturers
    file.write("-- Insert Lecturers\n")
    lecturer_values = [f"({lid}, '{fake.random_element(elements=departments)}')" 
                       for lid in lecturer_ids]
    batch_inserts(file, "Lecturer", "lecturerID, department", lecturer_values)

    # Batch insert admins
    file.write("-- Insert Admins\n")
    admin_values = [f"({aid})" for aid in admin_ids]
    batch_inserts(file, "Admin", "adminID", admin_values)

    file.write("-- Insert Courses\n")
    course_names  = [f"{level} {subject}" for level in levels for subject in subjects]
    fake.random.shuffle(course_names)  
    
    course_values = []
    # Fixed course for testing
    course_codes.append(TEST_COURSE_CODE)

    course_values.append(
        f"('{TEST_COURSE_CODE}', '{TEST_COURSE_NAME}')"
    )
    
    for course in range(1, COURSES + 1):
        course_num = fake.unique.random_int(min=1000, max=3999)
        
        course_name = course_names[course - 1]
        course_code = None
        for subj, pref in subjects.items():
            if course_name.endswith(subj):
                course_code = f"{pref}{course_num}"
                break
        # Fallback if no subject match found (shouldn't happen with current data)
        if course_code is None:
            course_code = f"GEN{course_num}"

        course_codes.append(course_code)
        course_values.append(f"('{course_code}', '{course_name}')")
    
    # Batch insert courses
    batch_inserts(file, "Course", "courseCode, courseName", course_values)

    file.write("-- Insert Enrollments\n")

    enrollments = set()
    # Fixed enrollment
    enrollments.add((TEST_STUDENT_ID, TEST_COURSE_CODE))
    student_course_count = {sid: 0 for sid in student_ids}

    # Each student has 3-6 courses 
    for num in range(1, STUDENTS + 1):
        enrolled = fake.random_elements(elements=course_codes, unique=True, length=fake.random_int(min=3, max=6))
        student = student_ids[num - 1]
        for course in enrolled:
            enrollments.add((student, course))
            student_course_count[student] += 1
    
    # At least 10 students are enrolled in each course
    for code in course_codes:
        selected_students = fake.random_elements(elements=student_ids, unique=True, length=10)
        for student in selected_students:
            if (student, code) not in enrollments and student_course_count[student] < 6:
                enrollments.add((student, code))
                student_course_count[student] += 1

    # Batch insert enrollments
    enrollments = list(enrollments)
    fake.random.shuffle(enrollments)
    enrollment_values = [f"({student}, '{course}')" for student, course in enrollments]
    batch_inserts(file, "Enroll", "studentID, courseCode", enrollment_values)

    file.write("-- Insert Creates\n")

    creates = []
    # Fixed admin creates course
    creates.append((TEST_ADMIN_ID, TEST_COURSE_CODE))

    # assign each course to a random admin
    for code in course_codes:
        admin = fake.random_element(elements=admin_ids)
        creates.append((admin, code))

    create_values = [f"({admin}, '{code}')" for admin, code in creates]
    batch_inserts(file, "Creates", "adminID, courseCode", create_values)

    file.write("-- Insert Teaches\n")

    teaches = set()
    lecturer_course_count = {lid: 0 for lid in lecturer_ids}
    assigned_courses = set()

    # Fixed lecturer assignment
    teaches.add((TEST_LECTURER_ID, TEST_COURSE_CODE))
    assigned_courses.add(TEST_COURSE_CODE)
    lecturer_course_count[TEST_LECTURER_ID] = 1

    # Assign each lecturer at least one course
    available_courses = [code for code in course_codes if code not in assigned_courses]
    course_index = 0

    for lecturer_id in lecturer_ids:
        if lecturer_id == TEST_LECTURER_ID: # Skip fixed lecturer already assigned
            continue

        if course_index >= len(available_courses):
            break

        code = available_courses[course_index]

        teaches.add((lecturer_id, code))
        assigned_courses.add(code)
        lecturer_course_count[lecturer_id] += 1
        course_index += 1

    # Assign remaining courses, ensuring no lecturer exceeds 5 courses
    remaining_courses = [code for code in course_codes if code not in assigned_courses]

    for code in remaining_courses:
        available_lecturers = [lid for lid in lecturer_ids if lecturer_course_count[lid] < 5]
        if not available_lecturers:
            break

        lecturer_id = fake.random_element(elements=available_lecturers)
        teaches.add((lecturer_id, code))
        lecturer_course_count[lecturer_id] += 1
        assigned_courses.add(code)

    # Batch insert teaching assignments
    teaches = list(teaches)
    fake.random.shuffle(teaches)
    teach_values = [f"({lecturer_id}, '{code}')" for lecturer_id, code in teaches]
    batch_inserts(file, "Teaches", "lecturerID, courseCode", teach_values)
    
    # (SECTIONS, CONTENT, FORUMS, CALENDAR) for testing
    file.write("-- Insert Course Sections\n")
    section_values = []
    # Setup sections across all courses tracking auto-increment values implicitly (1 to COURSES * 2)
    sec_id_counter = 1
    course_sections_map = {}
    
    for code in course_codes:
        course_sections_map[code] = []
        for week in range(1, 3):
            section_values.append(f"(NULL, '{code}', 'Week {week} Overview')")
            course_sections_map[code].append(sec_id_counter)
            sec_id_counter += 1
    batch_inserts(file, "Section", "secID, courseCode, secName", section_values)

    file.write("-- Insert Course Content\n")
    content_values = []
    for code, sec_ids in course_sections_map.items():
        for s_id in sec_ids:
            content_values.append(f"(NULL, {s_id}, 'Lecture Slides', 'slide', 'https://university.edu/slides/week1.pdf')")
            content_values.append(f"(NULL, {s_id}, 'Readings Resource Link', 'link', 'http://example.com/readings')")
    batch_inserts(file, "CourseContent", "contentID, secID, contentName, type, content", content_values)

    file.write("-- Insert Forums\n")
    forum_values = []
    forum_id_counter = 1
    course_forum_map = {}
    
    for code in course_codes:
        forum_values.append(f"(NULL, '{code}', 'General Discussion Forum')")
        course_forum_map[code] = forum_id_counter
        forum_id_counter += 1
    batch_inserts(file, "Forum", "forumID, courseCode, forumName", forum_values)

    file.write("-- Insert Discussion Threads & Tree Replies (Reddit-style)\n")
    thread_values = []
    reply_relationship_values = []
    
    thread_id_counter = 1
    for code, f_id in course_forum_map.items():
        # Parent original thread post
        thread_values.append(f"(NULL, {f_id}, 'Welcome Thread', 'Please introduce yourselves here!')")
        parent_id = thread_id_counter
        thread_id_counter += 1
        
        # Child Reply (Level 1)
        thread_values.append(f"(NULL, {f_id}, 'Reply', 'Hi instructor, excited to be here.')")
        child_l1_id = thread_id_counter
        thread_id_counter += 1
        reply_relationship_values.append(f"({parent_id}, {child_l1_id})")
        
        # Nested Sub-Reply (Level 2 -> Child of Child)
        thread_values.append(f"(NULL, {f_id}, 'Reply', 'Welcome to the class mate!')")
        child_l2_id = thread_id_counter
        thread_id_counter += 1
        reply_relationship_values.append(f"({child_l1_id}, {child_l2_id})")
        
    batch_inserts(file, "Thread", "threadID, forumID, threadTitle, content", thread_values)
    batch_inserts(file, "Reply", "parentThreadID, childThreadID", reply_relationship_values)

    # CALENDAR, ASSIGNMENTS, SUBMISSIONS & GRADES
    file.write("-- Insert Calendar Events\n")
    event_values = []
    event_id_counter = 1
    course_event_map = {}
    
    for code in course_codes:
        event_values.append(f"(NULL, '{code}', 'Course Assignment 1', '2026-05-01', '2026-06-01')")
        course_event_map[code] = event_id_counter
        event_id_counter += 1
    batch_inserts(file, "CalendarEvent", "eventID, courseCode, eventName, createdDate, dueDate", event_values)

    file.write("-- Insert Assignments\n")
    assignment_values = []
    for code, ev_id in course_event_map.items():
        # Setup initial weight/points baseline mapping to calendar references
        assignment_values.append(f"({ev_id}, 100)")
    batch_inserts(file, "Assignment", "assignmentID, maxGrade", assignment_values)

    file.write("-- Insert Student Homework Submissions\n")
    submission_values = []
    for student, course in enrollments:
        # Check if course has a matching assigned event ID
        if course in course_event_map:
            ev_id = course_event_map[course]
            submission_values.append(f"({student}, {ev_id}, '/uploads/submissions/{student}_assignment.pdf')")
    batch_inserts(file, "Submission", "studentID, assignmentID, filePath", submission_values)

    file.write("-- Insert Lecturer Grades\n")
    grade_values = []

    course_lecturer_map = {}
    for lecturer_id, course in teaches:
        course_lecturer_map[course] = lecturer_id

    for student, course in enrollments:
        if course in course_event_map and course in course_lecturer_map:
            ev_id = course_event_map[course]
            lecturer_id = course_lecturer_map[course]

            random_grade = fake.random_int(min=50, max=100)

            grade_values.append(
                f"({lecturer_id}, {student}, {ev_id}, {random_grade})"
            )

    batch_inserts(file, "Grade", "lecturerID, studentID, assignmentID, score", grade_values)

    # Print summary
    print("Data generation complete. Check data.sql")
    print(f"Generated:")
    print(f"  - {STUDENTS:,} students")
    print(f"  - {LECTURERS} lecturers")
    print(f"  - {ADMINS} admins")
    print(f"  - {COURSES} courses")
    print(f"  - Enrollments: ~{len(enrollment_values):,}")
    print(f"  - Teaching assignments: {len(teach_values)}")

    print("\n==============================")
    print("FIXED POSTMAN TEST DATA")

    print("\n--- STUDENT LOGIN ---")
    print("ID       : 888888")
    print("Password : password@123")

    print("\n--- LECTURER LOGIN ---")
    print("ID       : 777777")
    print("Password : exp3ctop@troNum")

    print("\n--- ADMIN LOGIN ---")
    print("ID       : 999999")
    print("Password : admin123")

    print("\n--- FIXED COURSE ---")
    print("Course Code : MATH0010")
    print("Course Name : Pre-Calculus")
