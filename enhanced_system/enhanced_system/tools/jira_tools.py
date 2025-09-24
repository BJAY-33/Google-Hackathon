"""
JIRA Tools - Tools for JIRA integration and ticket processing
"""

import re
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import json
from urllib.parse import urlparse

class JiraTicket(BaseModel):
    """Model for JIRA ticket information."""
    ticket_id: str
    title: str
    description: str = ""
    status: str = ""
    priority: str = ""
    assignee: str = ""
    reporter: str = ""
    acceptance_criteria: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)

class TestScenario(BaseModel):
    """Model for test scenarios generated from JIRA tickets."""
    scenario_id: str
    title: str
    description: str
    steps: List[str]
    expected_result: str
    priority: str = "Medium"
    test_type: str = "Functional"  # Functional, Integration, E2E, etc.

def extract_jira_url_info(text: str) -> Dict[str, Any]:
    """
    Extract JIRA URL information from text.
    
    Args:
        text: Text that may contain JIRA URLs or ticket IDs
        
    Returns:
        Dictionary with extracted JIRA information
    """
    # Pattern for JIRA URLs
    jira_url_pattern = r'https?://([^/]+)\.atlassian\.net/browse/([A-Z]+-\d+)'
    # Pattern for standalone ticket IDs
    ticket_id_pattern = r'\b([A-Z]+-\d+)\b'
    
    jira_info = {
        "jira_urls": [],
        "ticket_ids": [],
        "base_url": ""
    }
    
    # Find JIRA URLs
    url_matches = re.findall(jira_url_pattern, text, re.IGNORECASE)
    for match in url_matches:
        domain = match[0]
        ticket_id = match[1]
        full_url = f"https://{domain}.atlassian.net/browse/{ticket_id}"
        base_url = f"https://{domain}.atlassian.net"
        
        jira_info["jira_urls"].append(full_url)
        jira_info["ticket_ids"].append(ticket_id)
        jira_info["base_url"] = base_url
    
    # Find standalone ticket IDs if no URLs found
    if not jira_info["ticket_ids"]:
        ticket_matches = re.findall(ticket_id_pattern, text)
        jira_info["ticket_ids"] = list(set(ticket_matches))  # Remove duplicates
    
    return jira_info

def fetch_jira_ticket(ticket_url_or_id: str, jira_base_url: str = "", username: str = "", api_token: str = "") -> Dict[str, Any]:
    """
    Fetch JIRA ticket information.
    
    Note: This is a mock implementation. In a real system, you would:
    1. Use proper JIRA API authentication
    2. Make actual API calls to JIRA
    3. Handle various JIRA configurations and custom fields
    
    Args:
        ticket_url_or_id: JIRA ticket URL or ID
        jira_base_url: Base URL for JIRA instance
        username: JIRA username for authentication
        api_token: JIRA API token for authentication
        
    Returns:
        Dictionary with ticket information
    """
    try:
        # Extract ticket ID from URL if needed
        if ticket_url_or_id.startswith('http'):
            ticket_match = re.search(r'/browse/([A-Z]+-\d+)', ticket_url_or_id)
            ticket_id = ticket_match.group(1) if ticket_match else ""
            
            # Extract base URL if not provided
            if not jira_base_url:
                parsed_url = urlparse(ticket_url_or_id)
                jira_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            ticket_id = ticket_url_or_id
        
        if not ticket_id:
            return {
                "status": "error",
                "message": "Invalid ticket URL or ID",
                "ticket": None
            }
        
        # Mock JIRA ticket data (replace with actual JIRA API call)
        mock_ticket_data = {
            "PROJ-123": {
                "title": "Implement user authentication system",
                "description": "As a user, I want to be able to log in to the system securely so that I can access my personal dashboard.",
                "status": "In Progress",
                "priority": "High",
                "assignee": "john.doe@company.com",
                "reporter": "product.manager@company.com",
                "acceptance_criteria": [
                    "User can log in with valid email and password",
                    "System displays error message for invalid credentials",
                    "User session expires after 30 minutes of inactivity",
                    "Password must meet complexity requirements",
                    "Account locks after 5 failed login attempts"
                ],
                "labels": ["authentication", "security", "user-management"],
                "components": ["Frontend", "Backend", "Database"]
            },
            "STORY-456": {
                "title": "Add shopping cart functionality",
                "description": "Implement shopping cart where users can add, remove, and modify items before checkout.",
                "status": "To Do",
                "priority": "Medium",
                "assignee": "jane.smith@company.com",
                "reporter": "business.analyst@company.com",
                "acceptance_criteria": [
                    "Users can add items to cart from product pages",
                    "Users can view cart contents and total price",
                    "Users can modify quantities or remove items",
                    "Cart persists across browser sessions",
                    "Cart shows real-time inventory availability"
                ],
                "labels": ["e-commerce", "shopping", "frontend"],
                "components": ["Frontend", "API", "Database"]
            }
        }
        
        # Simulate API call delay and potential issues
        if ticket_id in mock_ticket_data:
            ticket_data = mock_ticket_data[ticket_id]
            
            return {
                "status": "success",
                "message": f"Successfully fetched ticket {ticket_id}",
                "ticket": {
                    "ticket_id": ticket_id,
                    "title": ticket_data["title"],
                    "description": ticket_data["description"],
                    "status": ticket_data["status"],
                    "priority": ticket_data["priority"],
                    "assignee": ticket_data["assignee"],
                    "reporter": ticket_data["reporter"],
                    "acceptance_criteria": ticket_data["acceptance_criteria"],
                    "labels": ticket_data["labels"],
                    "components": ticket_data["components"]
                }
            }
        else:
            # Simulate a generic ticket for unknown IDs
            return {
                "status": "success",
                "message": f"Successfully fetched ticket {ticket_id}",
                "ticket": {
                    "ticket_id": ticket_id,
                    "title": f"Generic ticket {ticket_id}",
                    "description": "This is a mock ticket for demonstration purposes.",
                    "status": "Open",
                    "priority": "Medium",
                    "assignee": "unassigned",
                    "reporter": "system",
                    "acceptance_criteria": [
                        "Implement the required functionality",
                        "Add appropriate error handling",
                        "Include unit tests",
                        "Update documentation"
                    ],
                    "labels": ["feature", "development"],
                    "components": ["Backend"]
                }
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching JIRA ticket: {str(e)}",
            "ticket": None
        }

