import subprocess

# Define the path to the requirements.txt file
requirements_file = 'requirements.txt'

# Install requirements using pip
try:
    subprocess.call(['pip', 'install', '-r', requirements_file])
    print("Requirements installation successful.")
except subprocess.CalledProcessError as e:
    print("Error installing requirements: {}".format(e))