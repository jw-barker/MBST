import sys
import subprocess
import os
import requests
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QVBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt

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
            QMessageBox.information(None, "Success", "Tool downloaded successfully to the Desktop.")
        else:
            QMessageBox.critical(None, "Download Error", f"Failed to download the tool. Status code: {response.status_code}")
    except Exception as e:
        QMessageBox.critical(None, "Exception", f"An error occurred while downloading the tool: {str(e)}")

# Function to run commands with elevated privileges
def run_command_as_admin(command):
    try:
        ps_command = f'Start-Process cmd.exe -ArgumentList \'/c {command}\' -Verb RunAs'
        result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True)

        if result.returncode != 0:
            QMessageBox.critical(None, "Error", f"Command failed with error: {result.stderr}")
    except Exception as e:
        QMessageBox.critical(None, "Exception", f"An error occurred while running the command: {str(e)}")

def clean_with_password():
    password = password_entry.text()
    if not password:
        QMessageBox.critical(None, "Input Error", "Please enter the Tamper Protection password.")
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

    locations = [
        os.path.join(os.getenv('LOCALAPPDATA'), "Temp", log_filename),
        os.path.join(os.getenv('SystemRoot'), "Temp", log_filename)
    ]

    for location in locations:
        if os.path.exists(location):
            try:
                shutil.copy(location, desktop_path)
                QMessageBox.information(None, "Success", f"Log file copied to Desktop from {location}.")
                return
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to copy log file: {str(e)}")
                return

    QMessageBox.information(None, "Info", "Log file not found in expected locations.")

def generate_diagnostic_logs():
    command = '"C:\\Program Files\\Malwarebytes Endpoint Agent\\Useragent\\EACmd.exe" -diag'
    run_command_as_admin(command)
    QMessageBox.information(None, "Action", "Diagnostic logs generation process initiated.")

def set_loglevel_debug():
    command = '"C:\\Program Files\\Malwarebytes Endpoint Agent\\MBCloudEA.exe" -loglevel=debug'
    run_command_as_admin(command)

def set_loglevel_info():
    command = '"C:\\Program Files\\Malwarebytes Endpoint Agent\\MBCloudEA.exe" -loglevel=info'
    run_command_as_admin(command)

def toggle_loglevel(state):
    if state == Qt.Checked:
        set_loglevel_debug()
    else:
        set_loglevel_info()

