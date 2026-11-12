FROM public.ecr.aws/lambda/python:3.10

# Install system dependencies required for compilation, math, and HDF5 model files
RUN yum install -y gcc gcc-c++ make cmake git zlib-devel libjpeg-devel hdf5-devel

# Set the working directory inside the Lambda container
WORKDIR /var/task

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy all application files (including app.py and churn_model.keras) into the container
COPY . .

# Set the Lambda handler command
CMD [ "app.handler" ]
