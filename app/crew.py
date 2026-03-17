import json
from crewai import Crew, Process
from app.agents import get_agents
from app.tasks import get_tasks
from app.models import ResumeData, JobDescriptionData, InterviewResearchData, InterviewScript

def run_full_interview_pipeline(resume_file: str, jd_file: str):
    print(f"[*] Initializing Unified Interview Pipeline...")
    
    # 1. Initialize Agents
    extractor_agent, jd_analyzer_agent, researcher_agent, orchestrator_agent = get_agents()
    
    # 2. Initialize Tasks with native context dependencies
    # All tasks are initialized and linked inside get_tasks
    resume_task, jd_task, research_task, orchestration_task = get_tasks(resume_file, jd_file)
    
    # 3. Assign Agents to Tasks
    resume_task.agent = extractor_agent
    jd_task.agent = jd_analyzer_agent
    research_task.agent = researcher_agent
    orchestration_task.agent = orchestrator_agent
    
    # 4. Assemble the Crew
    interview_crew = Crew(
        agents=[extractor_agent, jd_analyzer_agent, researcher_agent, orchestrator_agent],
        tasks=[resume_task, jd_task, research_task, orchestration_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 5. Execute sequential pipeline
    print(f"[*] Kicking off full 4-agent sequential pipeline...")
    result = interview_crew.kickoff()
    
    print("\n" + "="*50)
    print("FINAL UNIFIED PIPELINE EXECUTION SUMMARY:")
    print("="*50 + "\n")
    
    # Extract results
    try:
        if hasattr(result, 'json_dict') and result.json_dict:
            print("[+] Successfully generated Interview Script.")
            return result.json_dict
        else:
            print("[!] Raw Output from final task:")
            print(result.raw)
            return result.raw
    except Exception as e:
        print(f"[!] Error processing final result: {e}")
        return str(result)
