"""
Tool: Convert base64 to HTML and HTML to plain text.
"""
import base64
import re
from bs4 import BeautifulSoup

def decode_base64_to_text(base64_content: str) -> str:
    """Decode base64 content to plain text"""
    try:
        base64_content = base64_content.replace("\n", "").replace(" ", "")
        decoded_bytes = base64.b64decode(base64_content)
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        return f"Error decoding base64: {str(e)}"

def markdown_to_html(markdown_content: str) -> str:
    """Basic markdown to HTML conversion"""
    if not markdown_content:
        return ""
    html = markdown_content
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    html = html.replace('\n\n', '</p><p>')
    html = f'<p>{html}</p>'
    return html

def html_to_plain_text(html_content: str) -> str:
    """Convert HTML content to plain text"""
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return f"Error converting HTML to text: {str(e)}"
