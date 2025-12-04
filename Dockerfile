
FROM python:3.12.2

# Set locale to UTF-8
ENV LANG C.UTF-8

# Create a directory for the Django application
RUN mkdir /django

# Copy the requirements file into the container
COPY ./requirements.txt /django/requirements.txt

# Update package lists and install required packages
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential && \
    pip install --no-cache-dir -r /django/requirements.txt


# Clean up unneeded packages and files
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /django

# Create a non-root user
RUN useradd -ms /bin/sh cnb

# Switch to the non-root user
USER cnb