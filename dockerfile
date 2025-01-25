# python
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
# Install system dependencies
# Install system dependencies for WeasyPrint
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpango1.0-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gobject-introspection \
    && rm -rf /var/lib/apt/lists/*


COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv

RUN pipenv install --system --deploy

COPY . .

EXPOSE 80

ENV NAME=Web2PDF

# Run the application
CMD ["python", "main.py"]