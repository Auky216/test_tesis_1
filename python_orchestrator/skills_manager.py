import os
import glob

def load_skills() -> str:
    skills_content = []
    skills_dir = "skills"
    
    if os.path.exists(skills_dir):
        skill_files = glob.glob(os.path.join(skills_dir, "*.SKILL.md"))
        for file in skill_files:
            with open(file, "r") as f:
                skills_content.append(f.read())
                
    return "\n".join(skills_content)
