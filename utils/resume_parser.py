import pdfplumber
import docx
import re
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(stopwords.words('english'))
        
        # Enhanced skill keywords
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js', 'express'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'ml', 'ai'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack']
        }
        
        self.education_keywords = ['university', 'college', 'institute', 'bachelor', 'master', 'phd', 'degree']

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text

    def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """Main method to parse resume and extract information"""
        if file_type == "pdf":
            text = self.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

        return self.analyze_text(text)

    def analyze_text(self, text: str) -> Dict:
        """Analyze extracted text and structure information"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Extract sections
        sections = self.extract_sections(text)
        
        return {
            'raw_text': text,
            'personal_info': self.extract_personal_info(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'sections': sections,
            'stats': self.calculate_stats(text)
        }

    def extract_sections(self, text: str) -> Dict:
        """Identify and extract resume sections"""
        sections = {}
        lines = text.split('\n')
        
        current_section = "Summary"
        section_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            if self.is_section_header(line):
                if current_section and section_content:
                    sections[current_section] = ' '.join(section_content)
                current_section = line
                section_content = []
            else:
                section_content.append(line)
        
        if current_section and section_content:
            sections[current_section] = ' '.join(section_content)
            
        return sections

    def is_section_header(self, line: str) -> bool:
        """Check if a line is likely a section header"""
        header_patterns = [
            r'^(experience|work experience|employment history)',
            r'^(education|academic background)',
            r'^(skills|technical skills|competencies)',
            r'^(projects|personal projects)',
            r'^(certifications|certificates)',
            r'^(achievements|awards)',
            r'^(summary|objective|about)'
        ]
        
        line_lower = line.lower().strip()
        return any(re.match(pattern, line_lower) for pattern in header_patterns)

    def extract_personal_info(self, text: str) -> Dict:
        """Extract personal information"""
        # Email
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        # Phone numbers
        phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        # LinkedIn profile
        linkedin = re.findall(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9-]+', text)
        
        return {
            'email': emails[0] if emails else None,
            'phone': phones[0] if phones else None,
            'linkedin': linkedin[0] if linkedin else None
        }

    def extract_skills(self, text: str) -> Dict:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.technical_skills.items():
            found_skills[category] = []
            for skill in skills:
                if skill in text_lower:
                    found_skills[category].append(skill)
        
        return found_skills

    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience information"""
        experience = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Simple pattern matching for experience entries
            if re.search(r'\b(\d{4})\s*[-–]\s*(\d{4}|present|current)\b', line, re.IGNORECASE):
                exp_entry = {
                    'duration': re.search(r'\b(\d{4})\s*[-–]\s*(\d{4}|present|current)\b', line).group(),
                    'position': line,
                    'company': self.extract_company_name(line)
                }
                experience.append(exp_entry)
        
        return experience

    def extract_company_name(self, line: str) -> str:
        """Extract company name from experience line"""
        # Remove duration and position words to get company name
        cleaned = re.sub(r'\b(\d{4})\s*[-–]\s*(\d{4}|present|current)\b', '', line)
        cleaned = re.sub(r'\b(senior|junior|lead|manager|director|engineer|developer|analyst)\b', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in self.education_keywords):
                education.append({
                    'institution': line,
                    'degree': self.extract_degree(line)
                })
        
        return education

    def extract_degree(self, line: str) -> str:
        """Extract degree information from education line"""
        degrees = ['bachelor', 'master', 'phd', 'associate', 'diploma', 'certificate']
        line_lower = line.lower()
        
        for degree in degrees:
            if degree in line_lower:
                return degree.capitalize()
        return "Unknown"

    def calculate_stats(self, text: str) -> Dict:
        """Calculate resume statistics"""
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'unique_words': len(set(words))
        }
