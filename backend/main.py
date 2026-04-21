from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

# Initialize the FastAPI application
app = FastAPI(title="Local Autonomous AI Agent")

# CORS so Flutter Web can talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data structure coming from your Flutter app
class TaskRequest(BaseModel):
    user_id: str
    prompt: str

@app.get("/")
def read_root():
    return {"status": "Backend is running loud and clear"}

# ==========================================
# 1. THE TOOLBOX (Your Python Functions)
# ==========================================

def check_flight_status(flight_number: str) -> str:
    """Checks the current real-time status of a given flight number."""
    # In a production app, this would use the requests library to hit an aviation API.
    print(f"\n[SYSTEM] ✈️ Executing API call for flight {flight_number}...")
    return f"Flight {flight_number} is currently boarding at Gate 4, on time."

def book_flight(origin: str, destination: str, date: str) -> str:
    """Books a flight ticket between two cities on a specific date."""
    print(f"\n[SYSTEM] 📅 Executing booking from {origin} to {destination} on {date}...")
    return f"Booking confirmed. Your confirmation code is XYZ890."

# ==========================================
# 2. THE AGENT LOGIC
# ==========================================

@app.post("/api/execute_task")
def execute_task(request: TaskRequest):
    print("\n" + "="*50)
    print(f"🚀 NEW INCOMING TASK")
    print(f"👤 User: {request.user_id}")
    print(f"💬 Prompt: '{request.prompt}'")
    print("="*50)
    
    print("🧠 AI is analyzing the request...")
    
    try:
        # Give the prompt and the toolbox to the local Llama 3.1 model
        response = ollama.chat(
            model='gemma4:e4b',
            messages=[{'role': 'user', 'content': request.prompt}],
            tools=[check_flight_status, book_flight], # The LLM reads these functions natively
        )
        
        bot_response = ""
        action_taken = "none"
        result = ""

        # Check if the AI decided it needs to use a tool to fulfill the request
        if response.get('message', {}).get('tool_calls'):
            print("🔧 AI decided to use a tool!")
            
            for tool in response['message']['tool_calls']:
                tool_name = tool['function']['name']
                arguments = tool['function']['arguments']
                
                print(f"   -> Selected Tool: {tool_name}")
                print(f"   -> Extracted Data: {arguments}")
                
                # Execute the specific Python function the AI requested
                if tool_name == 'check_flight_status':
                    result = check_flight_status(arguments.get('flight_number', 'Unknown'))
                    action_taken = "checked_flight"
                    
                elif tool_name == 'book_flight':
                    result = book_flight(
                        arguments.get('origin', ''), 
                        arguments.get('destination', ''), 
                        arguments.get('date', '')
                    )
                    action_taken = "booked_flight"

            # Formulate the final response using the data returned from the Python function
            bot_response = f"Action Completed: {result}"

        else:
            # The AI decided this was just a normal conversation, no tools needed
            print("💬 AI determined no tools are required. Generating conversational response.")
            bot_response = response['message']['content']
            action_taken = "general_chat"

        print(f"\n📤 Sending back to Flutter app: {bot_response}")
        print("="*50 + "\n")

        return {
            "status": "success",
            "feedback": bot_response,
            "action_taken": action_taken
        }

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
