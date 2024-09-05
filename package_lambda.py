#!/usr/bin/env python3

import os
import zipfile
import shutil

# Ensure we're in the /var/task directory
os.chdir('/var/task')

# Create a temporary directory
tmp_package = 'tmp_package'
os.makedirs(tmp_package, exist_ok=True)

# Copy the Lambda function code
shutil.copy('lambda_function.py', tmp_package)

# Copy installed dependencies
site_packages = '/var/lang/lib/python3.9/site-packages'
for item in os.listdir(site_packages):
    s = os.path.join(site_packages, item)
    d = os.path.join(tmp_package, item)
    if os.path.isdir(s):
        shutil.copytree(s, d, symlinks=False, ignore=None)
    else:
        shutil.copy2(s, d)

# Create a ZIP file
with zipfile.ZipFile('lambda_function.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(tmp_package):
        for file in files:
            zipf.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file), tmp_package))

# Clean up
shutil.rmtree(tmp_package)

print("Lambda function packaged as lambda_function.zip")