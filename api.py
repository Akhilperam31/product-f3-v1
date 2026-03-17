import os
import uuid
import json
import base64
import asyncio
from typing import Dict
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.crew import run_full_interview_pipeline
from app.agents import InterviewerCrew
from app.speech import SpeechService
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services
speech_service = SpeechService()
interviewer_crew_service = InterviewerCrew()

# Global store for session data (in-memory for simplicity)
sessions: Dict[str, dict] = {}

# Ensure data/uploads directory exists
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_documents(
    resume: UploadFile = File(...),
    jd: UploadFile = File(...)
):
    try:
        session_id = str(uuid.uuid4())
        
        # Save files
        resume_path = os.path.join(UPLOAD_DIR, f"{session_id}_resume_{resume.filename}")
        jd_path = os.path.join(UPLOAD_DIR, f"{session_id}_jd_{jd.filename}")
        
        with open(resume_path, "wb") as f:
            f.write(await resume.read())
            
        with open(jd_path, "wb") as f:
            f.write(await jd.read())
            
        # Trigger Crew 1 (Agents 1-4)
        print(f"[*] Starting Crew 1 for session {session_id}...")
        # run_full_interview_pipeline returns the InterviewScript as a dict
        loop = asyncio.get_event_loop()
        script_data = await loop.run_in_executor(None, run_full_interview_pipeline, resume_path, jd_path)
        
        if not script_data:
            return JSONResponse(content={"error": "Failed to generate interview script"}, status_code=500)
            
        # Store script data in session
        sessions[session_id] = {
            "script_data": script_data,
            "interviewer_agent": None # Will be initialized on WebSocket connect
        }
        
        return JSONResponse(content={"session_id": session_id})
        
    except Exception as e:
        print(f"Error in upload: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.websocket("/ws/interview/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    if session_id not in sessions:
        await websocket.close(code=1008) # Policy Violation
        return

    await websocket.accept()
    session = sessions[session_id]
    script_data = session["script_data"]
    
    # Initialize Agent 5 (Interviewer Agent) with script context
    interviewer_agent = interviewer_crew_service.create_interviewer_agent(script_data)
    session["interviewer_agent"] = interviewer_agent
    
    session_history = ""
    
    # 1. Send Intro (Agent 5's greeting)
    # We'll use a standard intro first then trigger the agent
    candidate_name = script_data.get("candidate_name", "Candidate")
    intro_text = f"Hello {candidate_name}, welcome to your interview. I've reviewed your profile and the job requirements. Let's begin."
    
    audio_bytes = speech_service.text_to_speech(intro_text)
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    await websocket.send_json({
        "type": "agent_speech", 
        "text": intro_text, 
        "audio_base64": audio_base64
    })
    
    # 2. Trigger Agent to ask for candidate introduction
    print(f"Triggering agent for intro request for session {session_id}...")
    loop = asyncio.get_event_loop()
    agent_msg = await loop.run_in_executor(
        None, 
        interviewer_crew_service.process_response, 
        interviewer_agent, 
        f"System: Interview started.", 
        "Please introduce yourself."
    )
    
    q_audio_bytes = speech_service.text_to_speech(agent_msg)
    q_audio_base64 = base64.b64encode(q_audio_bytes).decode('utf-8')
    
    session_history = f"Agent: {intro_text}\nAgent: {agent_msg}\n"
    
    await websocket.send_json({
        "type": "agent_speech", 
        "text": agent_msg, 
        "audio_base64": q_audio_base64
    })

    try:
        while True:
            data = await websocket.receive_bytes()
            if len(data) < 200: 
                continue

            try:
                user_text = speech_service.transcribe_audio(data)
            except Exception as e:
                print(f"Transcription failed: {e}")
                continue
            
            if not user_text.strip():
                continue
                
            await websocket.send_json({"type": "user_transcript", "text": user_text})
            
            # Agent decides (Follow-up or Next script question)
            session_history += f"Candidate: {user_text}\n"
            agent_response = await loop.run_in_executor(
                None, 
                interviewer_crew_service.process_response, 
                interviewer_agent, 
                session_history, 
                user_text
            )
            
            session_history += f"Agent: {agent_response}\n"
            
            # TTS
            resp_audio_bytes = speech_service.text_to_speech(agent_response)
            resp_audio_base64 = base64.b64encode(resp_audio_bytes).decode('utf-8')
            
            await websocket.send_json({
                "type": "agent_speech", 
                "text": agent_response, 
                "audio_base64": resp_audio_base64
            })
            
            if "Thank you for the interview" in agent_response:
                await asyncio.sleep(5)
                await websocket.close()
                break

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error in websocket loop: {e}")
        await websocket.send_json({"type": "error", "text": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
