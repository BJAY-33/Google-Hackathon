"""
Enhanced Agent Engine - Web Interface Integration
Integrates with ADK web interface for browser-based chatbot experience
"""

import asyncio
import json
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.web import WebRunner
from dotenv import load_dotenv
import os

# Import the enhanced coordinator with all subagents
from agents.enhanced_coordinator import enhanced_root_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedWebAgent:
    """Web-enabled Enhanced Agent Engine for browser-based interaction."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="enhanced_agent_engine_web",
            agent=enhanced_root_agent,
            session_service=self.session_service
        )
        logger.info("Enhanced Agent Engine Web Interface initialized")
    
    async def start_web_interface(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the web interface using ADK WebRunner."""
        try:
            logger.info(f"Starting Enhanced Agent Engine web interface on {host}:{port}")
            
            # Create web runner with our enhanced agent
            web_runner = WebRunner(
                runner=self.runner,
                host=host,
                port=port,
                title="Enhanced Agent Engine",
                description="Multi-agent system for Git analysis, JIRA integration, PDF processing, and test generation"
            )
            
            # Start the web server
            await web_runner.start()
            logger.info("Web interface started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            raise

async def main():
    """Main entry point for the web interface."""
    print("🚀 Enhanced Agent Engine - Web Interface")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google API key in the .env file")
        return
    
    # Get configuration from environment
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8080"))
    
    print(f"🌐 Starting web interface on http://{host}:{port}")
    print("📋 Available capabilities:")
    print("   • Git repository analysis and code change detection")
    print("   • JIRA ticket processing and test case generation")
    print("   • PDF document analysis and requirement extraction")
    print("   • Automation script generation (CI/CD, deployment)")
    print("   • Comprehensive test suite generation")
    print("   • Strategic planning and risk assessment")
    print("\n" + "=" * 50)
    
    # Initialize and start the web agent
    try:
        web_agent = EnhancedWebAgent()
        await web_agent.start_web_interface(host=host, port=port)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Enhanced Agent Engine...")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        logger.error(f"Web interface error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
