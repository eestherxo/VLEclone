from faker import Faker 

fake = Faker()

STUDENTS = 100000
COURSES = 200
LECTURERS = 40
BATCH_SIZE = 1000  # Number of rows per batch insert

student_ids = []
lecturer_ids = []
course_codes = []

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


with open('data.sql', 'w') as file:    
    users = []
    
    # Generate Student Users
    for student in range(1, STUDENTS + 1):
        sid = fake.unique.random_number(digits=6, fix_len=True)
        student_ids.append(sid)
        fname = fake.first_name().replace("'", "''")  
        lname = fake.last_name().replace("'", "''")  
        pwd = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True).replace("'", "''")
        users.append((sid, pwd, fname, lname, 'Student'))

    # Generate Lecturer Users
    for lecturer in range(1, LECTURERS + 1):
        lid = fake.unique.random_number(digits=6, fix_len=True)
        lecturer_ids.append(lid)
        fname = fake.first_name().replace("'", "''")  
        lname = fake.last_name().replace("'", "''") 
        pwd = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True).replace("'", "''")
        users.append((lid, pwd, fname, lname, 'Lecturer'))

 
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

    file.write("-- Insert Courses\n")
    course_names  = [f"{level} {subject}" for level in levels for subject in subjects]
    fake.random.shuffle(course_names)  
    
    course_values = []
    for course in range(1, COURSES + 1):
        course_num = fake.unique.random_int(min=1000, max=3999)
        
        course_name = course_names[course - 1]
        for subj, pref in subjects.items():
            if course_name.endswith(subj):
                course_code = f"{pref}{course_num}"
                course_codes.append(course_code)
                break
        course_values.append(f"('{course_code}', '{course_name}')")
    
    # Batch insert courses
    batch_inserts(file, "Course", "courseCode, courseName", course_values)

    file.write("-- Insert Enrollments\n")

    enrollments = set()
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

    file.write("-- Insert Teaches\n")

    teaches = set()
    lecturer_course_count = {lid: 0 for lid in lecturer_ids}

    # Assign each lecturer at least one course
    for i, lecturer_id in enumerate(lecturer_ids):
        code = course_codes[i]
        teaches.add((lecturer_id, code))
        lecturer_course_count[lecturer_id] += 1

    # Assign remaining courses, ensuring no lecturer exceeds 5 courses
    for code in course_codes[LECTURERS:]:
        available_lecturers = [lid for lid in lecturer_ids if lecturer_course_count[lid] < 5]
        if available_lecturers:
            lecturer_id = fake.random_element(elements=available_lecturers)
            teaches.add((lecturer_id, code))
            lecturer_course_count[lecturer_id] += 1

    # Batch insert teaching assignments
    teaches = list(teaches)
    fake.random.shuffle(teaches)
    teach_values = [f"({lecturer_id}, '{code}')" for lecturer_id, code in teaches]
    batch_inserts(file, "Teaches", "lecturerID, courseCode", teach_values)
    
    # Print summary
    print("Data generation complete. Check data.sql")
    print(f"Generated:")
    print(f"  - {STUDENTS:,} students")
    print(f"  - {LECTURERS} lecturers")
    print(f"  - {COURSES} courses")
    print(f"  - Enrollments: ~{len(enrollment_values):,}")
    print(f"  - Teaching assignments: {len(teach_values)}")
