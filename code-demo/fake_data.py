from faker import Faker
import random

fake = Faker()

def seed_data(
        db, Project, User,
    num_users=50,
    num_projects=20,
    min_projects_per_user=1,
    max_projects_per_user=5,
):
    users = []
    projects = []

    # Create projects
    for _ in range(num_projects):
        project = Project(
            name=fake.bs().title(),
            is_active=random.choice([True, True, True, False]),
        )
        projects.append(project)

    db.session.add_all(projects)
    db.session.flush()  # get project IDs

    # Create users and assign projects
    for _ in range(num_users):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
        )

        assigned_projects = random.sample(
            projects,
            random.randint(min_projects_per_user, max_projects_per_user),
        )

        user.projects.extend(assigned_projects)
        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print(f"Seeded {num_users} users and {num_projects} projects.")
