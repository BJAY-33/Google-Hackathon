"""
Git Tools - Tools for Git repository analysis and manipulation
"""

import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class GitRepository(BaseModel):
    """Model for Git repository information."""
    url: str
    branch: str = "main"
    local_path: str = ""
    commit_hash: str = ""

class GitChange(BaseModel):
    """Model for Git change information."""
    file_path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0
    content_preview: str = ""

class GitAnalysisResult(BaseModel):
    """Model for Git analysis results."""
    repository: GitRepository
    changes: List[GitChange]
    affected_files: List[str]
    commit_messages: List[str]
    summary: str

def clone_repository(repository_url: str, branch: str = "main", target_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Clone a Git repository to analyze its contents.
    
    Args:
        repository_url: The URL of the Git repository to clone
        branch: The branch to checkout (default: main)
        target_dir: Optional target directory (if None, uses temp directory)
        
    Returns:
        Dictionary with clone status and local path information
    """
    try:
        # Create target directory
        if target_dir is None:
            target_dir = tempfile.mkdtemp(prefix="git_analysis_")
        
        # Clone the repository
        clone_cmd = ["git", "clone", "--branch", branch, repository_url, target_dir]
        result = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Failed to clone repository: {result.stderr}",
                "local_path": ""
            }
        
        # Get the latest commit hash
        commit_cmd = ["git", "-C", target_dir, "rev-parse", "HEAD"]
        commit_result = subprocess.run(commit_cmd, capture_output=True, text=True)
        commit_hash = commit_result.stdout.strip() if commit_result.returncode == 0 else ""
        
        return {
            "status": "success",
            "message": f"Successfully cloned repository to {target_dir}",
            "local_path": target_dir,
            "repository_url": repository_url,
            "branch": branch,
            "commit_hash": commit_hash
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Repository clone timed out",
            "local_path": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error cloning repository: {str(e)}",
            "local_path": ""
        }

def analyze_git_changes(repository_path: str, since_commit: Optional[str] = None, max_commits: int = 10) -> Dict[str, Any]:
    """
    Analyze recent changes in a Git repository.
    
    Args:
        repository_path: Path to the local Git repository
        since_commit: Optional commit hash to compare from
        max_commits: Maximum number of commits to analyze
        
    Returns:
        Dictionary with analysis of recent changes
    """
    try:
        if not os.path.exists(repository_path) or not os.path.exists(os.path.join(repository_path, ".git")):
            return {
                "status": "error",
                "message": "Invalid Git repository path",
                "changes": []
            }
        
        # Get recent commits
        if since_commit:
            log_cmd = ["git", "-C", repository_path, "log", f"{since_commit}..HEAD", "--oneline", f"-{max_commits}"]
        else:
            log_cmd = ["git", "-C", repository_path, "log", "--oneline", f"-{max_commits}"]
        
        log_result = subprocess.run(log_cmd, capture_output=True, text=True)
        commit_messages = log_result.stdout.strip().split('\n') if log_result.stdout.strip() else []
        
        # Get file changes
        if since_commit:
            diff_cmd = ["git", "-C", repository_path, "diff", "--name-status", f"{since_commit}..HEAD"]
        else:
            diff_cmd = ["git", "-C", repository_path, "diff", "--name-status", "HEAD~1..HEAD"]
        
        diff_result = subprocess.run(diff_cmd, capture_output=True, text=True)
        
        changes = []
        affected_files = []
        
        if diff_result.stdout.strip():
            for line in diff_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status = parts[0]
                        file_path = parts[1]
                        
                        # Map Git status codes to change types
                        change_type_map = {
                            'A': 'added',
                            'M': 'modified',
                            'D': 'deleted',
                            'R': 'renamed',
                            'C': 'copied'
                        }
                        
                        change_type = change_type_map.get(status[0], 'unknown')
                        changes.append({
                            "file_path": file_path,
                            "change_type": change_type,
                            "status_code": status
                        })
                        affected_files.append(file_path)
        
        # Get detailed statistics
        stats_cmd = ["git", "-C", repository_path, "diff", "--stat", "HEAD~1..HEAD"]
        stats_result = subprocess.run(stats_cmd, capture_output=True, text=True)
        
        return {
            "status": "success",
            "changes": changes,
            "affected_files": affected_files,
            "commit_messages": commit_messages,
            "stats": stats_result.stdout.strip() if stats_result.stdout else "",
            "total_files_changed": len(affected_files),
            "summary": f"Analyzed {len(commit_messages)} commits affecting {len(affected_files)} files"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing Git changes: {str(e)}",
            "changes": []
        }

def extract_file_changes(repository_path: str, file_path: str, since_commit: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract detailed changes for a specific file.
    
    Args:
        repository_path: Path to the local Git repository
        file_path: Path to the specific file to analyze
        since_commit: Optional commit hash to compare from
        
    Returns:
        Dictionary with detailed file change information
    """
    try:
        if not os.path.exists(repository_path):
            return {
                "status": "error",
                "message": "Repository path does not exist",
                "content": ""
            }
        
        # Get the current file content
        full_file_path = os.path.join(repository_path, file_path)
        current_content = ""
        
        if os.path.exists(full_file_path):
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            except UnicodeDecodeError:
                # Handle binary files or files with different encodings
                current_content = "[Binary file or encoding issue]"
        
        # Get the diff for this specific file
        if since_commit:
            diff_cmd = ["git", "-C", repository_path, "diff", f"{since_commit}..HEAD", "--", file_path]
        else:
            diff_cmd = ["git", "-C", repository_path, "diff", "HEAD~1..HEAD", "--", file_path]
        
        diff_result = subprocess.run(diff_cmd, capture_output=True, text=True)
        
        # Get file statistics
        stat_cmd = ["git", "-C", repository_path, "diff", "--numstat", "HEAD~1..HEAD", "--", file_path]
        stat_result = subprocess.run(stat_cmd, capture_output=True, text=True)
        
        additions, deletions = 0, 0
        if stat_result.stdout.strip():
            stats = stat_result.stdout.strip().split('\t')
            if len(stats) >= 2:
                try:
                    additions = int(stats[0]) if stats[0] != '-' else 0
                    deletions = int(stats[1]) if stats[1] != '-' else 0
                except ValueError:
                    pass
        
        return {
            "status": "success",
            "file_path": file_path,
            "current_content": current_content[:2000] + "..." if len(current_content) > 2000 else current_content,
            "diff": diff_result.stdout,
            "additions": additions,
            "deletions": deletions,
            "file_exists": os.path.exists(full_file_path),
            "summary": f"File {file_path}: +{additions} -{deletions} lines changed"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error extracting file changes: {str(e)}",
            "content": ""
        }

def cleanup_repository(repository_path: str) -> Dict[str, Any]:
    """
    Clean up a cloned repository directory.
    
    Args:
        repository_path: Path to the repository directory to clean up
        
    Returns:
        Dictionary with cleanup status
    """
    try:
        if os.path.exists(repository_path):
            shutil.rmtree(repository_path)
            return {
                "status": "success",
                "message": f"Successfully cleaned up repository at {repository_path}"
            }
        else:
            return {
                "status": "warning",
                "message": "Repository path does not exist, nothing to clean up"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error cleaning up repository: {str(e)}"
        }
