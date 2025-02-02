FROM python:3.12-slim

WORKDIR /app

# Copy only the files needed to install dependencies first
COPY requirements.txt .
COPY setup.py .
COPY README.md .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Command to run the application
ENTRYPOINT ["python", "warc_processor_main.py"]
CMD []
