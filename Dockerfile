# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /llm-usage-monitoring

# Copy the current directory contents into the container at /llm-usage-monitoring
COPY . /llm-usage-monitoring

# Force a fresh installation of dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]