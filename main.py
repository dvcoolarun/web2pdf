#!/usr/bin/python

from dominate.util import raw
from dominate import tags as tags
import dominate
from weasyprint import HTML
from readability import Document
from fake_useragent import UserAgent
import grequests
import validators
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from rich import print
import typer
import gevent.monkey as curious_george
curious_george.patch_all(thread=False, select=False)
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

    def __init__(self):
        self.console = Console()

    def make_async_request(self, url_list, headers):
        """ Making asynchrnous requests """
        try:
            request_urls = (grequests.get(url, headers=headers)
                            for url in url_list)
            return grequests.map(request_urls)
        except Exception as e:
            print(f"Error making asynchronous request: (e)")
            return []

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

    def save_html_to_file(self, html_document):
        """ Writing the HTML document to file """
        try:
            with open("print.html", "w+") as output_file:
                output_file.write(html_document.render())
        except Exception as e:
            print(f"Error saving HTML to file: {e}")

    def convert_html_to_pdf(self, html_filename="print.html", pdf_filename="print.pdf"):
        """ Converting HTML to PDF using WeasyPrint"""
        try:
            HTML(html_filename).write_pdf(pdf_filename)
        except Exception as e:
            print(f"Error converting HTML to PDF: {e}")

    def process_urls(self, url_list):
        """ Processing the URLs """
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

                progress.add_task(
                    description="Preparing HTML document. :page_with_curl:")
                document = self.create_html_document(request_responses)

                progress.add_task(
                    description="Preparing content to add. :pencil:")
                html_document = self.process_and_add_content(
                    request_responses, document)

                progress.add_task(
                    description="HTML is getting ready to save. :floppy_disk:")
                self.save_html_to_file(html_document)

                progress.add_task(
                    description="Converting HTML to PDF :rocket:")
                self.convert_html_to_pdf()

                print("[bold Green]Your PDF is ready! :boom:[/bold Green]")
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

    def main(self):
        """
            Convert web pages to a PDF File.
            Provide list of URL's as command line.
        """
        try:
            self.console.print(
                "\n[bold Green]Welcome to Web2PDF! By @dvcoolarun :rocket:[/bold Green]",
                "\n[bold Yellow]If this CLI is helpful to you, please consider supporting me by buying me a coffee :coffee: https://www.buymeacoffee.com/web2pdf[/bold Yellow]")
            self.console.print(
                "\n[bold red]Please provide the list of URLs to convert to PDF. :link:[/bold red]")

            valid_urls=self.get_valid_urls()

            if valid_urls:
                self.process_urls(valid_urls)
            else:
                self.console.print(
                    "\n[red]No URLs provided. Exiting... :bye:[/red]")

        except KeyboardInterrupt:
            self.console.print(
                "[red]Process interrupted by user. Exiting...[/red]")
            raise typer.Exit()

if __name__ == "__main__":
    convertor=Web2PDFConverter()
    typer.run(convertor.main)