def extract_requirements(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and structure requirements from JIRA ticket data.
    
    Args:
        ticket_data: JIRA ticket information
        
    Returns:
        Dictionary with structured requirements
    """
    try:
        if not ticket_data or "ticket" not in ticket_data:
            return {
                "status": "error",
                "message": "Invalid ticket data provided",
                "requirements": {}
            }
        
        ticket = ticket_data["ticket"]
        
        # Extract functional requirements from description and acceptance criteria
        functional_requirements = []
        
        # Parse acceptance criteria
        for criteria in ticket.get("acceptance_criteria", []):
            functional_requirements.append({
                "id": f"REQ-{len(functional_requirements) + 1}",
                "description": criteria,
                "type": "functional",
                "priority": ticket.get("priority", "Medium"),
                "testable": True
            })
        
        # Extract additional requirements from description
        description = ticket.get("description", "")
        
        # Look for common requirement patterns in description
        requirement_patterns = [
            r"must\s+([^.]+)",
            r"should\s+([^.]+)",
            r"shall\s+([^.]+)",
            r"will\s+([^.]+)"
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:  # Filter out very short matches
                    functional_requirements.append({
                        "id": f"REQ-{len(functional_requirements) + 1}",
                        "description": match.strip(),
                        "type": "functional",
                        "priority": ticket.get("priority", "Medium"),
                        "testable": True
                    })
        
        # Identify non-functional requirements based on keywords
        non_functional_requirements = []
        nfr_keywords = {
            "performance": ["performance", "speed", "fast", "response time", "latency"],
            "security": ["security", "secure", "authentication", "authorization", "encrypt"],
            "usability": ["usability", "user-friendly", "intuitive", "easy"],
            "reliability": ["reliable", "availability", "uptime", "stable"],
            "scalability": ["scalable", "scale", "concurrent", "load"]
        }
        
        description_lower = description.lower()
        for nfr_type, keywords in nfr_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                non_functional_requirements.append({
                    "id": f"NFR-{len(non_functional_requirements) + 1}",
                    "type": nfr_type,
                    "description": f"{nfr_type.title()} requirement identified from ticket description",
                    "priority": "Medium",
                    "testable": True
                })
        
        # Identify integration points from components
        integration_points = []
        components = ticket.get("components", [])
        if len(components) > 1:
            integration_points.append({
                "components": components,
                "description": f"Integration between {', '.join(components)} components",
                "test_type": "integration"
            })
        
        requirements = {
            "ticket_id": ticket.get("ticket_id", ""),
            "functional_requirements": functional_requirements,
            "non_functional_requirements": non_functional_requirements,
            "integration_points": integration_points,
            "business_rules": [],  # Could be extracted from description with more sophisticated parsing
            "constraints": [],
            "assumptions": []
        }
        
        return {
            "status": "success",
            "message": f"Extracted {len(functional_requirements)} functional and {len(non_functional_requirements)} non-functional requirements",
            "requirements": requirements
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error extracting requirements: {str(e)}",
            "requirements": {}
        }

def generate_test_scenarios_from_jira(requirements_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive test scenarios from extracted requirements.
    
    Args:
        requirements_data: Structured requirements from extract_requirements
        
    Returns:
        Dictionary with generated test scenarios
    """
    try:
        if not requirements_data or "requirements" not in requirements_data:
            return {
                "status": "error",
                "message": "Invalid requirements data provided",
                "test_scenarios": []
            }
        
        requirements = requirements_data["requirements"]
        test_scenarios = []
        scenario_counter = 1
        
        # Generate positive test scenarios from functional requirements
        for req in requirements.get("functional_requirements", []):
            # Positive scenario
            positive_scenario = {
                "scenario_id": f"TS-{scenario_counter:03d}",
                "title": f"Verify {req['description'][:50]}...",
                "description": f"Test that the system correctly implements: {req['description']}",
                "steps": [
                    "Navigate to the relevant feature/page",
                    "Perform the required action as described in the requirement",
                    "Verify the expected behavior occurs"
                ],
                "expected_result": req['description'],
                "priority": req.get('priority', 'Medium'),
                "test_type": "Functional",
                "requirement_id": req['id']
            }
            test_scenarios.append(positive_scenario)
            scenario_counter += 1
            
            # Negative scenario
            negative_scenario = {
                "scenario_id": f"TS-{scenario_counter:03d}",
                "title": f"Verify error handling for {req['description'][:50]}...",
                "description": f"Test error handling and validation for: {req['description']}",
                "steps": [
                    "Navigate to the relevant feature/page",
                    "Attempt invalid or boundary condition inputs",
                    "Verify appropriate error handling occurs"
                ],
                "expected_result": "System displays appropriate error message and handles invalid input gracefully",
                "priority": req.get('priority', 'Medium'),
                "test_type": "Negative",
                "requirement_id": req['id']
            }
            test_scenarios.append(negative_scenario)
            scenario_counter += 1
        
        # Generate test scenarios for non-functional requirements
        for nfr in requirements.get("non_functional_requirements", []):
            nfr_scenario = {
                "scenario_id": f"TS-{scenario_counter:03d}",
                "title": f"Verify {nfr['type']} requirement",
                "description": f"Test {nfr['type']} aspect: {nfr['description']}",
                "steps": [
                    f"Set up {nfr['type']} testing environment",
                    f"Execute {nfr['type']} test procedures",
                    f"Measure and verify {nfr['type']} metrics"
                ],
                "expected_result": f"System meets {nfr['type']} requirements as specified",
                "priority": nfr.get('priority', 'Medium'),
                "test_type": nfr['type'].title(),
                "requirement_id": nfr['id']
            }
            test_scenarios.append(nfr_scenario)
            scenario_counter += 1
        
        # Generate integration test scenarios
        for integration in requirements.get("integration_points", []):
            integration_scenario = {
                "scenario_id": f"TS-{scenario_counter:03d}",
                "title": f"Verify integration between {', '.join(integration['components'])}",
                "description": integration['description'],
                "steps": [
                    "Set up test data in all involved components",
                    "Execute end-to-end workflow across components",
                    "Verify data flow and communication between components"
                ],
                "expected_result": "All components integrate correctly and data flows as expected",
                "priority": "High",
                "test_type": "Integration",
                "requirement_id": "INTEGRATION-001"
            }
            test_scenarios.append(integration_scenario)
            scenario_counter += 1
        
        # Generate edge case and boundary test scenarios
        edge_case_scenario = {
            "scenario_id": f"TS-{scenario_counter:03d}",
            "title": "Verify system behavior with edge cases and boundary conditions",
            "description": "Test system behavior with extreme values, empty inputs, and boundary conditions",
            "steps": [
                "Identify boundary values for all input fields",
                "Test with minimum and maximum allowed values",
                "Test with values just outside the allowed range",
                "Test with empty, null, and special character inputs"
            ],
            "expected_result": "System handles all edge cases gracefully with appropriate validation and error messages",
            "priority": "Medium",
            "test_type": "Boundary",
            "requirement_id": "EDGE-001"
        }
        test_scenarios.append(edge_case_scenario)
        
        return {
            "status": "success",
            "message": f"Generated {len(test_scenarios)} test scenarios",
            "test_scenarios": test_scenarios,
            "summary": {
                "total_scenarios": len(test_scenarios),
                "functional_tests": len([s for s in test_scenarios if s['test_type'] == 'Functional']),
                "negative_tests": len([s for s in test_scenarios if s['test_type'] == 'Negative']),
                "integration_tests": len([s for s in test_scenarios if s['test_type'] == 'Integration']),
                "nfr_tests": len([s for s in test_scenarios if s['test_type'] in ['Performance', 'Security', 'Usability', 'Reliability', 'Scalability']])
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating test scenarios: {str(e)}",
            "test_scenarios": []
        }
