SKILLS = [
    "python", "java", "c++", "sql", "machine learning",
    "data analysis", "deep learning", "nlp", "tensorflow",
    "pandas", "numpy", "react", "node", "mongodb"
]

def extract_skills(text):
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return found_skills
