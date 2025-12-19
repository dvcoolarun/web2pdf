#!/usr/bin/python

# Check for --browser flag BEFORE importing gevent to avoid conflicts with Playwright
import sys
_USE_BROWSER_MODE = '--browser' in sys.argv or '-b' in sys.argv

# Only patch gevent if NOT using browser mode (Playwright conflicts with gevent)
if not _USE_BROWSER_MODE:
    import gevent.monkey as curious_george
    curious_george.patch_all(thread=False, select=False)

from dominate.util import raw
from dominate import tags as tags
import dominate
from weasyprint import HTML
from readability import Document
from fake_useragent import UserAgent
import validators
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from rich import print
import typer
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse

# Import grequests only if not in browser mode (it requires gevent)
if not _USE_BROWSER_MODE:
    import grequests
else:
    import requests as grequests_fallback

# Optional Playwright support for JavaScript-rendered pages
# Check at runtime instead of module load time to handle conda environments better
def check_playwright_available():
    """ Check if Playwright is available (runtime check) """
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False

def ensure_playwright_installed():
    """ Try to install Playwright if it's not available """
    from rich import print
    
    print("[red]Playwright is not installed.[/red]")
    print("[yellow]Due to gevent compatibility issues, automatic installation is not available.[/yellow]")
    print("[bold yellow]Please install Playwright manually by running:[/bold yellow]")
    print("[bold cyan]  pip install playwright[/bold cyan]")
    print("[bold cyan]  playwright install chromium[/bold cyan]")
    print("[yellow]Then run this script again with the --browser flag.[/yellow]")
    return False

def ensure_playwright_browser_installed():
    """ Check if Playwright browsers are installed, and install chromium if not """
    import subprocess
    import sys
    from rich import print
    
    # First, check if Playwright is available
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[yellow]Playwright not found. Attempting to install...[/yellow]")
        if not ensure_playwright_installed():
            print("[red]Could not install Playwright. Please install manually: pip install playwright[/red]")
            return False
        # Try importing again after installation
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("[red]Playwright installation completed but import still fails. Please restart and try again.[/red]")
            return False
    
    try:
        # Try to launch chromium to see if it's installed
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            return True
        except Exception as e:
            # Browser not installed, need to install it
            print("[red]Chromium browser is not installed.[/red]")
            print("[yellow]Due to gevent compatibility issues, automatic installation is not available.[/yellow]")
            print("[bold yellow]Please install Chromium manually by running:[/bold yellow]")
            print("[bold cyan]  playwright install chromium[/bold cyan]")
            print("[yellow]Then run this script again with the --browser flag.[/yellow]")
            return False
    except Exception as e:
        from rich import print
        print(f"[red]Error checking Playwright installation: {e}[/red]")
        return False
""" Styles for the PDF """

css_styles = """
    body {
        hyphens: auto;
        font-size: 12px;
        font-weight: 100;
        line-height: 1.5;
        font-family: 'Work Sans', sans-serif;
    }

    @page {
        size: A4;
        @bottom-right {
            content: counter(page);
        }
    }
    @page :first {
        @bottom-right {
            content: "";
        }
    }

    #article-body>div {
        background-clip:content-box;
        text-align: justify;
        padding: 0em 1em;
    }

    #article-body > h1 {
        font-weight: 100;
        font-size: 24px;
    }

    .toc h1 {
        font-weight: 100;
        margin: 10% 0;
    }
    .toc h3 {
        border-bottom: 2px solid #f9f9f9;
        font-weight: 100;
        padding: 1em 0em;
    }

    .toc h3 a {
        display: block;
        text-decoration: none;
        color: #000;
    }
    .toc h3 a::after{
        content: target-counter(attr(href), page);
        float: right;
    }
    ul, li {
        font-weight: 100;
    }

    img {
        width: 100%;
    }

    .top-border {
        border-top: 5px solid #000;
        width: 30%;
    }

    .page-break {
        page-break-before: always
    }

    blockquote {
        background: #f9f9f9;
        border-left: 10px solid #ccc;
        margin: 1.5em 0.5em;
        padding: 0.5em 0.5em;
    }

    blockquote p {
        display: inline;
    }

    pre {
        background: #f9f9f9;
        border: 1px solid #eee;
        white-space: pre-wrap
    }
    table {
        background: #eee;
        border: 1px solid #eee;
        width: 100%;
        white-space: pre-wrap
    }
    td{
        background: #eee;
    }

    """

