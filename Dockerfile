# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install necessary tools and libraries
RUN yum update -y && \
    yum groupinstall -y "Development Tools" && \
    yum install -y openssl-devel bzip2-devel libffi-devel wget

# Download and compile Python 3.9
RUN wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz && \
    tar xzf Python-3.9.16.tgz && \
    cd Python-3.9.16 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.9.16 Python-3.9.16.tgz

# Upgrade pip
RUN python3.9 -m ensurepip && \
    python3.9 -m pip install --upgrade pip

# Install zip
RUN yum install -y zip

# Set the working directory in the container
WORKDIR /layer

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python packages
RUN python3.9 -m pip install -r requirements.txt -t python/lib/python3.9/site-packages/

# Create the ZIP file
RUN zip -r layer.zip python

# Set the default command
CMD ["/bin/bash"]