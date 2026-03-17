from typing import List, Optional
from pydantic import BaseModel, Field

class Project(BaseModel):
    name: str = Field(description="Name of the project")
    description: str = Field(description="Brief summary of the project")
    technologies: List[str] = Field(description="Technologies used in the project")

class Experience(BaseModel):
    company: str = Field(description="Company name")
    role: str = Field(description="Job title")
    duration: str = Field(description="Time period (e.g. 'Jan 2021 - Present')")
    description: str = Field(description="Primary responsibilities or achievements")

class ResumeData(BaseModel):
    candidate_name: str = Field(description="Full name of the candidate")
    skills: List[str] = Field(description="Technical and soft skills")
    projects: List[Project] = Field(description="Projects the candidate has worked on")
    experience: List[Experience] = Field(description="Professional work experience")
    extra_curricular_activities: List[str] = Field(description="Clubs, volunteering, or hobbies")

class JobDescriptionData(BaseModel):
    company_name: str = Field(description="The name of the company hiring for the position")
    job_title: str = Field(description="The title of the open position")
    required_skills: List[str] = Field(description="Mandatory technical and soft skills required for the role")
    preferred_skills: List[Optional[str]] = Field(description="Nice-to-have or preferred skills")
    experience_level: str = Field(description="Required years of experience or seniority level")
    key_responsibilities: List[str] = Field(description="Primary duties and expectations of the role")

class InterviewQuestion(BaseModel):
    question: str = Field(description="The specific interview question")
    category: str = Field(description="Categorization: 'Technical', 'Behavioral', 'System Design', 'Cultural Fit', or 'Problem Solving'")
    difficulty: str = Field(description="Assessment of difficulty: 'Junior', 'Mid-Level', 'Senior', or 'Expert'")
    rationale: str = Field(description="Strategic justification for why this question is high-probability for the target company/role")
    key_answer_points: List[str] = Field(description="Bullet points outlining the ideal components of a high-quality answer")

class InterviewResearchData(BaseModel):
    company_name: str = Field(description="Target company analyzed")
    job_title: str = Field(description="Job title analyzed")
    total_questions: int = Field(description="Total count of questions generated (Minimum 50)")
    questions: List[InterviewQuestion] = Field(description="A comprehensive list of 50+ targeted interview questions")

class CuratedQuestion(BaseModel):
    question: str = Field(description="The primary interview question (Matched with web research)")
    category: str = Field(description="'Skill-Based', 'Experience-Based', 'Project-Based', or 'Behavioral'")
    context: str = Field(description="Direct link to candidate's background")
    key_points: List[str] = Field(description="Short benchmarks for the interviewer")

class InterviewScript(BaseModel):
    candidate_name: str = Field(description="Name of the candidate")
    company_name: str = Field(description="Target company name")
    estimated_duration: str = Field(default="30 Minutes")
    total_questions: int = Field(description="Count of questions in this script (Target 25+)")
    questions: List[CuratedQuestion] = Field(description="Rapid-fire priority list: 1. Skills, 2. Experience, 3. Projects, followed by 5-6 Behavioral questions.")



