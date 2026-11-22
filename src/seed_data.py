"""Sample data for the Skill Gap system (skills taxonomy, job roles, courses, demo students).
Real project me isko apne dataset (O*NET / job postings) se replace/extend karo."""

SKILLS = {
    # name: category
    "Python": "Programming", "Java": "Programming", "JavaScript": "Programming",
    "SQL": "Data", "Excel": "Data", "Statistics": "Data", "Pandas": "Data",
    "NumPy": "Data", "Data Visualization": "Data", "Power BI": "Data", "Tableau": "Data",
    "Machine Learning": "AI/ML", "Deep Learning": "AI/ML", "NLP": "AI/ML",
    "Scikit-learn": "AI/ML", "TensorFlow": "AI/ML", "MLOps": "AI/ML",
    "Data Structures": "CS Fundamentals", "Algorithms": "CS Fundamentals",
    "Git": "Tools", "Docker": "Tools", "Linux": "Tools", "CI/CD": "Tools",
    "REST APIs": "Web", "Flask": "Web", "Django": "Web", "HTML/CSS": "Web", "React": "Web",
    "Node.js": "Web", "AWS": "Cloud", "Kubernetes": "Cloud",
    "Communication": "Soft Skills", "Problem Solving": "Soft Skills",
}

# Alternate spellings used in resumes -> canonical skill name
ALIASES = {
    "js": "JavaScript", "sklearn": "Scikit-learn", "scikit learn": "Scikit-learn",
    "ml": "Machine Learning", "dl": "Deep Learning", "powerbi": "Power BI",
    "power-bi": "Power BI", "html": "HTML/CSS", "css": "HTML/CSS", "postgres": "SQL",
    "postgresql": "SQL", "mysql": "SQL", "sqlite": "SQL", "ms excel": "Excel",
    "nodejs": "Node.js", "node": "Node.js", "rest": "REST APIs", "rest api": "REST APIs",
    "restful": "REST APIs", "dsa": "Data Structures", "tf": "TensorFlow",
    "k8s": "Kubernetes", "ci cd": "CI/CD", "matplotlib": "Data Visualization",
    "seaborn": "Data Visualization", "natural language processing": "NLP",
    "problem-solving": "Problem Solving", "github": "Git",
}

# role -> {"industry": ..., "skills": {skill: (required_level 1-5, importance 0-1)}}
ROLES = {
    "Data Analyst": {"industry": "Analytics", "skills": {
        "SQL": (4, 1.0), "Excel": (4, 0.8), "Python": (3, 0.8), "Statistics": (3, 0.8),
        "Data Visualization": (4, 0.9), "Power BI": (3, 0.6), "Pandas": (3, 0.6),
        "Communication": (3, 0.5)}},
    "Data Scientist": {"industry": "Analytics/AI", "skills": {
        "Python": (4, 1.0), "Statistics": (4, 0.9), "Machine Learning": (4, 1.0),
        "Pandas": (4, 0.8), "NumPy": (3, 0.6), "Scikit-learn": (4, 0.8), "SQL": (3, 0.7),
        "Data Visualization": (3, 0.6), "Deep Learning": (3, 0.5)}},
    "ML Engineer": {"industry": "AI", "skills": {
        "Python": (4, 1.0), "Machine Learning": (4, 1.0), "Deep Learning": (4, 0.8),
        "TensorFlow": (3, 0.7), "Docker": (3, 0.7), "MLOps": (3, 0.8), "Git": (3, 0.6),
        "REST APIs": (3, 0.6), "AWS": (3, 0.5), "Algorithms": (3, 0.5)}},
    "Backend Developer": {"industry": "Software", "skills": {
        "Python": (4, 0.9), "Java": (3, 0.5), "SQL": (4, 0.9), "REST APIs": (4, 1.0),
        "Flask": (3, 0.6), "Django": (3, 0.6), "Git": (4, 0.7), "Docker": (3, 0.6),
        "Data Structures": (4, 0.8), "Algorithms": (3, 0.6), "Linux": (3, 0.5)}},
    "Frontend Developer": {"industry": "Software", "skills": {
        "HTML/CSS": (4, 1.0), "JavaScript": (4, 1.0), "React": (4, 0.9), "Git": (3, 0.6),
        "REST APIs": (3, 0.6), "Problem Solving": (3, 0.5), "Communication": (3, 0.4)}},
    "DevOps Engineer": {"industry": "Cloud/Infra", "skills": {
        "Linux": (4, 1.0), "Docker": (4, 1.0), "Kubernetes": (3, 0.8), "CI/CD": (4, 0.9),
        "AWS": (4, 0.9), "Git": (4, 0.7), "Python": (3, 0.6)}},
}

