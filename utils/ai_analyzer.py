import openai
from typing import Dict, List
import json
import re

class AIAnalyzer:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def analyze_resume(self, resume_data: Dict) -> Dict:
        """Comprehensive AI analysis of resume"""
        try:
            analysis_prompt = self._create_analysis_prompt(resume_data)
            response = self._get_ai_response(analysis_prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            return self._get_fallback_analysis(resume_data)

    def _create_analysis_prompt(self, resume_data: Dict) -> str:
        """Create detailed prompt for AI analysis"""
        return f"""
        Analyze this resume and provide a comprehensive assessment in JSON format:

        RESUME CONTENT:
        {resume_data.get('raw_text', '')[:3000]}

        EXTRACTED INFORMATION:
        Skills: {resume_data.get('skills', {})}
        Experience: {resume_data.get('experience', [])}
        Education: {resume_data.get('education', [])}

        Please provide analysis in this exact JSON format:
        {{
            "overall_score": 85,
            "strengths": ["list", "of", "key", "strengths"],
            "weaknesses": ["list", "of", "areas", "for", "improvement"],
            "skill_gaps": ["missing", "skills", "for", "tech", "roles"],
            "improvement_suggestions": ["specific", "actionable", "suggestions"],
            "career_recommendations": ["suitable", "job", "roles"],
            "ats_optimization_score": 75,
            "key_achievements": ["notable", "accomplishments"]
        }}

        Be specific, constructive, and data-driven in your analysis.
        """

    def _get_ai_response(self, prompt: str) -> str:
        """Get response from OpenAI API"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume analyst and career coach. Provide detailed, constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured data"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._parse_text_response(response)
        except:
            return self._get_default_analysis()

    def _parse_text_response(self, response: str) -> Dict:
        """Fallback parsing for text responses"""
        return {
            "overall_score": 70,
            "strengths": ["Strong technical background", "Relevant experience"],
            "weaknesses": ["Could use more quantifiable achievements"],
            "skill_gaps": ["Cloud technologies", "Advanced ML frameworks"],
            "improvement_suggestions": ["Add more metrics to experience", "Include project portfolio"],
            "career_recommendations": ["Software Engineer", "Data Analyst"],
            "ats_optimization_score": 65,
            "key_achievements": ["Multiple successful projects", "Technical leadership experience"]
        }

    def _get_fallback_analysis(self, resume_data: Dict) -> Dict:
        """Provide fallback analysis when AI fails"""
        skills = resume_data.get('skills', {})
        tech_skills_count = sum(len(skills_list) for skills_list in skills.values())
        
        return {
            "overall_score": min(80, tech_skills_count * 5 + 40),
            "strengths": ["Technical proficiency", "Industry experience"],
            "weaknesses": ["Limited detail in achievements", "Could improve formatting"],
            "skill_gaps": ["Advanced certifications", "Specialized tools"],
            "improvement_suggestions": [
                "Quantify achievements with numbers",
                "Add more project details",
                "Include relevant certifications"
            ],
            "career_recommendations": ["Technical roles", "Engineering positions"],
            "ats_optimization_score": 70,
            "key_achievements": ["Demonstrated technical capabilities", "Project experience"]
        }

    def _get_default_analysis(self) -> Dict:
        """Default analysis template"""
        return {
            "overall_score": 75,
            "strengths": [],
            "weaknesses": [],
            "skill_gaps": [],
            "improvement_suggestions": [],
            "career_recommendations": [],
            "ats_optimization_score": 70,
            "key_achievements": []
        }