class Web2PDFConverter:
    """ Class to convert web pages to PDF """

    def __init__(self, use_browser=False):
        self.console = Console()
        self.visited_urls = set()
        self.all_urls = set()
        
        if use_browser:
            # Automatically ensure Playwright and browser are installed when --browser is used
            if ensure_playwright_browser_installed():
                self.use_browser = True
            else:
                print("[yellow]Warning: Could not set up Playwright browser.[/yellow]")
                print("[yellow]Falling back to regular HTTP requests (may not work for JavaScript-rendered pages)[/yellow]")
                self.use_browser = False
        else:
            self.use_browser = False

    def generate_filename_from_url(self, url):
        """ Generate a clean filename from URL """
        try:
            from urllib.parse import urlparse
            import re
            
            parsed = urlparse(url)
            
            # Get the path and clean it up
            path = parsed.path.strip('/')
            
            # If path is empty or just '/', use the domain
            if not path or path == '/':
                filename = parsed.netloc.replace('www.', '').replace('.', '_')
            else:
                # Use the last part of the path
                path_parts = [p for p in path.split('/') if p]
                if path_parts:
                    filename = path_parts[-1]
                else:
                    filename = parsed.netloc.replace('www.', '').replace('.', '_')
            
            # Clean up the filename
            filename = re.sub(r'[^\w\-_.]', '_', filename)
            filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores with single
            filename = filename.strip('_')
            
            # If filename is too long, truncate it
            if len(filename) > 50:
                filename = filename[:50]
            
            # If filename is empty, use a default
            if not filename:
                filename = 'webpage'
                
            return filename
        except Exception as e:
            print(f"Error generating filename: {e}")
            return 'webpage'

    def _format_text_as_html(self, text):
        """ Format plain text as HTML with basic structure """
        if not text:
            return ""
        
        import html
        
        # Escape HTML special characters
        def escape_html(s):
            return html.escape(str(s))
        
        lines = text.split('\n')
        html_lines = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    escaped_para = escape_html(' '.join(current_paragraph))
                    html_lines.append(f"<p>{escaped_para}</p>")
                    current_paragraph = []
            elif len(line) > 0 and line[0].isupper() and len(line) < 100 and not line.endswith('.') and not line.endswith(','):
                # Might be a heading
                if current_paragraph:
                    escaped_para = escape_html(' '.join(current_paragraph))
                    html_lines.append(f"<p>{escaped_para}</p>")
                    current_paragraph = []
                escaped_heading = escape_html(line)
                html_lines.append(f"<h2>{escaped_heading}</h2>")
            else:
                current_paragraph.append(line)
        
        if current_paragraph:
            escaped_para = escape_html(' '.join(current_paragraph))
            html_lines.append(f"<p>{escaped_para}</p>")
        
        escaped_text = escape_html(text)
        return '\n'.join(html_lines) if html_lines else f"<p>{escaped_text}</p>"

    def extract_content_fallback(self, html_content):
        """ Extract meaningful content from HTML when readability fails """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript", "meta", "link"]):
                script.decompose()
            
            # Try to find main content areas
            main_content = None
            
            # Common content container selectors
            content_selectors = [
                'main', 'article', '[role="main"]', 
                '.content', '#content', '.main-content',
                '.post', '.entry', '.article-content',
                'body'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    main_content = elements[0]
                    break
            
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Get text content with some structure preserved
            # Extract headings and paragraphs
            content_html = ""
            
            # Get title
            title_tag = soup.find('title')
            if title_tag:
                content_html += f"<h1>{title_tag.get_text()}</h1>\n"
            
            # Extract all headings and paragraphs
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section', 'article']):
                # Skip if element is empty or only whitespace
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Only include substantial content
                    tag_name = element.name
                    # Preserve heading hierarchy
                    if tag_name.startswith('h'):
                        content_html += f"<{tag_name}>{text}</{tag_name}>\n"
                    elif tag_name == 'p':
                        content_html += f"<p>{text}</p>\n"
                    elif text:  # For divs and other containers, just get text
                        # Only include if it's substantial (not just navigation, etc.)
                        if len(text) > 50:
                            content_html += f"<div>{text}</div>\n"
            
            # If we still don't have much content, get all text from body
            if len(content_html.strip()) < 200:
                body_text = main_content.get_text(separator='\n', strip=True)
                # Clean up excessive whitespace
                lines = [line.strip() for line in body_text.split('\n') if line.strip() and len(line.strip()) > 10]
                if lines:
                    content_html = "<div>" + "\n".join([f"<p>{line}</p>" for line in lines[:50]]) + "</div>"
            
            return content_html if content_html.strip() else None
            
        except Exception as e:
            print(f"[yellow]Warning: Fallback content extraction failed: {e}[/yellow]")
            return None

    def extract_links_from_page(self, response, base_url):
        """ Extract links from a web page response """
        try:
            if not response or not response.text:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            # Find all anchor tags with href attributes
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(base_url, href)
                
                # Parse the URL to check if it's from the same domain
                parsed_base = urlparse(base_url)
                parsed_link = urlparse(absolute_url)
                
                # Only include links from the same domain
                if parsed_link.netloc == parsed_base.netloc:
                    # Remove fragments and query parameters for cleaner URLs
                    clean_url = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                    if clean_url not in self.visited_urls:
                        links.append(clean_url)
            
            return links
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []

    def crawl_urls_recursively(self, start_url, depth=2, current_depth=0, rate_limit=5):
        """ Recursively crawl URLs starting from a base URL """
        if current_depth >= depth or start_url in self.visited_urls:
            return []
        
        self.visited_urls.add(start_url)
        self.all_urls.add(start_url)
        
        if current_depth == 0:
            print(f"[bold Green]Starting recursive crawl from: {start_url}[/bold Green]")
            print(f"[bold Yellow]Crawl depth: {depth}[/bold Yellow]")
        
        try:
            user_agent = UserAgent()
            headers = {'User-Agent': user_agent.random}
            
            # Get the page content
            # Use regular requests if in browser mode (gevent not patched), otherwise use grequests
            if _USE_BROWSER_MODE:
                import requests
                response = requests.get(start_url, headers=headers, timeout=30)
            else:
                import grequests
                response = grequests.get(start_url, headers=headers)
                response = grequests.map([response])[0]
            
            if not response or response.status_code != 200:
                print(f"[red]Failed to fetch {start_url}: {response.status_code if response else 'No response'}[/red]")
                return [start_url]
            
            print(f"[green]✓ Crawled: {start_url} (depth {current_depth})[/green]")
            
            # If we haven't reached max depth, extract links and crawl them
            if current_depth < depth - 1:
                links = self.extract_links_from_page(response, start_url)
                print(f"[blue]Found {len(links)} links to crawl at depth {current_depth + 1}[/blue]")
                
                # Crawl found links recursively with rate limiting
                import time
                batch_size = 10
                for i, link in enumerate(links):
                    if link not in self.visited_urls:
                        # Add delay every 10 requests to be respectful to the server
                        if i > 0 and i % batch_size == 0:
                            print(f"[yellow]Rate limiting: sleeping {rate_limit} seconds after {i} requests...[/yellow]")
                            time.sleep(rate_limit)
                        
                        self.crawl_urls_recursively(link, depth, current_depth + 1, rate_limit)
            
            return [start_url]
            
        except Exception as e:
            print(f"[red]Error crawling {start_url}: {e}[/red]")
            return [start_url]

    def fetch_with_browser(self, url, headers=None):
        """ Fetch page content using Playwright (for JavaScript-rendered pages) """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("[red]Error: Playwright is not available. Please install it: pip install playwright[/red]")
            return None
        
        try:
            import requests
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent if provided
                if headers and 'User-Agent' in headers:
                    page.set_extra_http_headers({'User-Agent': headers['User-Agent']})
                
                # Navigate and wait for content to load
                print(f"[blue]Loading {url} with browser...[/blue]")
                page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Wait for common content indicators to appear
                # Try to wait for actual content elements, not just network idle
                try:
                    # Wait for Redoc-specific elements first (common in API docs)
                    redoc_selectors = ['redoc', '#redoc-container', '.redoc-wrap', '[class*="redoc"]']
                    redoc_loaded = False
                    
                    for selector in redoc_selectors:
                        try:
                            element = page.wait_for_selector(selector, timeout=10000, state='attached')
                            if element:
                                print(f"[green]Found Redoc element: {selector}[/green]")
                                # Wait for Redoc to render content (it loads schema asynchronously)
                                page.wait_for_timeout(8000)  # Redoc needs time to fetch and render schema
                                redoc_loaded = True
                                break
                        except:
                            continue
                    
                    if not redoc_loaded:
                        # Wait for common content containers
                        selectors_to_try = [
                            'main', 'article', '[role="main"]', 
                            '.content', '#content', '.main-content',
                            'body > *:not(script):not(style)',
                            'h1', 'h2', 'p'
                        ]
                        
                        content_found = False
                        for selector in selectors_to_try:
                            try:
                                # Wait for selector with visible text content
                                element = page.wait_for_selector(selector, timeout=5000, state='attached')
                                if element:
                                    # Check if element has substantial text content
                                    text = element.inner_text() if hasattr(element, 'inner_text') else ''
                                    if text and len(text.strip()) > 100:
                                        print(f"[green]Found content via selector: {selector} ({len(text)} chars)[/green]")
                                        content_found = True
                                        break
                            except:
                                continue
                        
                        if not content_found:
                            print("[yellow]No substantial content found via selectors, waiting longer...[/yellow]")
                            # Wait longer for dynamic content (e.g., React apps, Vue apps)
                            page.wait_for_timeout(5000)
                    
                    # Additional wait for any remaining lazy-loaded content
                    page.wait_for_timeout(3000)
                    
                except Exception as e:
                    print(f"[yellow]Warning while waiting for content: {e}[/yellow]")
                    # Still wait a bit even if selectors fail
                    page.wait_for_timeout(5000)
                
                # Scroll to trigger lazy loading
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(1000)
                except:
                    pass
                
                # For Redoc and other shadow DOM content, extract the rendered content
                # Redoc renders content in shadow DOM which page.content() doesn't capture
                html_content = None
                try:
                    # Get visible text content (this works even with shadow DOM)
                    # This is the key - innerText/textContent can access shadow DOM content
                    page_data = page.evaluate("""
                        () => {
                            return {
                                title: document.title,
                                visibleText: document.body.innerText || document.body.textContent || '',
                                bodyHTML: document.body.innerHTML,
                                // Try to get text from common content areas
                                mainText: (() => {
                                    const main = document.querySelector('main') || 
                                                 document.querySelector('article') || 
                                                 document.querySelector('[role="main"]') ||
                                                 document.body;
                                    return main.innerText || main.textContent || '';
                                })()
                            };
                        }
                    """)
                    
                    visible_text = page_data.get('visibleText', '') or page_data.get('mainText', '')
                    
                    if visible_text and len(visible_text.strip()) > 500:
                        print(f"[green]Extracted {len(visible_text)} chars from visible text (including shadow DOM)[/green]")
                        # Reconstruct HTML with the visible content properly formatted
                        # Try to preserve some structure by using the body HTML and injecting visible text
                        body_html = page_data.get('bodyHTML', '')
                        page_title = page_data.get('title', 'Page')
                        
                        # Create a well-structured HTML document with the visible content
                        import html
                        escaped_title = html.escape(page_title)
                        formatted_content = self._format_text_as_html(visible_text)
                        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escaped_title}</title>
