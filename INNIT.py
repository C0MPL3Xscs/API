import subprocess

try:
    subprocess.check_call(['python', 'manage.py', 'migrate'])
    print("DONE")
except subprocess.CalledProcessError as e:
    print("NOT DONE", e)
