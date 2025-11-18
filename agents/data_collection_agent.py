import requests
import base64
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re

def fetch_github_readme(owner: str, repo: str) -> Dict[str, any]:
    """
    Data Collection Agent - Fetches README content from GitHub repository
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
    
    Returns:
        Dictionary containing README content in various formats
    """
    
    # GitHub API endpoint for README
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    try:
        # Fetch README metadata
        response = requests.get(api_url, headers={
            "Accept": "application/vnd.github.v3+json"
        })
        
        if response.status_code == 404:
            return {
                "success": False,
                "error": "Repository or README not found",
                "owner": owner,
                "repo": repo
            }
        
        response.raise_for_status()
        readme_data = response.json()
        
        # Extract base64 content
        base64_content = readme_data.get("content", "")
        
        # Decode base64 to plain text
        plain_text = decode_base64_to_text(base64_content)
        
        # Get HTML content from GitHub API
        html_url = readme_data.get("html_url", "")
        download_url = readme_data.get("download_url", "")
        
        # Fetch raw HTML if available
        html_content = None
        if download_url:
            html_response = requests.get(download_url)
            if html_response.status_code == 200:
                raw_content = html_response.text
                # Convert markdown to HTML-like structure (basic)
                html_content = markdown_to_html(raw_content)
        
        # Convert HTML to plain text
        plain_from_html = html_to_plain_text(html_content) if html_content else plain_text
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "name": readme_data.get("name", ""),
            "path": readme_data.get("path", ""),
            "size": readme_data.get("size", 0),
            "url": readme_data.get("url", ""),
            "html_url": html_url,
            "download_url": download_url,
            "content": {
                "base64": base64_content[:100] + "..." if len(base64_content) > 100 else base64_content,
                "plain_text": plain_text,
                "html": html_content,
                "plain_from_html": plain_from_html,
                "word_count": len(plain_text.split()),
                "char_count": len(plain_text)
            }
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "owner": owner,
            "repo": repo
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "owner": owner,
            "repo": repo
        }

def decode_base64_to_text(base64_content: str) -> str:
    """Decode base64 content to plain text"""
    try:
        # Remove whitespace and newlines
        base64_content = base64_content.replace("\n", "").replace(" ", "")
        # Decode base64
        decoded_bytes = base64.b64decode(base64_content)
        # Convert to string
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        return f"Error decoding base64: {str(e)}"

def html_to_plain_text(html_content: str) -> str:
    """Convert HTML content to plain text"""
    if not html_content:
        return ""
    
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error converting HTML to text: {str(e)}"

def markdown_to_html(markdown_content: str) -> str:
    """Basic markdown to HTML conversion"""
    if not markdown_content:
        return ""
    
    html = markdown_content
    
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = f'<p>{html}</p>'
    
    return html
