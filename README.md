# Web2pdf

## CLI to convert webpages to PDFs
-- Webp2pdf is a command line tool that converts webpages to Beautifully formatted pdfs.

**This CLI is in its early version, and we encourage the community to help improve code, testing, and additional features. Feel free to contribute to the project by submitting pull requests, reporting issues, or suggesting new features. Your contributions are highly appreciated!**

**If this project proves useful to you in any way, please consider supporting me by buying a coffee! ** <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="web2pdf" data-color="#FF5F5F" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#ffffff" data-coffee-color="#FFDD00" ></script> **


![webp2pdf](https://github.com/dvcoolarun/web2pdf/blob/dev/assets/web2pdf.png?raw=true)


## Features
- Features
    - 💥 Batch Conversion: Convert multiple webpages to PDFs in one go.
    - 🔄 Custom Styling: Tailor the appearance of your PDFs with customizable CSS, allowing you to adjust everything from fonts to background colors.
    - 📄 Additional CSS: Flexibility to add custom CSS for further customization.
    - 🔗 Multi-column Support: Benefit from multi-column support for more complex PDF layouts.
    - 📚 Page Numbers: Add page numbers to your PDFs for easier navigation.
    - 🔢 Table of Contents: Automatically generate a table of contents based on the headings in your HTML.
    - 🔢 Page Numbers: Add page numbers to your PDFs for easier navigation.
    - 🚦 Page Breaks: Control page breaks to ensure your PDFs are formatted exactly as you want them.
    - 👍 Much more


## Usage/Installation
You can download the package from pypi using pip
```bash
pip install webp2pdf
```

Then you can use the tool as follows
```bash
webp2pdf https://www.paulgraham.com/avg.html, https://www.paulgraham.com/determination.html
```
Just add the webpage URLs separated by commas, and the tool will convert them to PDFs.


## Development
You can clone the repository and install the package using the following commands
```bash
git clone
cd webp2pdf
pipenv install
```