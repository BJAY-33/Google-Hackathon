"""
Enhanced Coordinator - Orchestrates all subagents
Extends TestMozart architecture with additional specialized agents
"""

import json
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# Import existing TestMozart agents
from .code_analyzer import code_analyzer_agent
from .test_case_designer import test_case_designer_agent
from .test_implementer import test_implementer_agent
from .test_runner import test_runner_agent
from .debugger_and_refiner import debugger_and_refiner_agent

# Import new specialized subagents
from .git_analyzer_agent import git_analyzer_agent
from .jira_integration_agent import jira_integration_agent
from .pdf_processor_agent import pdf_processor_agent
from .script_generator_agent import script_generator_agent
from .strategy_planner_agent import strategy_planner_agent

# Import tools
from tools.workflow_tools import exit_loop
from tools.git_tools import clone_repository, analyze_git_changes
from tools.jira_tools import fetch_jira_ticket, extract_requirements
from tools.pdf_tools import extract_pdf_content, analyze_document
from tools.script_tools import generate_automation_script

# --- Enhanced State Initialization ---

def initialize_enhanced_state(callback_context: CallbackContext):
    """Enhanced state initialization that handles multiple request types."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        try:
            request_data = json.loads(user_content.parts[0].text)
            
            # Store the original request
            callback_context.state['user_message'] = request_data.get('user_message', '')
            callback_context.state['request_type'] = request_data.get('request_type', 'general_chat')
            callback_context.state['task'] = request_data.get('task', 'general_assistance')
            
            # Initialize common state variables
            callback_context.state['source_code'] = ''
            callback_context.state['language'] = 'python'
            callback_context.state['test_results'] = {"status": "UNKNOWN"}
            callback_context.state['analysis_complete'] = False
            
            # Initialize task-specific state
            request_type = request_data.get('request_type', '')
            
            if request_type in ['git_analysis', 'git_pull']:
                callback_context.state['repository_url'] = ''
                callback_context.state['git_changes'] = []
                callback_context.state['affected_files'] = []
            
            elif request_type in ['jira_analysis', 'jira_test_generation']:
                callback_context.state['jira_url'] = ''
                callback_context.state['jira_requirements'] = {}
                callback_context.state['test_scenarios'] = []
            
            elif request_type == 'pdf_processing':
                callback_context.state['pdf_content'] = ''
                callback_context.state['document_analysis'] = {}
            
            elif request_type == 'script_generation':
                callback_context.state['script_requirements'] = {}
                callback_context.state['generated_script'] = ''
                
        except (json.JSONDecodeError, AttributeError):
            # Fallback for simple text input
            callback_context.state['user_message'] = user_content.parts[0].text if user_content.parts else ''
            callback_context.state['request_type'] = 'general_chat'
            callback_context.state['task'] = 'general_assistance'

# --- Request Router Agent ---

request_router_agent = LlmAgent(
    name="RequestRouter",
    description="Routes user requests to appropriate specialized subagents based on request type.",
    model="gemini-2.5-pro",
    instruction="""
    You are the request router for the Enhanced Agent Engine. Your job is to analyze the user's request and determine which specialized workflow to execute.

    Available workflows:
    1. GIT_ANALYSIS: For analyzing git repositories, code changes, commits
    2. JIRA_INTEGRATION: For processing JIRA tickets and generating test cases
    3. PDF_PROCESSING: For extracting and analyzing PDF documents
    4. SCRIPT_GENERATION: For generating automation scripts
    5. TEST_GENERATION: For generating test suites (original TestMozart functionality)
    6. CODE_ANALYSIS: For analyzing code without test generation
    7. GENERAL_CHAT: For general questions and assistance

    Based on the request type: {request_type} and task: {task}, set the workflow_type in your response.
    
    Your response should be a JSON object with:
    {
        "workflow_type": "selected_workflow",
        "reasoning": "why this workflow was selected",
        "next_steps": "what the system will do next"
    }
    """,
    output_key="routing_decision"
)

# --- Specialized Workflow Agents ---

# Git Analysis Workflow
git_workflow = SequentialAgent(
    name="GitWorkflow",
    description="Handles git repository analysis and code change processing.",
    sub_agents=[
        git_analyzer_agent,
        code_analyzer_agent,
        strategy_planner_agent
    ]
)

# JIRA Integration Workflow  
jira_workflow = SequentialAgent(
    name="JiraWorkflow",
    description="Processes JIRA tickets and generates test cases.",
    sub_agents=[
        jira_integration_agent,
        test_case_designer_agent,
        test_implementer_agent
    ]
)

# PDF Processing Workflow
pdf_workflow = SequentialAgent(
    name="PdfWorkflow", 
    description="Extracts and analyzes PDF documents.",
    sub_agents=[
        pdf_processor_agent,
        strategy_planner_agent
    ]
)

# Script Generation Workflow
script_workflow = SequentialAgent(
    name="ScriptWorkflow",
    description="Generates automation scripts based on requirements.",
    sub_agents=[
        script_generator_agent,
        test_implementer_agent  # For testing the generated scripts
    ]
)

# Original TestMozart Workflow (Enhanced)
test_generation_workflow = SequentialAgent(
    name="TestGenerationWorkflow",
    description="Original TestMozart functionality for test suite generation.",
    sub_agents=[
        code_analyzer_agent,
        test_case_designer_agent,
        test_implementer_agent,
        LoopAgent(
            name="TestRefinementLoop",
            description="Iterative test refinement and debugging.",
            sub_agents=[test_runner_agent, debugger_and_refiner_agent],
            max_iterations=3
        )
    ]
)

# --- Workflow Dispatcher ---

workflow_dispatcher_agent = LlmAgent(
    name="WorkflowDispatcher",
    description="Dispatches requests to the appropriate workflow based on routing decision.",
    model="gemini-2.5-flash",
    instruction="""
    You are the workflow dispatcher. Based on the routing_decision from the previous step, 
    determine which specialized workflow should handle this request.
    
    Available workflows:
    - git_workflow: For git and repository analysis
    - jira_workflow: For JIRA ticket processing  
    - pdf_workflow: For PDF document processing
    - script_workflow: For script generation
    - test_generation_workflow: For test suite generation
    
    Your response should indicate which workflow to execute next.
    Routing decision: {routing_decision}
    """,
    output_key="selected_workflow"
)

# --- Result Summarizer (Enhanced) ---

enhanced_result_summarizer = LlmAgent(
    name="EnhancedResultSummarizer",
    description="Summarizes results from any workflow and formats them for the user.",
    model="gemini-2.5-pro",
    instruction="""
    You are the enhanced result summarizer for the Agent Engine. Your job is to provide a clear, 
    comprehensive summary of what was accomplished based on the workflow that was executed.

    Available state variables:
    - {user_message}: Original user request
    - {request_type}: Type of request processed
    - {task}: Specific task that was executed
    - {routing_decision}: How the request was routed
    - {selected_workflow}: Which workflow was used
    
    Workflow-specific variables:
    - {source_code}: For code analysis tasks
    - {generated_test_code}: For test generation
    - {test_results}: For test execution results
    - {git_changes}: For git analysis
    - {jira_requirements}: For JIRA processing
    - {pdf_content}: For PDF processing
    - {generated_script}: For script generation
    
    Provide a helpful summary that:
    1. Acknowledges what the user requested
    2. Explains what was accomplished
    3. Presents the key results or outputs
    4. Suggests next steps if appropriate
    
    Format your response in a user-friendly way with clear sections and bullet points where helpful.
    """
)

# --- Enhanced Root Agent ---

enhanced_root_agent = SequentialAgent(
    name="EnhancedCoordinatorAgent",
    description="Enhanced orchestrator that handles multiple types of requests through specialized workflows.",
    sub_agents=[
        request_router_agent,
        workflow_dispatcher_agent,
        # Note: The actual workflow execution will be handled dynamically
        # based on the dispatcher's decision
        enhanced_result_summarizer
    ],
    before_agent_callback=initialize_enhanced_state
)

# --- Dynamic Workflow Execution ---

async def execute_selected_workflow(callback_context: CallbackContext):
    """Execute the workflow selected by the dispatcher."""
    selected_workflow = callback_context.state.get('selected_workflow', '')
    
    # Map workflow names to actual workflow agents
    workflow_map = {
        'git_workflow': git_workflow,
        'jira_workflow': jira_workflow, 
        'pdf_workflow': pdf_workflow,
        'script_workflow': script_workflow,
        'test_generation_workflow': test_generation_workflow
    }
    
    if selected_workflow in workflow_map:
        workflow_agent = workflow_map[selected_workflow]
        # Execute the selected workflow
        # Note: This would need to be integrated with the ADK's execution model
        return workflow_agent
    
    return None
