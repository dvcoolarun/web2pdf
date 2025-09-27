## Production Deployment

For production use cases requiring managed infrastructure and scaling:
- **Production API**: DocuQueue offers a managed document generation service ($5/mo) at [docuqueue.com](https://docuqueue.com/) — no infrastructure maintenance required.

<img width="690" height="315" alt="Screenshot 2026-06-14 at 2 39 33 PM" src="https://github.com/user-attachments/assets/b1fa35d1-96fc-4725-afc8-078b274741ba" />


# Web2pdf

## CLI to convert webpages to PDFs
Web2pdf is a command line tool that converts webpages to Beautifully formatted pdfs.

![webp2pdf](https://github.com/dvcoolarun/web2pdf/blob/main/assets/web2pdf.png?raw=true)

## Features
- Features
    - 💥 Batch Conversion: Convert multiple webpages to PDFs in one go.
    - 🕷️ Recursive Crawling: Crawl and convert entire websites starting from a single URL with configurable depth.
    - 🔄 Custom Styling: Tailor the appearance of your PDFs with customizable CSS, allowing you to adjust everything from fonts to background colors.
    - 📄 Additional CSS: Flexibility to add custom CSS for further customization.
    - 🔗 Multi-column Support: Benefit from multi-column support for more complex PDF layouts.
    - 📚 Page Numbers: Add page numbers to your PDFs for easier navigation.
    - 🔢 Table of Contents: Automatically generate a table of contents based on the headings in your HTML.
    - 🚦 Page Breaks: Control page breaks to ensure your PDFs are formatted exactly as you want them.
    - 🌐 Smart Link Filtering: Automatically filters to same-domain links to avoid external sites.
    - 👍 Much more

## Usage/Installation
To install it right away for all UNIX users (Linux, macOS, etc.), type:
```bash
git clone https://github.com/dvcoolarun/web2pdf.git
```

Then you can use the tool as follows

### With Pipenv
```bash
pipenv shell
pipenv install
python main.py
```

### With Conda (Recommended)
```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate web2pdf

# Run the tool
python main.py
```

### With Docker ( To save the file from container to directory using mount volume )
```bash
docker build -t web2pdf .                    
docker run -it -v $(pwd):/app/ web2pdf
```

## Usage Examples

### Interactive Mode (Original)
```bash
python main.py
# Enter URLs when prompted
```

### Single URL
```bash
python main.py https://example.com
```

### Recursive Crawling
```bash
# Crawl a website with default depth of 2
python main.py https://example.com --recursive

# Crawl with custom depth
python main.py https://example.com --recursive --depth 3

# Short form
python main.py https://example.com -r -d 3

# Use default output directory (~/web2pdf_output)
python main.py https://example.com --recursive

# Specify custom output directory (will be created if it doesn't exist)
python main.py https://example.com --recursive --output ./my_pdfs
```

The recursive mode will:
- Start from the provided URL
- Crawl all links on the same domain
- Go up to the specified depth (default: 2)
- Convert each found page into a separate PDF file
- Generate filenames based on the URL structure (e.g., `web2pdf.pdf` for `github.com/zaphodbeeblebrox3rd/web2pdf`)


## Development
You can clone the repository and install the package using the following commands
```bash
git clone
cd webp2pdf
pipenv install
```

## Contributing
**This CLI is in its early version, and we encourage the community to help improve code, testing, and additional features. Feel free to contribute to the project by submitting pull requests, reporting issues, or suggesting new features. Your contributions are highly appreciated!**
