from app import app, db, Student, Course, Enrollment
import random

def seed_data():
    db.drop_all()
    db.create_all()

    # --- Create Students ---
    students = [
        Student(id=1),
        Student(id=2),
        Student(id=3),
        Student(id=4),
    ]

    # --- Create Courses ---
    courses = [
        Course(id=101),
        Course(id=102),
        Course(id=103),
    ]

    db.session.add_all(students + courses)
    db.session.commit()

    # --- Possible grades ---
    grades = ["A", "A-", "B+", "B", "C", "F", None]

    # --- Create Enrollments ---
    enrollments = []
    for student in students:
        # each student takes 1–3 courses
        enrolled_courses = random.sample(courses, random.randint(1, 3))
        for course in enrolled_courses:
            e = Enrollment(
                grade=random.choice(grades),
                student_id=student.id,
                course_id=course.id
            )
            enrollments.append(e)

    db.session.add_all(enrollments)
    db.session.commit()

    print("Fake data inserted successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
