import json
import re
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class JobMatcher:
    def __init__(self):
        self.sample_jobs = self._load_sample_jobs()
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def _load_sample_jobs(self) -> List[Dict]:
        """Load sample job descriptions"""
        return [
            {
                "id": 1,
                "title": "Senior Data Scientist",
                "company": "Tech Innovations Inc.",
                "description": "We're looking for a Senior Data Scientist with strong Python skills, experience with machine learning frameworks like TensorFlow or PyTorch, and expertise in data analysis. Requirements include 5+ years of experience, advanced degree in Computer Science or related field, and proficiency with SQL and big data technologies.",
                "required_skills": ["python", "machine learning", "tensorflow", "pytorch", "sql", "data analysis"],
                "preferred_skills": ["aws", "docker", "kubernetes", "spark"],
                "experience_level": "senior",
                "salary_range": "$120,000 - $160,000"
            },
            {
                "id": 2,
                "title": "Full Stack Developer",
                "company": "Web Solutions LLC",
                "description": "Join our team as a Full Stack Developer. You'll work with modern technologies including React, Node.js, Python, and cloud platforms. Ideal candidate has 3+ years of experience, strong JavaScript skills, and experience with database design and RESTful APIs.",
                "required_skills": ["javascript", "react", "node.js", "python", "sql", "rest api"],
                "preferred_skills": ["aws", "docker", "typescript", "mongodb"],
                "experience_level": "mid",
                "salary_range": "$90,000 - $120,000"
            },
            {
                "id": 3,
                "title": "Machine Learning Engineer",
                "company": "AI Pioneers Corp",
                "description": "Machine Learning Engineer needed to design and implement ML systems. Requires expertise in Python, deep learning, model deployment, and MLOps. Experience with cloud platforms and containerization is a plus.",
                "required_skills": ["python", "machine learning", "deep learning", "mlops", "docker"],
                "preferred_skills": ["kubernetes", "aws", "azure", "tensorflow", "pytorch"],
                "experience_level": "mid-senior",
                "salary_range": "$110,000 - $150,000"
            },
            {
                "id": 4,
                "title": "DevOps Engineer",
                "company": "Cloud Systems Ltd",
                "description": "DevOps Engineer to manage our cloud infrastructure. Skills needed: AWS, Docker, Kubernetes, CI/CD pipelines, Terraform, and monitoring tools. Linux administration and scripting skills required.",
                "required_skills": ["aws", "docker", "kubernetes", "ci/cd", "terraform", "linux"],
                "preferred_skills": ["python", "bash", "jenkins", "prometheus"],
                "experience_level": "mid-senior",
                "salary_range": "$100,000 - $140,000"
            },
            {
                "id": 5,
                "title": "Data Analyst",
                "company": "Business Insights Co.",
                "description": "Data Analyst position focusing on business intelligence and reporting. Required: SQL, Python, data visualization (Tableau/Power BI), statistical analysis. Experience with ETL processes and database management.",
                "required_skills": ["sql", "python", "data visualization", "tableau", "statistics"],
                "preferred_skills": ["power bi", "excel", "etl", "postgresql"],
                "experience_level": "entry-mid",
                "salary_range": "$65,000 - $85,000"
            }
        ]

    def match_resume_to_jobs(self, resume_data: Dict, top_n: int = 5) -> List[Dict]:
        """Match resume against job database"""
        resume_text = self._prepare_resume_text(resume_data)
        matches = []
        
        for job in self.sample_jobs:
            similarity_score = self._calculate_similarity(resume_text, job)
            skill_match = self._calculate_skill_match(resume_data.get('skills', {}), job['required_skills'])
            
            overall_score = (similarity_score * 0.6) + (skill_match * 0.4)
            
            matches.append({
                **job,
                'match_score': round(overall_score * 100, 1),
                'similarity_score': round(similarity_score * 100, 1),
                'skill_match_score': round(skill_match * 100, 1),
                'missing_skills': self._find_missing_skills(resume_data.get('skills', {}), job['required_skills']),
                'matching_skills': self._find_matching_skills(resume_data.get('skills', {}), job['required_skills'])
            })
        
        # Sort by match score and return top N
        return sorted(matches, key=lambda x: x['match_score'], reverse=True)[:top_n]

    def _prepare_resume_text(self, resume_data: Dict) -> str:
        """Prepare resume text for similarity analysis"""
        sections = [
            resume_data.get('raw_text', ''),
            ' '.join([str(exp) for exp in resume_data.get('experience', [])]),
            ' '.join([skill for category in resume_data.get('skills', {}).values() for skill in category])
        ]
        return ' '.join(sections)

    def _calculate_similarity(self, resume_text: str, job: Dict) -> float:
        """Calculate text similarity between resume and job description"""
        try:
            documents = [resume_text, job['description']]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0.5  # Default medium similarity

    def _calculate_skill_match(self, resume_skills: Dict, required_skills: List[str]) -> float:
        """Calculate skill matching percentage"""
        if not required_skills:
            return 0.0
            
        # Flatten resume skills
        resume_skill_list = []
        for category_skills in resume_skills.values():
            resume_skill_list.extend(category_skills)
        
        resume_skill_list = [skill.lower() for skill in resume_skill_list]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matching_skills = set(resume_skill_list) & set(required_skills_lower)
        return len(matching_skills) / len(required_skills_lower)

    def _find_missing_skills(self, resume_skills: Dict, required_skills: List[str]) -> List[str]:
        """Find skills missing from resume"""
        resume_skill_list = []
        for category_skills in resume_skills.values():
            resume_skill_list.extend(category_skills)
        
        resume_skill_list = [skill.lower() for skill in resume_skill_list]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        return list(set(required_skills_lower) - set(resume_skill_list))

    def _find_matching_skills(self, resume_skills: Dict, required_skills: List[str]) -> List[str]:
        """Find matching skills between resume and job"""
        resume_skill_list = []
        for category_skills in resume_skills.values():
            resume_skill_list.extend(category_skills)
        
        resume_skill_list = [skill.lower() for skill in resume_skill_list]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        return list(set(resume_skill_list) & set(required_skills_lower))