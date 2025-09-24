"""
Enhanced Agent Engine - Main Orchestrator (Chatbot Interface)
Based on TestMozart architecture with additional capabilities for:
- Git repository analysis
- JIRA integration  
- PDF processing
- Code change analysis
- Script generation
"""

import asyncio
import json
import re
from typing import Dict, Any, Optional, List
from google.adk.runners import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv

# Import the enhanced coordinator with all subagents
from agents.enhanced_coordinator import enhanced_root_agent

class ChatbotOrchestrator:
    """Main orchestrator that provides a chatbot interface for the agent system."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="enhanced_agent_engine",
            agent=enhanced_root_agent,
            session_service=self.session_service
        )
        self.active_sessions = {}
    
    async def create_session(self, user_id: str) -> str:
        """Create a new chat session for a user."""
        session = await self.runner.session_service.create_session(
            app_name="enhanced_agent_engine",
            user_id=user_id
        )
        self.active_sessions[user_id] = session
        return session.session_id
    
    async def process_user_message(self, user_id: str, message: str) -> str:
        """Process a user message and return the agent's response."""
        if user_id not in self.active_sessions:
            await self.create_session(user_id)
        
        # Detect the type of request and route accordingly
        request_type = self._detect_request_type(message)
        
        # Format the request for the agent system
        formatted_request = self._format_request(message, request_type)
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=formatted_request)]
        )
        
        # Stream the response from the agent system
        final_output = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=self.active_sessions[user_id].session_id,
            content=user_message
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    final_output += event.content.parts[0].text
        
        return final_output
    
    def _detect_request_type(self, message: str) -> str:
        """Detect the type of request from the user message."""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['git', 'repository', 'repo', 'github', 'gitlab']):
            if any(keyword in message_lower for keyword in ['analyze', 'changes', 'diff', 'commit']):
                return "git_analysis"
            else:
                return "git_pull"
        
        elif any(keyword in message_lower for keyword in ['jira', 'ticket', 'issue', 'story']):
            if any(keyword in message_lower for keyword in ['test', 'case', 'scenario']):
                return "jira_test_generation"
            else:
                return "jira_analysis"
        
        elif any(keyword in message_lower for keyword in ['pdf', 'document', 'file']):
            return "pdf_processing"
        
        elif any(keyword in message_lower for keyword in ['script', 'automation', 'generate']):
            return "script_generation"
        
        elif any(keyword in message_lower for keyword in ['test', 'unittest', 'pytest']):
            return "test_generation"
        
        elif any(keyword in message_lower for keyword in ['analyze', 'code', 'review']):
            return "code_analysis"
        
        else:
            return "general_chat"
    
    def _format_request(self, message: str, request_type: str) -> str:
        """Format the user request for the agent system."""
        request_data = {
            "user_message": message,
            "request_type": request_type,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Add specific formatting based on request type
        if request_type == "git_analysis":
            request_data["task"] = "analyze_git_repository"
        elif request_type == "jira_test_generation":
            request_data["task"] = "generate_tests_from_jira"
        elif request_type == "pdf_processing":
            request_data["task"] = "process_pdf_document"
        elif request_type == "script_generation":
            request_data["task"] = "generate_automation_script"
        elif request_type == "test_generation":
            request_data["task"] = "generate_test_suite"
        elif request_type == "code_analysis":
            request_data["task"] = "analyze_code_changes"
        else:
            request_data["task"] = "general_assistance"
        
        return json.dumps(request_data, indent=2)

async def main():
    """Main entry point for the chatbot interface."""
    print("🤖 Enhanced Agent Engine - Chatbot Interface")
    print("=" * 50)
    
    # Initialize the orchestrator
    orchestrator = ChatbotOrchestrator()
    
    # Create a session for the demo user
    user_id = "demo_user"
    session_id = await orchestrator.create_session(user_id)
    print(f"Created session: {session_id}")
    
    print("\nAvailable commands:")
    print("- Git analysis: 'Analyze git repository [URL]'")
    print("- JIRA integration: 'Generate tests from JIRA ticket [URL]'")
    print("- PDF processing: 'Process PDF document [path/url]'")
    print("- Script generation: 'Generate automation script for [task]'")
    print("- Code analysis: 'Analyze code changes in [file/repo]'")
    print("- Test generation: 'Generate tests for [code/file]'")
    print("- Type 'exit' to quit")
    print("\n" + "=" * 50)
    
    # Interactive chat loop
    while True:
        try:
            user_input = input("\n🧑‍💻 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("🤖 Agent Engine: Processing your request...")
            
            # Process the message through the agent system
            response = await orchestrator.process_user_message(user_id, user_input)
            
            print(f"🤖 Agent Engine: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the chatbot interface
    asyncio.run(main())
