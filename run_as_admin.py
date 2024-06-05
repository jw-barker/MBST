import ctypes
import sys
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join([sys.executable] + sys.argv), None, 1)
    except Exception as e:
        sys.stderr.write(f"Failed to elevate privileges: {str(e)}\n")
        sys.exit(1)

if not is_admin():
    run_as_admin()
    sys.exit(0)

# If running as admin, execute the main script
exec(open("main_app.py").read())