</head>
<body>
    <div id="main-content">
        <h1>{escaped_title}</h1>
        <div id="extracted-text-content">
            {formatted_content}
        </div>
    </div>
</body>
</html>"""
                    else:
                        print(f"[yellow]Visible text too short ({len(visible_text)} chars), using regular HTML[/yellow]")
                        html_content = None
                except Exception as e:
                    print(f"[yellow]Could not extract visible text content: {e}[/yellow]")
                    html_content = None
                
                # Fallback to regular content if extraction didn't work
                if not html_content:
                    html_content = page.content()
                
                # Debug: Check content size
                content_length = len(html_content)
                print(f"[blue]Rendered HTML size: {content_length} bytes[/blue]")
                
                # Check if we got substantial content
                soup = BeautifulSoup(html_content, 'html.parser')
                # Remove scripts and styles to check actual content
                for script in soup(["script", "style", "noscript"]):
                    script.decompose()
                text_content = soup.get_text(strip=True)
                text_length = len(text_content)
                print(f"[blue]Text content length: {text_length} chars[/blue]")
                
                if text_length < 500:
                    print(f"[yellow]Warning: Very little text content extracted ({text_length} chars). Page may still be loading.[/yellow]")
                
                browser.close()
                
                # Create a mock response object
                class MockResponse:
                    def __init__(self, text, status_code=200):
                        self.text = text
                        self.content = text.encode('utf-8')
                        self.status_code = status_code
                        self.headers = {'Content-Type': 'text/html'}
                
                return MockResponse(html_content, 200)
        except Exception as e:
            print(f"[red]Error fetching {url} with browser: {e}[/red]")
            import traceback
            traceback.print_exc()
            return None

    def make_async_request(self, url_list, headers):
        """ Making asynchrnous requests """
        try:
            print(f"Making requests to {len(url_list)} URLs")

            # Use browser for JavaScript-rendered pages if enabled
            if self.use_browser:
                print("[blue]Using browser rendering for JavaScript-rendered pages...[/blue]")
                responses = []
                for url in url_list:
                    response = self.fetch_with_browser(url, headers)
                    if response:
                        responses.append(response)
                    else:
                        # Fallback to regular request (using requests, not grequests in browser mode)
                        print(f"[yellow]Browser fetch failed for {url}, falling back to HTTP request[/yellow]")
                        import requests
                        try:
                            resp = requests.get(url, headers=headers, timeout=30)
                            responses.append(resp)
                        except Exception as e:
                            print(f"[red]HTTP request also failed for {url}: {e}[/red]")
                            responses.append(None)
            else:
                # Use grequests for async requests (only available when gevent is patched)
                import grequests
                request_urls = (grequests.get(url, headers=headers, timeout=30)
                                for url in url_list)
                responses = grequests.map(request_urls)

            print(f"Got {len(responses)} responses")

            # Debug: Check response sizes
            for url, response in zip(url_list, responses):
                if response:
                    content_length = len(response.text) if response.text else 0
                    print(f"[blue]  {url}: {response.status_code} ({content_length} bytes)[/blue]")
                    if content_length < 1000:
                        print(f"[yellow]  Warning: Very small response for {url} - may be JavaScript-rendered[/yellow]")
                        if not self.use_browser:
                            print(f"[yellow]  Consider using --browser flag for JavaScript-rendered pages[/yellow]")
                else:
                    print(f"[red]  {url}: No response[/red]")

            return responses
        except Exception as e:
            print(f"Error making asynchronous request: {e}")
            return []

    def create_assembled_pdf(self, url_list, request_responses, output_dir, force=False):
        """ Create a single assembled PDF with all pages combined """
        try:
            import os
            
            pdf_path = os.path.join(output_dir, "Assembled_Master.pdf")
            
            # Check if assembled PDF already exists (unless force mode)
            if not force and os.path.exists(pdf_path):
                print(f"[yellow]⏭️  Skipping Assembled_Master.pdf (already exists, use --force to re-process)[/yellow]")
                return
            
            # Create the assembled HTML document
            document = dominate.document()
            with document.head:
                tags.link(
                    href="https://fonts.googleapis.com/css2?family=Work+Sans&display=swap",
                    rel="stylesheet")
                tags.style(raw(css_styles))
                tags.meta(charset='utf-8')
                tags.meta(content="text/html")

            with document:
                # Create table of contents
                with tags.div(cls='toc'):
                    tags.h1("Table of Contents")
                    for index, (url, response) in enumerate(zip(url_list, request_responses)):
                        if response and response.status_code == 200:
                            try:
                                doc = Document(response.text)
                                title = doc.title()
                                with tags.h3():
                                    tags.a(title or f"Page {index + 1}", href=f"#heading{index}")
                            except:
                                with tags.h3():
                                    tags.a(f"Page {index + 1}", href=f"#heading{index}")
                    tags.p(cls='page-break')

                # Add all content
                for index, (url, response) in enumerate(zip(url_list, request_responses)):
                    if response and response.status_code == 200:
                        try:
                            doc = Document(response.text)
                            title = doc.title()
                            main_content = doc.summary()
                            
                            # Check if readability extracted meaningful content
                            content_length = len(main_content.strip()) if main_content else 0
                            
                            with tags.div(id='article-body'):
                                tags.h1(title or f"Page {index + 1}", id=f'heading{index}')
                                tags.p(cls='top-border')
                                
                                if main_content and content_length > 200:
                                    # Use readability content if substantial
                                    tags.div(raw(main_content))
                                else:
                                    # Try fallback extraction
                                    print(f"[yellow]Readability extracted minimal content ({content_length} chars) for {url}, trying fallback...[/yellow]")
                                    fallback_content = self.extract_content_fallback(response.text)
                                    
                                    if fallback_content and len(fallback_content.strip()) > 200:
                                        print(f"[green]Fallback extraction successful ({len(fallback_content)} chars)[/green]")
                                        tags.div(raw(fallback_content))
                                    else:
                                        # Last resort: use raw HTML but clean it up
                                        print(f"[yellow]Using raw HTML as last resort for {url}[/yellow]")
                                        soup = BeautifulSoup(response.text, 'html.parser')
                                        # Remove scripts and styles
                                        for script in soup(["script", "style", "noscript"]):
                                            script.decompose()
                                        tags.div(raw(str(soup)))
                            tags.p(cls='page-break')
                        except Exception as e:
                            print(f"[red]Error processing {url}: {e}[/red]")
                            try:
                                # Try fallback extraction even on error
                                fallback_content = self.extract_content_fallback(response.text)
                                with tags.div(id='article-body'):
                                    tags.h1(f"Page {index + 1}", id=f'heading{index}')
                                    tags.p(cls='top-border')
                                    if fallback_content:
                                        tags.div(raw(fallback_content))
                                    else:
                                        tags.div(raw(response.text))
                            except:
                                with tags.div(id='article-body'):
                                    tags.h1(f"Page {index + 1}", id=f'heading{index}')
                                    tags.p(cls='top-border')
                                    tags.p(f"Could not extract content from {url}")
                            tags.p(cls='page-break')

            # Save and convert the assembled document
            html_path = os.path.join(output_dir, "Assembled_Master.html")
            pdf_path = os.path.join(output_dir, "Assembled_Master.pdf")
            
            with open(html_path, "w+") as output_file:
                output_file.write(document.render())
            
            HTML(html_path).write_pdf(pdf_path)
            print(f"[green]✓ Created: Assembled_Master.pdf[/green]")
            
        except Exception as e:
            print(f"Error creating assembled PDF: {e}")

    def create_single_page_html_document(self, response, url):
        """ Creating HTML document for a single page """
        try:
            document = dominate.document()
            with document.head:
                tags.link(
                    href="https://fonts.googleapis.com/css2?family=Work+Sans&display=swap",
                    rel="stylesheet")
                tags.style(raw(css_styles))
                tags.meta(charset='utf-8')
                tags.meta(content="text/html")

            with document:
                if response:
                    try:
                        doc = Document(response.text)
                        title = doc.title()
                        main_content = doc.summary()
                        
                        # Check if readability extracted meaningful content
                        content_length = len(main_content.strip()) if main_content else 0
                        
                        # Debug: print what we're getting
                        print(f"[blue]Title: {title}[/blue]")
                        print(f"[blue]Content length: {content_length} chars[/blue]")
                        
                        with tags.div(id='article-body'):
                            tags.h1(title or "Untitled")
                            tags.p(cls='top-border')
                            
                            if main_content and content_length > 200:
                                # Use readability content if substantial
                                tags.div(raw(main_content))
                            else:
                                # Try fallback extraction
                                print(f"[yellow]Readability extracted minimal content ({content_length} chars), trying fallback...[/yellow]")
                                fallback_content = self.extract_content_fallback(response.text)
                                
                                if fallback_content and len(fallback_content.strip()) > 200:
                                    print(f"[green]Fallback extraction successful ({len(fallback_content)} chars)[/green]")
                                    tags.div(raw(fallback_content))
                                else:
                                    # Last resort: use raw HTML but clean it up
                                    print(f"[yellow]Using cleaned raw HTML as last resort[/yellow]")
                                    soup = BeautifulSoup(response.text, 'html.parser')
                                    # Remove scripts and styles
                                    for script in soup(["script", "style", "noscript"]):
                                        script.decompose()
                                    tags.div(raw(str(soup)))
                    except Exception as e:
                        print(f"[red]Error processing content: {e}[/red]")
                        try:
                            # Try fallback extraction even on error
                            fallback_content = self.extract_content_fallback(response.text)
                            with tags.div(id='article-body'):
                                tags.h1("Page Content")
                                tags.p(cls='top-border')
                                if fallback_content:
                                    tags.div(raw(fallback_content))
                                else:
                                    tags.p(f"Could not extract content: {e}")
                                    # Last resort: cleaned raw HTML
                                    soup = BeautifulSoup(response.text, 'html.parser')
                                    for script in soup(["script", "style", "noscript"]):
                                        script.decompose()
                                    tags.div(raw(str(soup)))
                        except Exception as e2:
                            print(f"[red]Fallback also failed: {e2}[/red]")
                            with tags.div(id='article-body'):
                                tags.h1("Error Processing Page")
                                tags.p(f"Could not extract content: {e}")
                                tags.p(f"Fallback also failed: {e2}")

            return document
        except Exception as e:
            print(f"Error creating single page HTML document: {e}")
            return dominate.document()

    def create_html_document(self, request_responses):
        """ Creating HTML document with Table of Contents"""
        try:
            document = dominate.document()
            with document.head:
                tags.link(
                    href="https://fonts.googleapis.com/css2?family=Work+Sans&display=swap",
                    rel="stylesheet")
                tags.style(raw(css_styles))
                """ For column layout """
                """ tags.style(raw(
                    "#article-body>div {column-count: 2; column-gap: 2em; column-rule: 2px solid #f9f9f9;}")) """
                tags.meta(charset='utf-8')
                tags.meta(content="text/html")

            with document:
                with tags.div(cls='toc'):
                    for index, each_response in enumerate(request_responses):
                        if each_response:
                            doc = Document(each_response.text)
                            title = doc.title()
                            with tags.h3():
                                tags.a(title, href="#heading" + str(index))
                    tags.p(cls='page-break')

            return document
        except Exception as e:
            print(f"Error creating HTML document: {e}")
            return dominate.document()

    def process_and_add_content(self, request_responses, document):
        """ Processing the response and adding content to the HTML document """
        try:
            for index, each_response in enumerate(request_responses):
                if each_response:
                    doc = Document(each_response.content)
                    title = doc.title()
                    main_content = doc.summary()
                    with document as final_document:
                        with tags.div(id='article-body'):
                            tags.h1(title, id='heading' + str(index))
                            tags.p(cls='top-border')
                            tags.div(raw(main_content))
                        tags.p(cls='page-break')

            return final_document
        except Exception as e:
            print(f"Error processing and adding content: {e}")
            return document

    def save_single_page_html(self, html_path, html_document):
        """ Writing a single page HTML document to file """
        try:
            import os
            # Create the entire directory path if it doesn't exist
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            with open(html_path, "w+") as output_file:
                output_file.write(html_document.render())
        except Exception as e:
            print(f"Error saving single page HTML to file: {e}")

    def convert_single_page_to_pdf(self, html_path, pdf_path):
        """ Converting a single HTML page to PDF """
        try:
            import os
            # Create the entire directory path if it doesn't exist
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            HTML(html_path).write_pdf(pdf_path)
        except Exception as e:
            print(f"Error converting single page HTML to PDF: {e}")

    def save_html_to_file(self, html_document, output_dir="."):
        """ Writing the HTML document to file """
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            html_path = os.path.join(output_dir, "print.html")
            with open(html_path, "w+") as output_file:
                output_file.write(html_document.render())
        except Exception as e:
            print(f"Error saving HTML to file: {e}")

    def convert_html_to_pdf(self, html_filename="print.html", pdf_filename="print.pdf", output_dir="."):
        """ Converting HTML to PDF using WeasyPrint"""
        try:
            import os
            html_path = os.path.join(output_dir, html_filename)
            pdf_path = os.path.join(output_dir, pdf_filename)
            HTML(html_path).write_pdf(pdf_path)
        except Exception as e:
            print(f"Error converting HTML to PDF: {e}")

    def process_urls(self, url_list, output_dir=".", assemble=False, force=False):
        """ Processing the URLs """
        import os
        # Create the output directory and all parent directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)
        
        user_agent = UserAgent()
        headers = {'User-Agent': user_agent.random}
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Processing URLs. :link:")
                request_responses = self.make_async_request(url_list, headers)

                if assemble:
                    # Separate PDF responses for direct download
                    html_urls = []
                    html_responses = []
                    for url, response in zip(url_list, request_responses):
                        if self.is_pdf_response(response, url):
                            print(f"[blue]Detected PDF link: {url}[/blue]")
                            self.save_pdf_response(response, url, output_dir, force)
                        else:
                            html_urls.append(url)
                            html_responses.append(response)
                    
                    if html_urls:
                        # Create a single assembled PDF from HTML pages
                        self.create_assembled_pdf(html_urls, html_responses, output_dir, force)
                    else:
                        print("[yellow]No HTML pages to assemble after filtering PDFs.[/yellow]")
                else:
                    # Process each URL individually
                    for i, (url, response) in enumerate(zip(url_list, request_responses)):
                        print(f"Processing URL: {url}")
                        print(f"Response status: {response.status_code if response else 'No response'}")
                        print(f"Response content length: {len(response.text) if response and response.text else 0}")
                        
                        if response and response.status_code == 200:
                            if self.is_pdf_response(response, url):
                                print(f"[blue]Detected PDF link: {url}[/blue]")
                                self.save_pdf_response(response, url, output_dir, force)
                                continue
                            
                            # Generate filename from URL
                            filename = self.generate_filename_from_url(url)
                            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
                            
                            # Check if PDF already exists (unless force mode)
                            if not force and os.path.exists(pdf_path):
                                print(f"[yellow]⏭️  Skipping {filename}.pdf (already exists, use --force to re-process)[/yellow]")
                                continue
                            
                            progress.add_task(
                                description=f"Processing {filename}.pdf :page_with_curl:")
                            
                            # Create individual HTML document for this page
                            document = self.create_single_page_html_document(response, url)
                            
                            progress.add_task(
                                description=f"Converting {filename}.pdf :rocket:")
                            
                            # Save and convert individual page
                            html_path = os.path.join(output_dir, f"{filename}.html")
                            
                            self.save_single_page_html(html_path, document)
                            self.convert_single_page_to_pdf(html_path, pdf_path)
                            
                            print(f"[green]✓ Created: {filename}.pdf[/green]")
                        else:
                            print(f"[red]✗ Failed to process: {url} (Status: {response.status_code if response else 'No response'})[/red]")

                print(f"[bold Green]All PDFs are ready! :boom:[/bold Green]")
                print(f"[bold Blue]Output files saved to: {output_dir}[/bold Blue]")
        except Exception as e:
            print(f"Expected error: {e}")

    def get_valid_urls(self):
        """ Get valid URLs from the user """
        valid_urls = []

        while True:
            user_input = typer.prompt(
                "\nEnter the URL(s) separated by comma (,)")
            split_urls = [url.strip() for url in user_input.replace(
                " ", "").split(",") if url.strip()]

            for url in split_urls:
                if not validators.url(url) or not url:
                    self.console.print(
                        "\n[red] :x: Invalid URL. Please enter a valid URL. :x:[/red]")
                else:
                    valid_urls.append(url)

            user_done = typer.confirm(
                "\nAre you done adding URLs?", default=False)

            if user_done:
                break

        return valid_urls

    def main(self, url: str = None, depth: int = 2, recursive: bool = False, output_dir: str = "~/web2pdf_output", rate_limit: int = 5, assemble: bool = False, force: bool = False, use_browser: bool = False):
        """
            Convert web pages to a PDF File.
            Support both single URL with recursive crawling and multiple URLs.
        """
        try:
            # Expand tilde in output directory path
            import os
            output_dir = os.path.expanduser(output_dir)
            
            self.console.print(
                "\n[bold Green] Credits for original idea and code go to: @dvcoolarun :rocket:[/bold Green]",
                "\n[bold Yellow]Feel free to support him by buying him a coffee :coffee: https://www.buymeacoffee.com/web2pdf[/bold Yellow]")
            
            valid_urls = []
            
            if url and recursive:
                # Recursive mode: crawl from a single URL
                self.console.print(f"\n[bold blue]Recursive mode: Starting from {url} with depth {depth}[/bold blue]")
                if not validators.url(url):
                    self.console.print(f"\n[red]Invalid URL: {url}[/red]")
                    return
                
                # Reset state for recursive crawling
                self.visited_urls.clear()
                self.all_urls.clear()
                
                # Start recursive crawling
                self.crawl_urls_recursively(url, depth, rate_limit=rate_limit)
                valid_urls = list(self.all_urls)
                
                self.console.print(f"\n[bold green]Found {len(valid_urls)} URLs to convert to PDF[/bold green]")
                
            elif url and not recursive:
                # Single URL mode
                if not validators.url(url):
                    self.console.print(f"\n[red]Invalid URL: {url}[/red]")
                    return
                valid_urls = [url]
                
            else:
                # Interactive mode: get URLs from user
                self.console.print(
                    "\n[bold red]Please provide the list of URLs to convert to PDF. :link:[/bold red]")
                valid_urls = self.get_valid_urls()

            if valid_urls:
                self.process_urls(valid_urls, output_dir, assemble, force)
            else:
                self.console.print(
                    "\n[red]No URLs provided. Exiting... :bye:[/red]")

        except KeyboardInterrupt:
            self.console.print(
                "[red]Process interrupted by user. Exiting...[/red]")
            raise typer.Exit()

    def is_pdf_response(self, response, url):
        """Determine if the response or URL points to a PDF file"""
        if not response:
            return False

        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' in content_type:
            return True

        parsed = urlparse(url)
        return parsed.path.lower().endswith('.pdf')

    def save_pdf_response(self, response, url, output_dir, force=False):
        """Save a PDF response directly to disk"""
        import os

        filename = self.generate_filename_from_url(url)
        if not filename.lower().endswith('.pdf'):
            filename = f"{filename}.pdf"

        pdf_path = os.path.join(output_dir, filename)

        if not force and os.path.exists(pdf_path):
            print(f"[yellow]⏭️  Skipping {filename} (already exists, use --force to re-download)[/yellow]")
            return

        try:
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"[green]✓ Downloaded PDF: {filename}[/green]")
        except Exception as e:
            print(f"[red]Error saving PDF {filename}: {e}[/red]")

def main_cli(url: str = typer.Argument(None, help="URL to convert to PDF (optional)"),
             depth: int = typer.Option(2, "--depth", "-d", help="Recursive crawl depth (default: 2)"),
             recursive: bool = typer.Option(False, "--recursive", "-r", help="Enable recursive crawling"),
             output_dir: str = typer.Option("~/web2pdf_output", "--output", "-o", help="Output directory for PDF and HTML files (default: ~/web2pdf_output)"),
             rate_limit: int = typer.Option(5, "--rate-limit", help="Seconds to wait between batches of 10 requests (default: 5)"),
             assemble: bool = typer.Option(False, "--assemble", "-a", help="Create a single assembled PDF with all pages combined"),
             force: bool = typer.Option(False, "--force", "-f", help="Force re-processing of existing PDFs (default: skip existing files)"),
             browser: bool = typer.Option(False, "--browser", "-b", help="Use browser rendering for JavaScript-rendered pages (requires Playwright)")):
    """
    Web2PDF - Convert web pages to PDF
    
    Examples:
    - python main.py  # Interactive mode
    - python main.py https://example.com  # Single URL
    - python main.py https://example.com --recursive --depth 3  # Recursive crawl
    """
    # Expand tilde in output directory path
    import os
    output_dir = os.path.expanduser(output_dir)
    
    convertor = Web2PDFConverter(use_browser=browser)
    convertor.main(url, depth, recursive, output_dir, rate_limit, assemble, force, use_browser=browser)

if __name__ == "__main__":
    typer.run(main_cli)
