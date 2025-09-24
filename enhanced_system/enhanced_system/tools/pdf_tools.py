"""
PDF Tools - Tools for PDF document processing and analysis
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re

# Note: In a real implementation, you would use libraries like:
# - PyPDF2 or pdfplumber for PDF text extraction
# - pdf2image for converting PDFs to images
# - pytesseract for OCR if needed
# For this demo, we'll create mock implementations

class DocumentSection(BaseModel):
    """Model for document section information."""
    section_id: str
    title: str
    content: str
    page_number: int = 1
    section_type: str = "content"  # content, table, image, etc.

class PDFAnalysisResult(BaseModel):
    """Model for PDF analysis results."""
    document_title: str = ""
    total_pages: int = 0
    sections: List[DocumentSection] = Field(default_factory=list)
    extracted_requirements: List[str] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""

def extract_pdf_content(pdf_path_or_url: str) -> Dict[str, Any]:
    """
    Extract text and structured content from PDF files.
    
    Args:
        pdf_path_or_url: Path to PDF file or URL
        
    Returns:
        Dictionary with extracted PDF content
    """
    try:
        # Check if it's a URL or local file path
        if pdf_path_or_url.startswith(('http://', 'https://')):
            # In a real implementation, you would download the PDF first
            return {
                "status": "error",
                "message": "PDF URL download not implemented in this demo",
                "content": ""
            }
        
        if not os.path.exists(pdf_path_or_url):
            return {
                "status": "error",
                "message": f"PDF file not found: {pdf_path_or_url}",
                "content": ""
            }
        
        # Mock PDF content extraction (replace with actual PDF processing)
        # In a real implementation, you would use PyPDF2, pdfplumber, or similar
        mock_pdf_content = {
            "user_manual.pdf": {
                "title": "User Authentication System - Requirements Document",
                "total_pages": 15,
                "content": """
                1. INTRODUCTION
                This document outlines the requirements for implementing a secure user authentication system.
                
                2. FUNCTIONAL REQUIREMENTS
                2.1 User Registration
                - Users must be able to create accounts with email and password
                - Email validation is required before account activation
                - Password must meet complexity requirements (8+ characters, mixed case, numbers, symbols)
                
                2.2 User Login
                - Users must authenticate with email and password
                - System must support "Remember Me" functionality
                - Failed login attempts must be tracked and limited
                
                2.3 Password Management
                - Users must be able to reset forgotten passwords
                - Password reset must use secure email verification
                - Users must be able to change passwords when logged in
                
                3. NON-FUNCTIONAL REQUIREMENTS
                3.1 Security
                - All passwords must be hashed using bcrypt or similar
                - Session tokens must expire after 30 minutes of inactivity
                - All authentication endpoints must use HTTPS
                
                3.2 Performance
                - Login response time must be under 2 seconds
                - System must support 1000+ concurrent users
                
                4. ACCEPTANCE CRITERIA
                - User can successfully register with valid information
                - User receives email confirmation after registration
                - User can log in with valid credentials
                - User cannot log in with invalid credentials
                - User account locks after 5 failed attempts
                - User can reset password using email link
                """,
                "sections": [
                    {
                        "section_id": "1",
                        "title": "Introduction",
                        "content": "This document outlines the requirements for implementing a secure user authentication system.",
                        "page_number": 1,
                        "section_type": "content"
                    },
                    {
                        "section_id": "2",
                        "title": "Functional Requirements",
                        "content": "User Registration, User Login, Password Management requirements...",
                        "page_number": 2,
                        "section_type": "requirements"
                    },
                    {
                        "section_id": "3",
                        "title": "Non-Functional Requirements", 
                        "content": "Security and Performance requirements...",
                        "page_number": 8,
                        "section_type": "requirements"
                    },
                    {
                        "section_id": "4",
                        "title": "Acceptance Criteria",
                        "content": "Detailed acceptance criteria for all features...",
                        "page_number": 12,
                        "section_type": "criteria"
                    }
                ]
            },
            "api_spec.pdf": {
                "title": "REST API Specification v2.1",
                "total_pages": 25,
                "content": """
                API SPECIFICATION
                
                1. AUTHENTICATION ENDPOINTS
                POST /api/auth/login
                - Request: {"email": "string", "password": "string"}
                - Response: {"token": "string", "expires": "datetime"}
                
                POST /api/auth/register
                - Request: {"email": "string", "password": "string", "firstName": "string", "lastName": "string"}
                - Response: {"userId": "string", "message": "string"}
                
                2. USER MANAGEMENT ENDPOINTS
                GET /api/users/profile
                - Headers: Authorization: Bearer <token>
                - Response: {"userId": "string", "email": "string", "profile": {}}
                
                PUT /api/users/profile
                - Headers: Authorization: Bearer <token>
                - Request: {"firstName": "string", "lastName": "string", "phone": "string"}
                - Response: {"success": "boolean", "message": "string"}
                
                3. ERROR RESPONSES
                - 400 Bad Request: Invalid input parameters
                - 401 Unauthorized: Invalid or expired token
                - 403 Forbidden: Insufficient permissions
                - 404 Not Found: Resource not found
                - 500 Internal Server Error: Server error
                """,
                "sections": [
                    {
                        "section_id": "1",
                        "title": "Authentication Endpoints",
                        "content": "POST /api/auth/login, POST /api/auth/register",
                        "page_number": 3,
                        "section_type": "api_spec"
                    },
                    {
                        "section_id": "2", 
                        "title": "User Management Endpoints",
                        "content": "GET /api/users/profile, PUT /api/users/profile",
                        "page_number": 8,
                        "section_type": "api_spec"
                    }
                ]
            }
        }
        
        # Determine which mock content to use based on filename
        filename = os.path.basename(pdf_path_or_url).lower()
        
        if "user" in filename or "manual" in filename or "requirements" in filename:
            content_data = mock_pdf_content["user_manual.pdf"]
        elif "api" in filename or "spec" in filename:
            content_data = mock_pdf_content["api_spec.pdf"]
        else:
            # Generic PDF content
            content_data = {
                "title": f"Document: {os.path.basename(pdf_path_or_url)}",
                "total_pages": 5,
                "content": "This is a sample PDF document with generic content for demonstration purposes.",
                "sections": [
                    {
                        "section_id": "1",
                        "title": "Generic Section",
                        "content": "Sample content from PDF document",
                        "page_number": 1,
                        "section_type": "content"
                    }
                ]
            }
        
        return {
            "status": "success",
            "message": f"Successfully extracted content from {pdf_path_or_url}",
            "document_title": content_data["title"],
            "total_pages": content_data["total_pages"],
            "full_content": content_data["content"],
            "sections": content_data["sections"],
            "file_path": pdf_path_or_url
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error extracting PDF content: {str(e)}",
            "content": ""
        }

def analyze_document_structure(pdf_content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the structure and organization of a PDF document.
    
    Args:
        pdf_content_data: Content data from extract_pdf_content
        
    Returns:
        Dictionary with document structure analysis
    """
    try:
        if not pdf_content_data or pdf_content_data.get("status") != "success":
            return {
                "status": "error",
                "message": "Invalid PDF content data provided",
                "analysis": {}
            }
        
        full_content = pdf_content_data.get("full_content", "")
        sections = pdf_content_data.get("sections", [])
        
        # Analyze document structure
        structure_analysis = {
            "document_type": "unknown",
            "has_requirements": False,
            "has_api_specs": False,
            "has_test_cases": False,
            "has_acceptance_criteria": False,
            "sections_count": len(sections),
            "key_sections": [],
            "requirements_sections": [],
            "testable_items": []
        }
        
        # Determine document type based on content
        content_lower = full_content.lower()
        
        if any(keyword in content_lower for keyword in ["requirement", "specification", "spec"]):
            structure_analysis["document_type"] = "requirements"
            structure_analysis["has_requirements"] = True
        
        if any(keyword in content_lower for keyword in ["api", "endpoint", "rest", "post", "get", "put", "delete"]):
            structure_analysis["document_type"] = "api_specification"
            structure_analysis["has_api_specs"] = True
        
        if any(keyword in content_lower for keyword in ["test", "testing", "test case", "scenario"]):
            structure_analysis["has_test_cases"] = True
        
        if any(keyword in content_lower for keyword in ["acceptance criteria", "acceptance", "criteria"]):
            structure_analysis["has_acceptance_criteria"] = True
        
        # Analyze sections
        for section in sections:
            section_content_lower = section.get("content", "").lower()
            section_title_lower = section.get("title", "").lower()
            
            # Identify key sections
            if any(keyword in section_title_lower for keyword in ["requirement", "functional", "non-functional"]):
                structure_analysis["key_sections"].append(section["title"])
                structure_analysis["requirements_sections"].append({
                    "section_id": section["section_id"],
                    "title": section["title"],
                    "type": "requirements",
                    "page": section.get("page_number", 1)
                })
            
            elif any(keyword in section_title_lower for keyword in ["api", "endpoint", "specification"]):
                structure_analysis["key_sections"].append(section["title"])
                structure_analysis["requirements_sections"].append({
                    "section_id": section["section_id"],
                    "title": section["title"],
                    "type": "api_spec",
                    "page": section.get("page_number", 1)
                })
            
            elif any(keyword in section_title_lower for keyword in ["acceptance", "criteria", "test"]):
                structure_analysis["key_sections"].append(section["title"])
                structure_analysis["requirements_sections"].append({
                    "section_id": section["section_id"],
                    "title": section["title"],
                    "type": "acceptance_criteria",
                    "page": section.get("page_number", 1)
                })
        
        # Extract testable items
        testable_patterns = [
            r"user\s+(?:must|should|can|will)\s+([^.]+)",
            r"system\s+(?:must|should|will)\s+([^.]+)",
            r"(?:must|should)\s+([^.]+)",
            r"acceptance\s+criteria[:\s]*([^.]+)"
        ]
        
        for pattern in testable_patterns:
            matches = re.findall(pattern, full_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 10:  # Filter short matches
                    structure_analysis["testable_items"].append({
                        "description": match.strip(),
                        "type": "functional_requirement",
                        "testable": True
                    })
        
        return {
            "status": "success",
            "message": f"Analyzed document structure with {len(sections)} sections",
            "analysis": structure_analysis,
            "recommendations": [
                "Extract requirements for test case generation" if structure_analysis["has_requirements"] else "No clear requirements found",
                "Generate API test cases" if structure_analysis["has_api_specs"] else "No API specifications found",
                "Validate acceptance criteria coverage" if structure_analysis["has_acceptance_criteria"] else "No acceptance criteria found"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing document structure: {str(e)}",
            "analysis": {}
        }

def generate_test_cases_from_pdf(pdf_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test cases from PDF document analysis.
    
    Args:
        pdf_analysis_data: Analysis data from analyze_document_structure
        
    Returns:
        Dictionary with generated test cases
    """
    try:
        if not pdf_analysis_data or pdf_analysis_data.get("status") != "success":
            return {
                "status": "error",
                "message": "Invalid PDF analysis data provided",
                "test_cases": []
            }
        
        analysis = pdf_analysis_data.get("analysis", {})
        testable_items = analysis.get("testable_items", [])
        
        test_cases = []
        test_case_counter = 1
        
        # Generate test cases from testable items
        for item in testable_items:
            # Positive test case
            positive_test = {
                "test_case_id": f"TC-PDF-{test_case_counter:03d}",
                "title": f"Verify: {item['description'][:50]}...",
                "description": f"Test that the system correctly implements: {item['description']}",
                "preconditions": ["System is properly configured", "User has appropriate permissions"],
                "test_steps": [
                    "Navigate to the relevant functionality",
                    "Execute the required action as described",
                    "Verify the expected behavior occurs"
                ],
                "expected_result": item['description'],
                "test_type": "Functional",
                "priority": "Medium",
                "source": "PDF Requirements"
            }
            test_cases.append(positive_test)
            test_case_counter += 1
            
            # Negative test case
            negative_test = {
                "test_case_id": f"TC-PDF-{test_case_counter:03d}",
                "title": f"Verify error handling: {item['description'][:50]}...",
                "description": f"Test error handling for: {item['description']}",
                "preconditions": ["System is properly configured"],
                "test_steps": [
                    "Navigate to the relevant functionality",
                    "Attempt invalid or boundary condition inputs",
                    "Verify appropriate error handling"
                ],
                "expected_result": "System handles invalid input gracefully with appropriate error messages",
                "test_type": "Negative",
                "priority": "Low",
                "source": "PDF Requirements"
            }
            test_cases.append(negative_test)
            test_case_counter += 1
        
        # Generate specific test cases based on document type
        doc_type = analysis.get("document_type", "unknown")
        
        if doc_type == "api_specification":
            # Generate API-specific test cases
            api_test = {
                "test_case_id": f"TC-PDF-{test_case_counter:03d}",
                "title": "API Endpoint Validation",
                "description": "Validate all API endpoints defined in the specification",
                "preconditions": ["API server is running", "Authentication tokens are available"],
                "test_steps": [
                    "Send requests to all defined endpoints",
                    "Verify response formats match specification",
                    "Test error scenarios and status codes"
                ],
                "expected_result": "All API endpoints respond according to specification",
                "test_type": "API",
                "priority": "High",
                "source": "PDF API Specification"
            }
            test_cases.append(api_test)
            test_case_counter += 1
        
        elif doc_type == "requirements":
            # Generate requirements-based test cases
            requirements_test = {
                "test_case_id": f"TC-PDF-{test_case_counter:03d}",
                "title": "Requirements Coverage Validation",
                "description": "Validate that all requirements from the PDF are properly implemented",
                "preconditions": ["System is deployed", "Test environment is configured"],
                "test_steps": [
                    "Review all functional requirements",
                    "Execute test scenarios for each requirement",
                    "Verify non-functional requirements where applicable"
                ],
                "expected_result": "All requirements are properly implemented and testable",
                "test_type": "Requirements",
                "priority": "High",
                "source": "PDF Requirements Document"
            }
            test_cases.append(requirements_test)
        
        # Generate integration test cases if multiple sections are present
        if analysis.get("sections_count", 0) > 3:
            integration_test = {
                "test_case_id": f"TC-PDF-{test_case_counter:03d}",
                "title": "End-to-End Workflow Validation",
                "description": "Validate complete workflows described in the document",
                "preconditions": ["All system components are available", "Test data is prepared"],
                "test_steps": [
                    "Execute complete user workflows",
                    "Verify data flow between components",
                    "Validate business process completion"
                ],
                "expected_result": "Complete workflows execute successfully as documented",
                "test_type": "Integration",
                "priority": "High",
                "source": "PDF Document Workflows"
            }
            test_cases.append(integration_test)
        
        return {
            "status": "success",
            "message": f"Generated {len(test_cases)} test cases from PDF analysis",
            "test_cases": test_cases,
            "summary": {
                "total_test_cases": len(test_cases),
                "functional_tests": len([tc for tc in test_cases if tc['test_type'] == 'Functional']),
                "negative_tests": len([tc for tc in test_cases if tc['test_type'] == 'Negative']),
                "api_tests": len([tc for tc in test_cases if tc['test_type'] == 'API']),
                "integration_tests": len([tc for tc in test_cases if tc['test_type'] == 'Integration']),
                "source_document_type": doc_type
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating test cases from PDF: {str(e)}",
            "test_cases": []
        }
