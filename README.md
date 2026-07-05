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
To get started run:
```bash
git clone https://github.com/dvcoolarun/web2pdf.git
```

### System Dependencies

WeasyPrint requires system libraries that must be installed before installing Python packages. Install them based on your operating system:

#### macOS (using Homebrew)
```bash
brew install cairo pango gdk-pixbuf libffi pkg-config
```

**Note:** If you encounter library loading errors after installation, see the [Troubleshooting](#troubleshooting) section below.

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpango1.0-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gobject-introspection
```

#### Linux (Fedora/RHEL/CentOS)
```bash
sudo dnf install -y \
    gcc \
    python3-devel \
    libffi-devel \
    openssl-devel \
    libxml2-devel \
    libxslt-devel \
    libjpeg-turbo-devel \
    pango-devel \
    cairo-devel \
    gobject-introspection-devel
```

### With Conda (Recommended)
> You need to install system dependencies (see above) PRIOR TO creating the conda environment.  The order matters.  If you jumped the gun and created your conda environment already like a boss, that unfortunately will backfire and land you in the troubleshooting section below.  Sorry!

```bash
# Install system dependencies first (see System Dependencies section above)
# Then create and activate conda environment
conda env create -f environment.yml
conda activate web2pdf

# Run the tool
python main.py
```

### Troubleshooting

#### macOS: "cannot load library 'libgobject-2.0-0'" Error

If you encounter this error after installing system dependencies, WeasyPrint may not be able to find the libraries. Try one of these solutions:

**Option 1: Set environment variables (Recommended)**
Add to your shell configuration file (`~/.zshrc` for zsh or `~/.bash_profile` for bash):
```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
```
Then reload: `source ~/.zshrc` (or `source ~/.bash_profile`)

**Option 2: Reinstall WeasyPrint**
After installing system dependencies, reinstall WeasyPrint:
```bash
conda activate web2pdf
pip uninstall weasyprint -y
pip install weasyprint
```

**Option 3: Use conda-forge WeasyPrint (Alternative)**
You can try installing WeasyPrint from conda-forge which may handle dependencies better:
```bash
conda activate web2pdf
conda install -c conda-forge weasyprint
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

# Adjust rate limiting (default: 5 seconds between batches of 10 requests)
python main.py https://example.com --recursive --rate-limit 3

# Create a single assembled PDF with all pages combined
python main.py https://example.com --recursive --assemble

# Force re-processing of existing PDFs (default: skip existing files)
python main.py https://example.com --recursive --force
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
git clone https://github.com/dvcoolarun/web2pdf.git
cd web2pdf
pip install -r requirements.txt
```

### Running Tests
```bash
pip install pytest
python -m pytest tests/ -v
```

## Contributing
**This CLI is in its early version, and we encourage the community to help improve code, testing, and additional features. Feel free to contribute to the project by submitting pull requests, reporting issues, or suggesting new features. Your contributions are highly appreciated!**