def check_services():
    services = ["MBAMService", "MBEndpointAgent", "EAServiceMonitor"]
    running_services = []
    stopped_services = []
    missing_services = []

    for service in services:
        try:
            result = subprocess.run(['sc', 'query', service], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                running_services.append(service)
            elif "STOPPED" in result.stdout:
                stopped_services.append(service)
            else:
                missing_services.append(service)
        except Exception as e:
            missing_services.append(service)

    if not missing_services and not stopped_services:
        QMessageBox.information(None, "Services Check", "All services are running.")
    else:
        message = ""
        if missing_services:
            message += f"Missing services: {', '.join(missing_services)}.\n"
        if stopped_services:
            message += f"Stopped services: {', '.join(stopped_services)}."
        if stopped_services:
            restart = QMessageBox.question(None, "Restart Services", f"{message}\nWould you like to restart the stopped services?", QMessageBox.Yes | QMessageBox.No)
            if restart == QMessageBox.Yes:
                for service in stopped_services:
                    run_command_as_admin(f'sc start {service}')

class CleanupToolWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Malwarebytes Business Support Tool")
        layout = QVBoxLayout()

        step_label = QLabel("Follow the steps below to clean up Malwarebytes Endpoint Agent:")
        step_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(step_label)

        download_button = QPushButton("Download Tool")
        download_button.setFixedSize(200, 30)
        download_button.clicked.connect(download_tool)
        layout.addWidget(download_button, alignment=Qt.AlignCenter)

        step1_label = QLabel("Step 1: Enter Tamper Protection password and click 'Clean with Password':")
        step1_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(step1_label)

        global password_entry
        password_entry = QLineEdit()
        password_entry.setEchoMode(QLineEdit.Password)
        password_entry.setFixedSize(200, 30)
        layout.addWidget(password_entry, alignment=Qt.AlignCenter)

        clean_with_password_button = QPushButton("Clean with Password")
        clean_with_password_button.setFixedSize(200, 30)
        clean_with_password_button.clicked.connect(clean_with_password)
        layout.addWidget(clean_with_password_button, alignment=Qt.AlignCenter)

        step2_label = QLabel("Step 2: If Tamper Protection is disabled, click 'Clean without Password':")
        step2_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(step2_label)

        clean_without_password_button = QPushButton("Clean without Password")
        clean_without_password_button.setFixedSize(200, 30)
        clean_without_password_button.clicked.connect(clean_without_password)
        layout.addWidget(clean_without_password_button, alignment=Qt.AlignCenter)

        step3_label = QLabel("Step 3: After reboot, click 'Final Cleanup':")
        step3_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(step3_label)

        final_cleanup_button = QPushButton("Final Cleanup")
        final_cleanup_button.setFixedSize(200, 30)
        final_cleanup_button.clicked.connect(final_cleanup)
        layout.addWidget(final_cleanup_button, alignment=Qt.AlignCenter)

        verify_label = QLabel(
            "Verify the following directories are deleted after reboot:\n"
            "C:\\Program Files\\Malwarebytes Endpoint Agent\n"
            "C:\\ProgramData\\Malwarebytes Endpoint Agent\n"
            "C:\\Program Files\\Malwarebytes\n"
            "C:\\ProgramData\\Malwarebytes"
        )
        verify_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(verify_label)

        check_log_file_button = QPushButton("Check Log File")
        check_log_file_button.setFixedSize(200, 30)
        check_log_file_button.clicked.connect(check_log_file)
        layout.addWidget(check_log_file_button, alignment=Qt.AlignCenter)

        back_button = QPushButton("Back")
        back_button.setFixedSize(200, 30)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def go_back(self):
        self.close()
        main_window.show()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Malwarebytes Business Support Tool")
        layout = QVBoxLayout()

        instructions = QLabel(
            'The Business Support Tool removes Nebula and OneView products from endpoints. This includes files, settings, and license information. '
            'First, attempt to uninstall the endpoint agent by deleting it in Nebula or OneView. '
            'See how to uninstall endpoints from <a href="https://support.threatdown.com/hc/en-us/articles/4413799100435">Nebula</a> or '
            '<a href="https://support.threatdown.com/hc/en-us/articles/4413799443347">OneView</a>.'
            '<br><br>'
            'Make sure to have your Tamper Protection uninstall password or that Tamper Protection is turned off, as you will need to know this to run the tool. '
            'For more information, check the corresponding article for your console: '
            '<br>'
            '<center><a href="https://support.threatdown.com/hc/en-us/articles/4413799066643">Tamper protection policy settings in Nebula</a></center>'
            '<center><a href="https://support.threatdown.com/hc/en-us/articles/4413802883987">Tamper protection policy settings in OneView</a></center>'
        )
        instructions.setOpenExternalLinks(True)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        loglevel_checkbox = QCheckBox("Enable Debug Log Level")
        loglevel_checkbox.stateChanged.connect(toggle_loglevel)
        layout.addWidget(loglevel_checkbox, alignment=Qt.AlignCenter)

        cleanup_tool_button = QPushButton("Remove the Endpoint Agent")
        cleanup_tool_button.setFixedSize(200, 30)
        cleanup_tool_button.clicked.connect(self.show_cleanup_tool)
        layout.addWidget(cleanup_tool_button, alignment=Qt.AlignCenter)

        diagnostic_logs_button = QPushButton("Generate Diagnostic Logs")
        diagnostic_logs_button.setFixedSize(200, 30)
        diagnostic_logs_button.clicked.connect(generate_diagnostic_logs)
        layout.addWidget(diagnostic_logs_button, alignment=Qt.AlignCenter)

        check_services_button = QPushButton("Check Services")
        check_services_button.setFixedSize(200, 30)
        check_services_button.clicked.connect(check_services)
        layout.addWidget(check_services_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def show_cleanup_tool(self):
        self.hide()
        self.cleanup_tool_window = CleanupToolWindow()
        self.cleanup_tool_window.show()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())