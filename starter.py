from subprocess import run
from time import sleep

# Path and name to the script you are trying to start
file_path = "main.py" 

restart_timer = 0.5
def start_script():
    try:
        # Make sure 'python' command is available
        run("python "+file_path, check=True) 
    except:
        # Script crashed, lets restart it!
        handle_crash()

def handle_crash():
    print('Crashed once')
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_script()

start_script()
