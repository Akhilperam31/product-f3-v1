from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI
from app.tools import extract_document_tool, search_tool
import os
import streamlit as st


def get_agents():
    extractor_agent = Agent(
        role="Principal Talent Intelligence Analyst",
        goal=(
            "Perform deep semantic extraction of unstructured candidate resumes and strictly output "
            "a highly structured, sanitized, and normalized data schema encompassing the "
            "candidate's core identity, chronological work experience, portfolio of projects, "
            "technical skill matrices, and extra-curricular engagements."
        ),
        backstory=(
            "You are a cutting-edge Enterprise AI specializing in Human Resources schema mapping "
            "and data extraction. Built by a team of elite data scientists, your primary function "
            "is to eliminate manual data entry by processing diverse, complex, and sometimes poorly "
            "formatted PDF resumes. You possess an unparalleled understanding of industry jargon, "
            "role hierarchies, and project lifecycles. You are meticulous; you ensure that durations "
            "are parsed consistently, descriptions are concisely captured without losing critical "
            "business impact metrics, and technologies are accurately identified. Your output is "
            "the foundational layer for downstream Applicant Tracking Systems (ATS) routing, and "
            "thus operates with a zero-hallucination, high-fidelity mandate."
        ),
        verbose=True,
        allow_delegation=False, # strictly bounded to one agent for deterministic extraction
        tools=[extract_document_tool]
    )

    jd_analyzer_agent = Agent(
        role="Principal Workforce Architect & Strategist",
        goal=(
            "Analyze and deconstruct Job Descriptions (JD) to extract a high-fidelity 'Requirement Matrix'. "
            "Strictly identify the hiring company identity, core technical mandate, seniority expectations, and business-critical "
            "responsibilities while filtering out non-functional corporate boilerplate."
        ),
        backstory=(
            "You are an elite Workforce Architect specializing in Technical Talent Acquisition and Organizational "
            "Design. Your expertise lies in translating vague human-authored job requisitions into precise, "
            "machine-readable requirement specifications. You possess an advanced understanding of the "
            "global tech landscape, including evolving stack dependencies, seniority benchmarks, and "
            "industry-standard role definitions. Your mission is to provide the 'Ground Truth' for "
            "recruitment pipelines by ensuring that every skill, responsibility, and qualification is "
            "categorized with surgical precision. You operate as a critical validation gate, ensuring that "
            "downstream matching algorithms receive data that is accurate, normalized, and free of "
            "ambiguous jargon."
        ),
        verbose=True,
        allow_delegation=False, # restricted to single-agent execution for deterministic mapping
        tools=[extract_document_tool]
    )

    interview_researcher_agent = Agent(
        role="Principal Interview Intelligence Strategist",
        goal=(
            "Synthesize massive amounts of real-world interview intelligence to generate a "
            "multi-dimensional 50-question readiness matrix. Provide actionable rationale "
            "and answer keys for every query."
        ),
        backstory=(
            "You are a world-class Interview Intelligence Strategist with a background in "
            "Executive Search and Technical Assessment Design. You leverage advanced "
            "web research techniques to bypass generic content and find high-stakes, "
            "frequently-asked technical and behavioral questions specific to target "
            "organizations. You understand the 'Interview Flywheel'—how specific projects "
            "and cultural values at a company dictate the types of questions candidates "
            "face. Your output is the gold standard for high-performance interview preparation."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool]
    )
    interview_orchestrator_agent = Agent(
        role="Principal Technical Assessment Architect",
        goal=(
            "Execute a high-velocity, rapid-fire 30-minute technical interview script. "
            "Prioritize deep-probing of candidate skills, professional experience, and technical projects "
            "by matching them with real-world researched interview data."
        ),
        backstory=(
            "You are a master of high-stakes technical evaluations at elite firms. "
            "You specialize in 'Rapid-Fire Assessment'—the ability to probe a candidate's "
            "technical depth across 25-30 questions within a 30-minute window. "
            "You are dynamic and uncompromising; you map every technical skill, past "
            "professional challenge, and architectural decision in the candidate's history "
            "to real-world interview questions scraped from industry sources. "
            "Your priority is Skills first, followed by Experience, then Projects, "
            "finishing with a precise set of cultural alignment markers. You ensure no "
            "stone is left unturned in a candidate's technical profile."
        ),
        verbose=True,
        allow_delegation=False
    )

    return extractor_agent, jd_analyzer_agent, interview_researcher_agent, interview_orchestrator_agent


class InterviewerCrew:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0.5,
            openai_api_key=st.secrets["OPENAI_API_KEY"]
        )
        
    def create_interviewer_agent(self, script_data: dict) -> Agent:
        candidate_name = script_data.get("candidate_name", "Candidate")
        company_name = script_data.get("company_name", "the company")
        
        # Format questions for the prompt instead of using a tool
        questions_str = "\n".join([f"- {q['question']} (Category: {q['category']})" for q in script_data.get("questions", [])])

        return Agent(
            role='Technical Interviewer',
            goal=f'Conduct a professional and insightful mock interview at {company_name} for {candidate_name}.',
            backstory=f"""
            You are a highly professional AI Technical Interviewer for {company_name}. 
            Your goal is to evaluate the candidate "{candidate_name}" based on a specific set of questions that have been researched and curated for them.

            HERE IS THE CURATED INTERVIEW SCRIPT:
            {questions_str}

            STRICT GUIDELINES:
            1. **Response Style**:
               - Be warm, polite, and professional (address as "{candidate_name}").
               - Keep your questions and responses clear and concise.

            2. **Interview Flow & Time Management**:
               - START: Your first task is to ask "{candidate_name}" to introduce themselves. 
               - AFTER INTRO: Once they have introduced themselves, acknowledge it briefly and then ask the first question from the script above.
               - SCRIPT: Ask ONE question at a time from the script. Do NOT dump all questions.
               - CROSS-QUESTIONING: You MUST ask cross-questions (follow-ups) based on their answers if you feel a concept needs more depth or if their answer is interesting but shallow. This is critical for assessing depth.
               - DURATION: The total interview should be efficient but thorough.

            3. **Closing**:
               - If the candidate says 'End the Interview', you finish the script, or the 30-minute limit is reached, say exactly: "Thank you for the interview. You will get the evaluation document to your mail."
            """,
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def process_response(self, interviewer: Agent, chat_history: str, user_response: str) -> str:
        """Let the agent decide the next step based on script and history."""
        task = Task(
            description=f"""The interview is in progress. 
            Chat History so far: 
            {chat_history}
            
            Latest candidate response: '{user_response}'.
            
            Evaluate the response and decide:
            - If this is the beginning, greet the candidate and ask for a self-introduction.
            - If the self-introduction is done, start with the first question from the script in your backstory.
            - If a response is interesting or shallow, ask a cross-question (follow-up).
            - If a script question is sufficiently answered (including any follow-ups), pick the NEXT question from the script in your backstory.
            - If it's 'End the Interview', provide the thank you message.
            
            IMPORTANT: Stay in character as the professional interviewer.""",
            agent=interviewer,
            expected_output="The next question, a relevant cross-question, or the mandatory 'End the Interview' message."
        )
        
        crew = Crew(
            agents=[interviewer],
            tasks=[task],
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return str(result)