# (course name, provider, hours, [skills covered])
COURSES = [
    ("SQL for Data Analysis", "Udacity", 20, ["SQL"]),
    ("Advanced SQL Bootcamp", "Udemy", 30, ["SQL"]),
    ("Excel for Analysts", "Coursera", 15, ["Excel"]),
    ("Python for Everybody", "Coursera", 30, ["Python"]),
    ("Python for Data Science", "NPTEL", 40, ["Python", "Pandas", "NumPy"]),
    ("Statistics Fundamentals", "Khan Academy", 25, ["Statistics"]),
    ("Data Visualization with Matplotlib & Seaborn", "Coursera", 12, ["Data Visualization"]),
    ("Power BI Essentials", "Microsoft Learn", 10, ["Power BI"]),
    ("Tableau Basics", "Tableau eLearning", 8, ["Tableau", "Data Visualization"]),
    ("Machine Learning Specialization", "Coursera", 60, ["Machine Learning", "Scikit-learn"]),
    ("Deep Learning Specialization", "Coursera", 80, ["Deep Learning", "TensorFlow"]),
    ("NLP with Transformers", "Hugging Face", 25, ["NLP"]),
    ("MLOps Fundamentals", "DeepLearning.AI", 30, ["MLOps"]),
    ("Pandas Mastery", "Kaggle Learn", 6, ["Pandas"]),
    ("Data Structures & Algorithms in Python", "GeeksforGeeks", 50, ["Data Structures", "Algorithms"]),
    ("Git & GitHub Crash Course", "freeCodeCamp", 5, ["Git"]),
    ("Docker for Beginners", "Docker Docs", 8, ["Docker"]),
    ("Kubernetes Basics", "Linux Foundation", 20, ["Kubernetes"]),
    ("Linux Command Line Bootcamp", "Udemy", 15, ["Linux"]),
    ("CI/CD with GitHub Actions", "GitHub Learn", 8, ["CI/CD"]),
    ("Building REST APIs with Flask", "Udemy", 18, ["REST APIs", "Flask"]),
    ("Django for Beginners", "freeCodeCamp", 20, ["Django"]),
    ("HTML & CSS Complete Guide", "freeCodeCamp", 20, ["HTML/CSS"]),
    ("Modern JavaScript", "freeCodeCamp", 30, ["JavaScript"]),
    ("React - The Complete Guide", "Udemy", 40, ["React"]),
    ("Node.js Backend Development", "Udemy", 25, ["Node.js"]),
    ("Java Programming Masterclass", "Udemy", 50, ["Java"]),
    ("AWS Cloud Practitioner", "AWS Skill Builder", 20, ["AWS"]),
    ("Communication Skills for Professionals", "LinkedIn Learning", 6, ["Communication"]),
    ("Problem Solving with Coding Challenges", "LeetCode", 40, ["Problem Solving", "Algorithms"]),
]

# demo students: (name, degree, year, {skill: level})
STUDENTS = [
    ("Aarav Shah", "B.Tech CSE", 3, {"Python": 3, "SQL": 2, "HTML/CSS": 3, "Java": 3, "Data Structures": 3, "Git": 2}),
    ("Diya Patel", "B.Sc IT", 2, {"HTML/CSS": 4, "JavaScript": 3, "Git": 2, "Communication": 3}),
    ("Rohan Mehta", "B.Tech IT", 4, {"Python": 4, "Statistics": 3, "Pandas": 3, "SQL": 3, "Machine Learning": 2}),
    ("Isha Desai", "BCA", 3, {"Excel": 4, "SQL": 3, "Power BI": 2, "Communication": 4}),
    ("Karan Joshi", "B.Tech CSE", 4, {"Linux": 3, "Docker": 2, "Python": 3, "Git": 3, "AWS": 2}),
]
