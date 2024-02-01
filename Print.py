"""
    Refactor the code // Functional
    Error Handling // TEST CASES
    CLI AND RICH INTEGRATION ?
    Column option provided or not ?
"""

import gevent.monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import grequests
from fake_useragent import UserAgent
from readability import Document
from weasyprint import HTML

import dominate
from dominate import tags as tags
from dominate.util import raw


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
        columns: 2;
        column-rule: 2px solid #f9f9f9;
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

""" Fake UserAgent """
user_agent = UserAgent()
headers = {'User-Agent': user_agent.random}

""" List of sample url's to process """
url_list = [
    'https://nathanbarry.com/wealth-creation/',
    'https://humanparts.medium.com/good-enough-is-just-fine-1126b09cbea',
    'https://blog.stephsmith.io/how-to-be-great/',
    'https://radreads.co/being-heroic-about-consistency/',
]

""" Making asynchrnous requests """
request_urls = (grequests.get(url, headers=headers) for url in url_list)
request_responses = grequests.map(request_urls)

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

for index, each_response in enumerate(request_responses):
    if each_response:
        doc = Document(each_response.content)
        title = doc.title()
        main_content = doc.summary()

        with document:
            with tags.div(id='article-body'):
                tags.h1(title, id='heading' + str(index))
                tags.p(cls='top-border')
                tags.div(raw(main_content))
            tags.p(cls='page-break')

""" Writing the HTML document to file """
with open("print.html", "w+") as output_file:
    output_file.write(document.render())

""" Converting HTML to PDF using WeasyPrint"""
HTML('print.html').write_pdf('print.pdf')