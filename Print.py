from time import time
from urllib import request
import gevent.monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

import grequests
from fake_useragent import UserAgent
from readability import Document
from weasyprint import HTML

import dominate
from dominate import tags as tags
from dominate.util import raw

app = typer.Typer()
console = Console()

""" Styles for the PDF """
css_styles = """
    body {
        hyphens: auto;
        font-size: 12px;
        font-weight: 100;
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
        column-gap: 2em;
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
        padding: 16px 0;
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
        margin: 1.5em 10px;
        padding: 0.5em 10px;
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

def make_async_request(url_list, headers):
    """ Making asynchrnous requests """
    try:
        request_urls = (grequests.get(url, headers=headers) for url in url_list)
        return grequests.map(request_urls)
    except Exception as e:
        print(f"Error making asynchronous request: (e)")
        return []

def create_html_document(request_responses):
    """ Creating HTML document with Table of Contents"""
    try:
        document = dominate.document()
        with document.head:
            tags.style(raw(css_styles))
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

def process_and_add_content(request_responses, document):
    """ Processing the response and adding content to the HTML document """
    print(request_responses, document)
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

def save_html_to_file(html_document):
    """ Writing the HTML document to file """
    print("in the save_html_to_file", html_document)
    try:
        with open("print.html", "w+") as output_file:
            output_file.write(html_document.render())
    except Exception as e:
        print(f"Error saving HTML to file: {e}")

def convert_html_to_pdf(html_filename="print.html", pdf_filename="print.pdf"):
    """ Converting HTML to PDF using WeasyPrint"""
    try:
        HTML(html_filename).write_pdf(pdf_filename)
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")

def process_urls(url_list):
    """ Fake UserAgent """
    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.random}

    try:
        with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        ) as progress:
            progress.add_task(description="Processing...")
            request_responses = make_async_request(url_list, headers)

            progress.add_task(description="Preparing HTML document.")
            document = create_html_document(request_responses)

            progress.add_task(description="Preparing...")
            final_document = process_and_add_content(request_responses, document)

            progress.add_task(description="HTML is getting ready.")
            save_html_to_file(final_document)

            progress.add_task(description="Converting HTML TO PDF.")
            convert_html_to_pdf()

            print("Your PDF is ready")
    except Exception as e:
        print(f"Expected error: {e}")

@app.command()
def main():
    """
        Convert web pages to a PDF File.
        Provide list of URL's as command line.
    """
    try:
        console.print("[bold Green]Welcome to the Web to PDF Converter![/bold Green]")
        console.print("[bold red]~~~ Please Enter the URLs you want to convert ~~~[/bold red]")
        urls = []
        while True:
            url = typer.prompt("Enter the URL")
            urls.append(url)

            done = typer.confirm("Are you done adding URLs?", default=False)

            if done:
                break
        if urls:
            process_urls(urls)
        else:
            console.print("[red]No URLs provided. Exiting...[/red]")

    except KeyboardInterrupt:
        console.print("[red]Process interrupted by user. Exiting...[/red]")

if __name__ == "__main__":
    app()
