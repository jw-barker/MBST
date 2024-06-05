import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import requests
import shutil

# Function to download the tool and save it to the desktop
def download_tool():
    url = "https://downloads.malwarebytes.com/file/mbstcmd"
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    tool_path = os.path.join(desktop_path, "mb-clean.exe")
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(tool_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            messagebox.showinfo("Success", "Tool downloaded successfully to the Desktop.")
        else:
            messagebox.showerror("Download Error", f"Failed to download the tool. Status code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Exception", f"An error occurred while downloading the tool: {str(e)}")

# Function to run commands with elevated privileges
def run_command_as_admin(command):
    try:
        # Ensure the command is properly quoted
        ps_command = f'Start-Process cmd.exe -ArgumentList \'/c {command}\' -Verb RunAs'
        result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True)
        
        # Check for errors and display them
        if result.returncode != 0:
            messagebox.showerror("Error", f"Command failed with error: {result.stderr}")
    except Exception as e:
        messagebox.showerror("Exception", f"An error occurred while running the command: {str(e)}")

def clean_with_password():
    password = password_entry.get()
    if not password:
        messagebox.showerror("Input Error", "Please enter the Tamper Protection password.")
        return
    
    command = f"cd %userprofile%\\desktop && mb-clean.exe /y /cleanup /noreboot /nopr /epatamperpw \"{password}\""
    run_command_as_admin(command)

def clean_without_password():
    command = "cd %userprofile%\\desktop && mb-clean.exe /y /cleanup /noreboot /nopr /epatoken \"NoTamperProtection\""
    run_command_as_admin(command)

def final_cleanup():
    command = "cd %userprofile%\\desktop && mb-clean.exe /y /cleanup /noreboot /nopr"
    run_command_as_admin(command)

def check_log_file():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_filename = "mbst-clean-results.txt"
    
    # Possible locations for the log file
    locations = [
        os.path.join(os.getenv('LOCALAPPDATA'), "Temp", log_filename),
        os.path.join(os.getenv('SystemRoot'), "Temp", log_filename)
    ]
    
    # Check each location for the log file
    for location in locations:
        if os.path.exists(location):
            try:
                shutil.copy(location, desktop_path)
                messagebox.showinfo("Success", f"Log file copied to Desktop from {location}.")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy log file: {str(e)}")
                return
    
    messagebox.showinfo("Info", "Log file not found in expected locations.")

# Create the main window
root = tk.Tk()
root.title("Malwarebytes Cleanup Tool")

# Instruction label
tk.Label(root, text="Follow the steps below to clean up Malwarebytes Endpoint Agent:").pack(pady=10)

# Download button
tk.Button(root, text="Download Tool", command=download_tool).pack(pady=10)

# Step 1: Tamper Protection Enabled
tk.Label(root, text="Step 1: Enter Tamper Protection password and click 'Clean with Password':").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)
tk.Button(root, text="Clean with Password", command=clean_with_password).pack(pady=10)

# Step 2: Tamper Protection Disabled
tk.Label(root, text="Step 2: If Tamper Protection is disabled, click 'Clean without Password':").pack(pady=5)
tk.Button(root, text="Clean without Password", command=clean_without_password).pack(pady=10)

# Step 3: Final Cleanup
tk.Label(root, text="Step 3: After reboot, click 'Final Cleanup':").pack(pady=5)
tk.Button(root, text="Final Cleanup", command=final_cleanup).pack(pady=10)

# Instruction to verify directories
tk.Label(root, text="Verify the following directories are deleted after reboot:\n"
                     "C:\\Program Files\\Malwarebytes Endpoint Agent\n"
                     "C:\\ProgramData\\Malwarebytes Endpoint Agent\n"
                     "C:\\Program Files\\Malwarebytes\n"
                     "C:\\ProgramData\\Malwarebytes").pack(pady=20)

# New button to check log file
tk.Label(root, text="Check for mbst-clean-results.txt log file:").pack(pady=5)
tk.Button(root, text="Check Log File", command=check_log_file).pack(pady=10)

# Start the GUI event loop
root.mainloop()