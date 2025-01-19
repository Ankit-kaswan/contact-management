# Use official Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install build dependencies (e.g., gcc, python3-dev, and libpq-dev)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Copy the wait-for-it script
COPY wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Copy entrypoint script and set permissions
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the port the app will run on
EXPOSE 8000

# Set the entry point to the entrypoint.sh script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Command to run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
