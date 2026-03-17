from crewai import Task
from app.models import ResumeData, JobDescriptionData, InterviewResearchData, InterviewScript

def get_tasks(resume_file: str, jd_file: str):
    # Task 1: Resume Extraction
    resume_extraction_task = Task(
        description=(
            f"**OBJECTIVE:** Digitally ingest and parse the target resume document located at '{resume_file}'.\n\n"
            "**EXECUTION STEPS:**\n"
            "1. **Ingestion:** Utilize the 'Document Extractor Tool' to extract the raw, unstructured text data from the provided document.\n"
            "2. **Normalization & Extraction:** Perform a comprehensive semantic analysis of the unstructured text. Identify and isolate the following data entities while maintaining strict fidelity to the source material:\n"
            "   - **Candidate Name:** Extract the full legal or preferred name.\n"
            "   - **Skills:** Aggregate a comprehensive list of all technical, domain, and soft skills identified. Normalize the casing where appropriate.\n"
            "   - **Experience:** Chronologically reconstruct the candidate's professional timeline. For each role, distinctly categorize the 'company' name, job 'role' (title), tenure 'duration', and a 'description' highlighting key impacts, metrics, and responsibilities.\n"
            "   - **Projects:** Identify any notable standalone projects, open-source contributions, or academic capstones. Extract the project 'name', a concise 'description' of the objective and outcome, and a list of specific 'technologies' utilized.\n"
            "   - **Extra Curricular Activities:** Capture verifiable involvement in clubs, volunteering, certifications, or organized competitive events.\n"
            "3. **Validation:** Ensure no synthesized or hallucinated information is included. If a field is entirely absent from the source text, represent it as an empty list or 'Not Provided' as appropriate within the schema bounds.\n"
        ),
        expected_output=(
            "A deterministic, strictly-typed JSON payload conforming exactly to the `ResumeData` Pydantic schema. "
            "The payload must be clean, free of trailing whitespaces, and fully validated against the defined keys."
        ),
        output_json=ResumeData
    )

    # Task 2: JD Analysis
    jd_analysis_task = Task(
        description=(
            f"**OBJECTIVE:** Perform a comprehensive semantic audit and deconstruction of the Job Description (JD) located at '{jd_file}'.\n\n"
            "**EXECUTION PROTOCOL:**\n"
            "1. **Document Ingestion:** Interface with the 'Document Extractor Tool' to convert the target document into a raw text stream.\n"
            "2. **Entitiy Identification & Schema Mapping:** Scan the raw text to isolate and extract the following core business entities:\n"
            "   - **Company Name:** Extract the name of the hiring organization.\n"
            "   - **Job Title:** The official standardized designation for the role.\n"
            "   - **Required Skills:** Mandatory technical competencies, frameworks, and tools. Differentiate strictly between 'required' and 'preferred'.\n"
            "   - **Preferred Skills:** Optional but advantageous skills, certifications, or domain knowledge listed as 'bonus' or 'nice-to-have'.\n"
            "   - **Experience Level:** Extract specific tenure requirements (e.g., '5+ years') or seniority designations (e.g., 'L6', 'Senior Staff') and normalize this into a clear level.\n"
            "   - **Key Responsibilities:** Synthesize the core operational duties and business objectives the role is expected to meet. Remove generic descriptions.\n"
            "3. **Data Integrity Check:** Cross-reference extracted entities with the original text to prevent hallucination. High-fidelity output is mandatory; if the JD does not provide a specific piece of information, do not infer it—instead, leave the field empty or mark as 'Not Stated'.\n"
        ),
        expected_output=(
            "A deterministic, production-grade JSON payload conforming exactly to the `JobDescriptionData` schema. "
            "The data must be sanitized, normalized for industry standards, and ready for ATS integration."
        ),
        output_json=JobDescriptionData
    )

    # Task 3: Interview Research (Depends on JD Analysis)
    interview_research_task = Task(
        description=(
            "**STANDARD OPERATING PROCEDURE: INTERVIEW INTELLIGENCE SYNTHESIS**\n\n"
            "**OBJECTIVE:** Generate a comprehensive, multi-dimensional interview readiness matrix "
            "by analyzing the Job Description (JD) extracted in the previous task.\n\n"
            "**1. COMPETENCY ANALYSIS:**\n"
            "- Evaluate the hiring company's typical interviewing style based on the JD data.\n"
            "- Map the required skills and experience levels found in the context to specific technical assessment sub-domains.\n\n"
            "**2. MULTI-CHANNEL RESEARCH:**\n"
            "Execute deep searches across multiple channels (Glassdoor, Reddit, LeetCode, GitHub repos, Engineering Blogs) "
            "to find questions specifically relevant to the target job title and the company's core technology stack found in the JD context.\n\n"
            "**3. CATEGORY QUOTAS (TARGET: 50 QUESTIONS):**\n"
            "You MUST curate exactly 50 or more high-quality questions. The distribution should cover:\n"
            "- **Core Technical Proficiency (Mapping to JD Skills):** 20 Questions\n"
            "- **Role-Specific Architecture & Problem Solving (Mapping to Key Responsibilities):** 15 Questions\n"
            "- **Behavioral (STAR Method - Mapping to Team/Cultural values):** 10 Questions\n"
            "- **Company-Specific Insights (Unique to hiring company culture):** 5 Questions\n\n"
            "**4. ENHANCEMENT PROTOCOL:**\n"
            "For EACH question, provide:\n"
            "- **Difficulty:** Junior, Mid-Level, Senior, or Expert.\n"
            "- **Strategic Rationale:** Link the question back to the specific responsibility or skill.\n"
            "- **Key Answer Points:** 3-5 bullet points the candidate MUST mention to be successful.\n"
        ),
        expected_output=(
            "An enterprise-grade JSON payload conforming to the `InterviewResearchData` schema. "
            "The list MUST contain AT LEAST 50 distinct, high-impact interview questions derived dynamically from the JD context."
        ),
        output_json=InterviewResearchData,
        context=[jd_analysis_task]
    )

    # Task 4: Interview Orchestration (Depends on Resume and Research)
    interview_orchestration_task = Task(
        description=(
            "**OBJECTIVE:** Curate a high-speed, technical-intensive 30-minute interview script "
            "by dynamically analyzing the candidate's profile and the researched interview intelligence.\n\n"
            "**DYNAMIC EXECUTION HIERARCHY:**\n"
            "1. **Primary Focus: Technical Skills (10-12 Questions):** Identify the candidate's core skills "
            "from the provided resume extraction context. Match these directly with the high-stakes technical questions "
            "discovered in the interview research context. Probe for deep technical proficiency.\n"
            "2. **Secondary Focus: Professional Experience (8-10 Questions):** Analyze the candidate's "
            "professional chronicity from the context. Select questions that challenge their technical contributions "
            "at their previous companies.\n"
            "3. **Tertiary Focus: Projects (5-7 Questions):** Extract key project details from the context and "
            "probe the architectural decisions and problem-solving strategies using matched web-scraped questions.\n"
            "4. **Closing: Behavioral & Cultural Fit (Strictly 5-6 Questions):** Select the most relevant Google-specific "
            "behavioral questions from the research context to assess cultural alignment.\n\n"
            "**ORCHESTRATION MANDATE:**\n"
            "- You MUST synthesize information FROM the provided task contexts (Resume Extraction & Interview Research).\n"
            "- Do NOT use generic placeholders; every question must feel custom-made for the candidate's history found in the context.\n"
            "- Ensure the final result is a rapid-fire prioritized list of 25-30 questions."
        ),
        expected_output=(
            "A comprehensive JSON script conforming to the `InterviewScript` schema, containing AT LEAST 25-30 "
            "rapid-fire, prioritized questions optimized for a deep 30-minute technical evaluation."
        ),
        output_json=InterviewScript,
        context=[resume_extraction_task, interview_research_task], 
    )

    return resume_extraction_task, jd_analysis_task, interview_research_task, interview_orchestration_task
