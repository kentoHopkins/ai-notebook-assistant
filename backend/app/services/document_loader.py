from pathlib import Path
import pymupdf
from pptx import Presentation
import requests
from bs4 import BeautifulSoup
import ipaddress
import socket
from urllib.parse import urlparse

def extract_txt(file_path: str | Path) -> str:
    """
    Extract text from a plain-text file.
    Args:
        file_path: Path to the text file.
    Returns:
        The text contained in the file.
    Raises:
        FileNotFoundError: If the specified file does not exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8-sig") as file:
        content = file.read()
    content = content.strip()
    if not content:
        raise ValueError("The text file is empty.")
    return content

def extract_pdf(file_path: str | Path) -> str:
    """
    Extract text from a PDF document.
    Args:
        file_path: Path to the PDF file.
    Returns:
        The extracted text from all pages.
    Raises:
        ValueError: If the PDF contains no extractable text.
    """
    #reference https://leapcell.io/blog/how-to-use-fitz-in-python
    path = Path(file_path)
    with pymupdf.open(path) as pdf:
        pages = []
        for page in pdf:
            page_text = page.get_text()
            if page_text.strip():
                pages.append(page_text.strip())
    content = "\n\n".join(pages)
    if not content:
        raise ValueError("The PDF contains no extractable text.")
    return content

def extract_pptx(file_path: str | Path) -> str:
    """
    Extract text from a PowerPoint presentation.
    Args:
        file_path: Path to the PowerPoint file.
    Returns:
        The extracted text from all slides.
    Raises:
        ValueError: If the presentation contains no extractable text.
    """
    #https://python-pptx.readthedocs.io/en/latest/user/presentations.html
    #https://python-pptx.readthedocs.io/en/latest/user/text.html
    path = Path(file_path)
    presentation = Presentation(path)
    slides_text = []

    for slide in presentation.slides:
        shapes_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text.strip()
                if text:
                    shapes_text.append(text)
        if shapes_text:
            slides_text.append("\n".join(shapes_text))
    content = "\n\n".join(slides_text)
    if not content:
        raise ValueError(
            "The PowerPoint presentation contains no extractable text."
        )
    return content

def extract_webpage(url: str) -> str:
    """
    Extract readable text from a webpage.
    Args:
        url: The URL of the webpage.
    Returns:
        The extracted text from the webpage.
    Raises:
        ValueError: If the URL is invalid or the webpage contains no extractable text.
        requests.RequestException: If the webpage request fails.
    """
    #send an HTTP request
    validate_public_url(url)

    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "AI-Notebook-Assistant/1.0"},
        allow_redirects=False,
    )

    response.raise_for_status()
    if 300 <= response.status_code < 400:
        raise ValueError("Webpage redirects are not supported.")

    soup = BeautifulSoup(response.text, "html.parser")
    #remove non-useful elements that doesn't contain article content
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    content = soup.get_text(separator=" ", strip=True)
    if not content:
        raise ValueError("The webpage contains no extractable text.")
    return content

def validate_public_url(url: str) -> str:
    """
    Validate a URL and reject destinations that resolve to
    non-public IP addresses.
    Returns:
        The validated URL.
    Raises:
        ValueError: If the URL is invalid or unsafe.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported.")
    if not parsed_url.hostname or parsed_url.username or parsed_url.password:
        raise ValueError("The URL is invalid or contains credentials.")

    #resolve the hostname to its IP addresses
    hostname = parsed_url.hostname
    try:
        addresses = socket.getaddrinfo(
            hostname,
            parsed_url.port or (443 if parsed_url.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise ValueError("The URL hostname could not be resolved.") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise ValueError("URLs resolving to non-public IP addresses are not allowed.")
    return url