import os
import warnings
warnings.filterwarnings('ignore')

# Disable NLTK downloads and usage
os.environ['NLTK_DATA'] = '/tmp/nltk_data'

# Mock NLTK to prevent downloads
try:
    import nltk
    nltk.data.path = ['/tmp/nltk_data']  # Set to non-existent path
except ImportError:
    pass

import streamlit as st
import pandas as pd
import plotly.express as px
# ... rest of your imports
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import tempfile
from datetime import datetime
import base64

# Import custom modules
from utils.resume_parser import ResumeParser
from utils.ai_analyzer import AIAnalyzer
from utils.job_matcher import JobMatcher

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .resume-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
    }
    .match-high {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 10px;
        border-radius: 10px;
    }
    .match-medium {
        background: linear-gradient(135deg, #FF9800, #F57C00);
        color: white;
        padding: 10px;
        border-radius: 10px;
    }
    .match-low {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
        padding: 10px;
        border-radius: 10px;
    }
    .skill-bar {
        background: #e0e0e0;
        border-radius: 10px;
        margin: 5px 0;
    }
    .skill-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 10px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

class ResumeAnalyzerApp:
    def __init__(self):
        self.parser = ResumeParser()
        self.job_matcher = JobMatcher()
        self.ai_analyzer = None
        
        # Initialize session state
        if 'analysis_complete' not in st.session_state:
            st.session_state.analysis_complete = False
        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = None
        if 'ai_analysis' not in st.session_state:
            st.session_state.ai_analysis = None
        if 'job_matches' not in st.session_state:
            st.session_state.job_matches = None

    def run(self):
        """Main application runner"""
        load_css()
        
        # Header
        st.title("🚀 AI-Powered Resume Analyzer Pro")
        st.markdown("### Transform Your Resume with AI-Driven Insights")
        
        # Sidebar
        self.render_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Resume", "📊 Analysis", "💼 Job Matches", "🎯 Improvement Plan"])
        
        with tab1:
            self.render_upload_section()
        
        with tab2:
            if st.session_state.analysis_complete:
                self.render_analysis_section()
            else:
                st.info("👆 Upload your resume to get started!")
        
        with tab3:
            if st.session_state.analysis_complete:
                self.render_job_matches_section()
            else:
                st.info("👆 Upload your resume to see job matches!")
        
        with tab4:
            if st.session_state.analysis_complete:
                self.render_improvement_plan()
            else:
                st.info("👆 Upload your resume to get personalized improvement suggestions!")

    def render_sidebar(self):
        """Render sidebar with API key input and info"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # API Key Input
            api_key = st.text_input(
                "OpenAI API Key (Optional)",
                type="password",
                help="For enhanced AI analysis. Get one from https://platform.openai.com"
            )
            
            if api_key:
                self.ai_analyzer = AIAnalyzer(api_key)
            
            st.markdown("---")
            st.header("📈 Features")
            st.markdown("""
            - ✅ **Smart Resume Parsing**
            - 🤖 **AI-Powered Analysis**
            - 🎯 **Job Matching**
            - 📊 **Skill Gap Analysis**
            - 💡 **Improvement Suggestions**
            - 📈 **ATS Optimization**
            """)
            
            st.markdown("---")
            st.header("💡 Tips")
            st.markdown("""
            - Use PDF or DOCX format
            - Ensure text is selectable
            - Include quantifiable achievements
            - Highlight technical skills
            - Keep formatting clean
            """)

    def render_upload_section(self):
        """Render resume upload section"""
        st.header("📤 Upload Your Resume")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose your resume file",
                type=['pdf', 'docx'],
                help="Supported formats: PDF, DOCX"
            )
            
            if uploaded_file is not None:
                # Display file info
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{uploaded_file.size / 1024:.1f} KB",
                    "File type": uploaded_file.type
                }
                
                st.json(file_details)
                
                # Process file
                if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
                    with st.spinner("Analyzing your resume..."):
                        self.process_resume(uploaded_file)

        with col2:
            st.markdown("### 📝 Sample Resume")
            st.markdown("""
            For best results, ensure your resume includes:
            
            - **Contact Information**
            - **Professional Summary**
            - **Work Experience**
            - **Education**
            - **Technical Skills**
            - **Projects & Achievements**
            """)

    def process_resume(self, uploaded_file):
        """Process the uploaded resume file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Parse resume
            file_type = "pdf" if uploaded_file.type == "application/pdf" else "docx"
            resume_data = self.parser.parse_resume(tmp_path, file_type)
            
            # AI Analysis
            if self.ai_analyzer:
                ai_analysis = self.ai_analyzer.analyze_resume(resume_data)
            else:
                ai_analysis = self.get_basic_analysis(resume_data)
            
            # Job Matching
            job_matches = self.job_matcher.match_resume_to_jobs(resume_data)
            
            # Update session state
            st.session_state.resume_data = resume_data
            st.session_state.ai_analysis = ai_analysis
            st.session_state.job_matches = job_matches
            st.session_state.analysis_complete = True
            
            # Cleanup
            os.unlink(tmp_path)
            
            st.success("✅ Analysis complete! Navigate to other tabs to see results.")
            
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")

    def get_basic_analysis(self, resume_data):
        """Provide basic analysis when AI is not available"""
        skills = resume_data.get('skills', {})
        tech_skills_count = sum(len(skills_list) for skills_list in skills.values())
        
        return {
            "overall_score": min(75, tech_skills_count * 5 + 40),
            "strengths": ["Automated parsing successful", "Skills identified"],
            "weaknesses": ["Enable AI for detailed analysis", "Add OpenAI API key for enhanced insights"],
            "skill_gaps": ["AI-powered analysis unavailable"],
            "improvement_suggestions": [
                "Add OpenAI API key for AI analysis",
                "Include more quantifiable achievements",
                "Highlight specific technical projects"
            ],
            "career_recommendations": ["Technical roles based on skills"],
            "ats_optimization_score": 65,
            "key_achievements": ["Resume successfully parsed", "Skills extracted"]
        }

    def render_analysis_section(self):
        """Render comprehensive analysis results"""
        st.header("📊 Resume Analysis Dashboard")
        
        # Overall Score Card
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            overall_score = st.session_state.ai_analysis.get('overall_score', 0)
            self.render_score_card("Overall Score", overall_score, "Total assessment score")
        
        with col2:
            ats_score = st.session_state.ai_analysis.get('ats_optimization_score', 0)
            self.render_score_card("ATS Score", ats_score, "Applicant Tracking System optimization")
        
        with col3:
            skills_count = sum(len(skills) for skills in st.session_state.resume_data.get('skills', {}).values())
            self.render_score_card("Skills Found", skills_count, "Technical skills identified")
        
        with col4:
            exp_count = len(st.session_state.resume_data.get('experience', []))
            self.render_score_card("Experience Entries", exp_count, "Work experience items")
        
        # Detailed Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_skills_analysis()
            self.render_strengths_weaknesses()
        
        with col2:
            self.render_ai_insights()
            self.render_personal_info()

    def render_score_card(self, title, score, description):
        """Render a score card with appropriate styling"""
        if isinstance(score, (int, float)):
            if score >= 80:
                css_class = "match-high"
            elif score >= 60:
                css_class = "match-medium"
            else:
                css_class = "match-low"
        else:
            css_class = "match-medium"
        
        st.markdown(f"""
        <div class="resume-card {css_class}">
            <h3>{title}</h3>
            <h2>{score}</h2>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

    def render_skills_analysis(self):
        """Render skills analysis visualization"""
        st.subheader("🛠 Technical Skills Analysis")
        
        skills_data = st.session_state.resume_data.get('skills', {})
        
        if skills_data:
            # Prepare data for visualization
            categories = []
            counts = []
            
            for category, skill_list in skills_data.items():
                if skill_list:  # Only include categories with skills
                    categories.append(category.replace('_', ' ').title())
                    counts.append(len(skill_list))
            
            if categories:
                fig = px.bar(
                    x=counts,
                    y=categories,
                    orientation='h',
                    title="Skills by Category",
                    labels={'x': 'Number of Skills', 'y': 'Category'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No technical skills detected in resume.")
        else:
            st.warning("No skills data available.")

    def render_strengths_weaknesses(self):
        """Render strengths and weaknesses analysis"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Strengths")
            strengths = st.session_state.ai_analysis.get('strengths', [])
            if strengths:
                for strength in strengths[:5]:  # Show top 5
                    st.markdown(f"• {strength}")
            else:
                st.info("No strengths identified.")
        
        with col2:
            st.subheader("📈 Areas for Improvement")
            weaknesses = st.session_state.ai_analysis.get('weaknesses', [])
            if weaknesses:
                for weakness in weaknesses[:5]:  # Show top 5
                    st.markdown(f"• {weakness}")
            else:
                st.info("No improvement areas identified.")

    def render_ai_insights(self):
        """Render AI-powered insights"""
        st.subheader("🤖 AI Insights & Recommendations")
        
        insights = st.session_state.ai_analysis
        
        # Key Achievements
        st.markdown("#### 🏆 Key Achievements")
        achievements = insights.get('key_achievements', [])
        if achievements:
            for achievement in achievements[:3]:
                st.markdown(f"• {achievement}")
        else:
            st.info("No specific achievements highlighted.")
        
        # Career Recommendations
        st.markdown("#### 🎯 Career Recommendations")
        recommendations = insights.get('career_recommendations', [])
        if recommendations:
            for rec in recommendations[:4]:
                st.markdown(f"• **{rec}**")
        else:
            st.info("Upload resume with OpenAI API for career recommendations.")

    def render_personal_info(self):
        """Render extracted personal information"""
        st.subheader("👤 Contact Information")
        
        personal_info = st.session_state.resume_data.get('personal_info', {})
        
        if personal_info:
            info_html = ""
            if personal_info.get('email'):
                info_html += f"📧 **Email:** {personal_info['email']}<br>"
            if personal_info.get('phone'):
                info_html += f"📞 **Phone:** {personal_info['phone']}<br>"
            if personal_info.get('linkedin'):
                info_html += f"💼 **LinkedIn:** {personal_info['linkedin']}<br>"
            
            if info_html:
                st.markdown(info_html, unsafe_allow_html=True)
            else:
                st.info("No contact information detected.")
        else:
            st.info("No personal information extracted.")

    def render_job_matches_section(self):
        """Render job matching results"""
        st.header("💼 Job Recommendations")
        
        if not st.session_state.job_matches:
            st.warning("No job matches found.")
            return
        
        # Overall matching statistics
        avg_match = sum(job['match_score'] for job in st.session_state.job_matches) / len(st.session_state.job_matches)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Match Score", f"{avg_match:.1f}%")
        with col2:
            st.metric("Top Match", f"{st.session_state.job_matches[0]['match_score']}%")
        with col3:
            st.metric("Jobs Analyzed", len(st.session_state.job_matches))
        
        # Job matches
        for i, job in enumerate(st.session_state.job_matches[:5]):
            with st.container():
                self.render_job_card(job, i)

    def render_job_card(self, job, index):
        """Render individual job match card"""
        # Determine match level
        if job['match_score'] >= 80:
            match_class = "match-high"
            match_emoji = "🎯"
        elif job['match_score'] >= 60:
            match_class = "match-medium"
            match_emoji = "✅"
        else:
            match_class = "match-low"
            match_emoji = "📊"
        
        st.markdown(f"""
        <div class="resume-card {match_class}">
            <h3>{match_emoji} {job['title']} at {job['company']}</h3>
            <h4>Match Score: {job['match_score']}%</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Job details in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Experience Level:** {job['experience_level']}")
            st.markdown(f"**Salary Range:** {job['salary_range']}")
        
        with col2:
            st.markdown("**Matching Skills:**")
            matching_skills = job.get('matching_skills', [])[:5]
            for skill in matching_skills:
                st.markdown(f"• {skill.title()}")
        
        with col3:
            st.markdown("**Skills to Learn:**")
            missing_skills = job.get('missing_skills', [])[:3]
            for skill in missing_skills:
                st.markdown(f"• {skill.title()}")
        
        # Expandable job description
        with st.expander("View Job Description"):
            st.write(job['description'])
        
        st.markdown("---")

    def render_improvement_plan(self):
        """Render personalized improvement plan"""
        st.header("🎯 Personalized Improvement Plan")
        
        ai_analysis = st.session_state.ai_analysis
        
        # Skill Gaps
        st.subheader("🔍 Identified Skill Gaps")
        skill_gaps = ai_analysis.get('skill_gaps', [])
        if skill_gaps:
            for gap in skill_gaps:
                st.markdown(f"• **{gap}**")
        else:
            st.info("No specific skill gaps identified.")
        
        # Improvement Suggestions
        st.subheader("💡 Actionable Suggestions")
        suggestions = ai_analysis.get('improvement_suggestions', [])
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"{i}. {suggestion}")
        else:
            st.info("Enable AI analysis for personalized suggestions.")
        
        # ATS Optimization Tips
        st.subheader("📈 ATS Optimization Tips")
        ats_tips = [
            "Use standard section headings (Experience, Education, Skills)",
            "Include relevant keywords from job descriptions",
            "Use bullet points for achievements",
            "Quantify results with numbers and percentages",
            "Avoid graphics and complex formatting",
            "Use common fonts (Arial, Calibri, Times New Roman)",
            "Save as PDF format",
            "Include contact information clearly"
        ]
        
        for tip in ats_tips:
            st.markdown(f"• {tip}")

def main():
    """Main application entry point"""
    app = ResumeAnalyzerApp()
    app.run()

if __name__ == "__main__":
    main()
