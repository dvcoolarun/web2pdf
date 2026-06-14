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
    - 🔄 Custom Styling: Tailor the appearance of your PDFs with customizable CSS, allowing you to adjust everything from fonts to background colors.
    - 📄 Additional CSS: Flexibility to add custom CSS for further customization.
    - 🔗 Multi-column Support: Benefit from multi-column support for more complex PDF layouts.
    - 📚 Page Numbers: Add page numbers to your PDFs for easier navigation.
    - 🔢 Table of Contents: Automatically generate a table of contents based on the headings in your HTML.
    - 🚦 Page Breaks: Control page breaks to ensure your PDFs are formatted exactly as you want them.
    - 👍 Much more

## Usage/Installation
To install it right away for all UNIX users (Linux, macOS, etc.), type:
```bash
git clone https://github.com/dvcoolarun/web2pdf.git
```

Then you can use the tool as follows
```bash
pipenv shell
pipenv install
python main.py

OR with Docker ( To save the file from container to directory using mount volume )

docker build -t web2pdf .                    

docker run -it -v $(pwd):/app/ web2pdf

```
Just add the webpage URLs separated by commas, and the tool will convert them to PDFs.


## Development
You can clone the repository and install the package using the following commands
```bash
git clone
cd webp2pdf
pipenv install
```

## Contributing
**This CLI is in its early version, and we encourage the community to help improve code, testing, and additional features. Feel free to contribute to the project by submitting pull requests, reporting issues, or suggesting new features. Your contributions are highly appreciated!**
