FROM python:3.12
# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set the locale to UTF-8
ENV LANG=C.UTF-8
ENV PYTHONPATH=~/api/venv/bin
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code to the working directory
COPY . .

# Set environment variables
#ENV FLASK_ENV=production
ENV FLASK_ENV=development
ENV FLASK_APP=app.py
ENV DEBUG=1

# Volume for code changes
VOLUME /app

# Expose port
EXPOSE 5030

# Run Flask using WSGI server (gunicorn) with web configuration options
#CMD ["gunicorn", "--workers=4", "--threads=2", "--bind=0.0.0.0:5353", "app:app"]
#CMD ["flask -A app run -h 0.0.0.0 -p 5030"]
