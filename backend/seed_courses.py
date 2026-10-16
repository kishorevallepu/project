from database import get_db_connection, get_db_backend


COURSES = [
    ("R", "Realistic", "You prefer practical and hands-on activities.", "Mechanical Engineering", "fa-gears", "Degree", "4 Years", "Learn mechanical systems, machines, manufacturing and engineering design."),
    ("R", "Realistic", "You prefer practical and hands-on activities.", "Automobile Engineering", "fa-car", "Degree / Diploma", "2-4 Years", "Study vehicle design, automobile systems and automotive technology."),
    ("R", "Realistic", "You prefer practical and hands-on activities.", "Electrical Engineering", "fa-bolt", "Degree / Diploma", "2-4 Years", "Learn electrical systems, circuits, power systems and electronics."),
    ("R", "Realistic", "You prefer practical and hands-on activities.", "Civil Engineering", "fa-building", "Degree", "4 Years", "Study construction, structures, infrastructure and civil engineering."),
    ("I", "Investigative", "You enjoy research, analysis, science and solving complex problems.", "Data Science", "fa-chart-line", "Degree / Certification", "6 Months - 4 Years", "Learn data analysis, statistics, Python, machine learning and visualization."),
    ("I", "Investigative", "You enjoy research, analysis, science and solving complex problems.", "Artificial Intelligence", "fa-brain", "Degree / Certification", "6 Months - 4 Years", "Learn machine learning, neural networks and AI applications."),
    ("I", "Investigative", "You enjoy research, analysis, science and solving complex problems.", "Computer Science", "fa-laptop-code", "Degree", "4 Years", "Study programming, algorithms, databases, software and computer systems."),
    ("I", "Investigative", "You enjoy research, analysis, science and solving complex problems.", "Research & Analytics", "fa-flask", "Certification", "3-12 Months", "Develop analytical, research and problem-solving skills."),
    ("A", "Artistic", "You enjoy creativity, design, self-expression and innovative activities.", "Graphic Design", "fa-pen-nib", "Certification", "3-12 Months", "Learn visual communication, branding, typography and digital design."),
    ("A", "Artistic", "You enjoy creativity, design, self-expression and innovative activities.", "UI/UX Design", "fa-object-group", "Certification", "3-12 Months", "Learn user interface and user experience design for digital products."),
    ("A", "Artistic", "You enjoy creativity, design, self-expression and innovative activities.", "Animation", "fa-film", "Certification / Degree", "1-4 Years", "Learn 2D, 3D animation, visual effects and digital storytelling."),
    ("A", "Artistic", "You enjoy creativity, design, self-expression and innovative activities.", "Digital Media", "fa-camera", "Certification", "3-12 Months", "Learn photography, video editing and digital content creation."),
    ("S", "Social", "You enjoy helping, teaching and communicating with people.", "Education & Teaching", "fa-chalkboard-user", "Degree / Certification", "1-4 Years", "Develop teaching, communication and classroom management skills."),
    ("S", "Social", "You enjoy helping, teaching and communicating with people.", "Psychology", "fa-comments", "Degree", "3-4 Years", "Study human behavior, psychology and mental processes."),
    ("S", "Social", "You enjoy helping, teaching and communicating with people.", "Human Resources", "fa-users", "Degree / Certification", "1-2 Years", "Learn recruitment, employee management and organizational behavior."),
    ("S", "Social", "You enjoy helping, teaching and communicating with people.", "Social Work", "fa-hand-holding-heart", "Degree", "3-4 Years", "Learn how to support individuals, communities and social development."),
    ("E", "Enterprising", "You enjoy leadership, business, persuasion and decision-making.", "Business Management", "fa-briefcase", "Degree", "3-4 Years", "Learn business operations, management and organizational strategy."),
    ("E", "Enterprising", "You enjoy leadership, business, persuasion and decision-making.", "Marketing", "fa-bullhorn", "Degree / Certification", "3-12 Months", "Learn digital marketing, branding, advertising and customer behavior."),
    ("E", "Enterprising", "You enjoy leadership, business, persuasion and decision-making.", "Entrepreneurship", "fa-lightbulb", "Certification / Degree", "3-12 Months", "Learn business planning, startup development and entrepreneurship."),
    ("E", "Enterprising", "You enjoy leadership, business, persuasion and decision-making.", "Finance & Banking", "fa-building-columns", "Degree / Certification", "1-4 Years", "Learn finance, banking, investment and financial management."),
    ("C", "Conventional", "You prefer organized work involving information, numbers and structured procedures.", "Accounting", "fa-calculator", "Degree / Certification", "1-4 Years", "Learn accounting principles, financial records and taxation."),
    ("C", "Conventional", "You prefer organized work involving information, numbers and structured procedures.", "Banking & Finance", "fa-building-columns", "Degree / Certification", "1-4 Years", "Study banking operations, finance and financial services."),
    ("C", "Conventional", "You prefer organized work involving information, numbers and structured procedures.", "Business Administration", "fa-briefcase", "Degree", "3-4 Years", "Learn administration, management, business operations and organization."),
    ("C", "Conventional", "You prefer organized work involving information, numbers and structured procedures.", "Data Management", "fa-database", "Certification", "3-12 Months", "Learn databases, data organization and information management."),
]


def seed_courses():

    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Could not connect to the career_guidance database")

    cursor = None

    try:

        cursor = connection.cursor()
        rows = [course + (order,) for order, course in enumerate(COURSES, start=1)]

        if get_db_backend() == "sqlite":
            cursor.executemany(
                """
                INSERT INTO course_catalog
                    (riasec_type, category_name, category_description, name,
                     icon, level, duration, description, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(riasec_type, name)
                DO UPDATE SET
                    category_name = excluded.category_name,
                    category_description = excluded.category_description,
                    icon = excluded.icon,
                    level = excluded.level,
                    duration = excluded.duration,
                    description = excluded.description,
                    display_order = excluded.display_order
                """,
                rows
            )
        else:
            cursor.executemany(
                """
                INSERT INTO course_catalog
                    (riasec_type, category_name, category_description, name,
                     icon, level, duration, description, display_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    category_name = VALUES(category_name),
                    category_description = VALUES(category_description),
                    icon = VALUES(icon),
                    level = VALUES(level),
                    duration = VALUES(duration),
                    description = VALUES(description),
                    display_order = VALUES(display_order)
                """,
                rows
            )
        connection.commit()
        print(f"Seeded {len(COURSES)} courses.")

    except Exception:

        connection.rollback()
        raise

    finally:

        if cursor:
            cursor.close()

        connection.close()


if __name__ == "__main__":
    seed_courses()
