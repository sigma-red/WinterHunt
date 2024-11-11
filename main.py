import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import winrm

REMOTE_TOOL_DIR = "C:\\Tools"  # Directory to place tools on the remote host
PS1_DIRECTORY = ".\\powershell_scripts"  # Directory containing .ps1 files

def create_winrm_session(host, username, password):
    """
    Creates a persistent WinRM session with NTLM authentication.
    """
    try:
        session = winrm.Session(f'http://{host}:5985/wsman', auth=(username, password), transport="ntlm")
        return session
    except Exception as e:
        return f"Connection Error on {host}: {e}"

def execute_powershell_script(script_content):
    """
    Execute a PowerShell script content locally and return the output.
    """
    try:
        process = subprocess.Popen(["powershell", "-Command", script_content],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        if process.returncode == 0:
            return output
        else:
            return f"Error: {error}"
    except Exception as e:
        return f"Exception: {e}"

def execute_remote_powershell_script(session, script_content):
    """
    Execute a PowerShell script content on a remote host via WinRM.
    """
    try:
        result = session.run_ps(script_content)
        return result.std_out.decode() if result.status_code == 0 else f"Error: {result.std_err.decode()}"
    except Exception as e:
        return f"Exception: {e}"

def load_ps1_files(directory):
    """
    Loads .ps1 files from the specified directory.
    """
    return [f for f in os.listdir(directory) if f.endswith('.ps1')]

def upload_tool_via_network_share(session, file_name, network_share_path):
    """
    Uses PowerShell Remoting with Invoke-Command to copy a file from a network share to the remote host.
    :param session: The WinRM session.
    :param file_name: The name of the file to copy (without path).
    :param network_share_path: The UNC path to the selected network share.
    :return: Result of the file copy command.
    """
    # Remote path where the file will be copied
    remote_path = os.path.join(REMOTE_TOOL_DIR, file_name)

    # PowerShell command to create the directory if it doesn’t exist
    create_dir_command = f"New-Item -ItemType Directory -Path '{REMOTE_TOOL_DIR}' -Force"
    create_dir_result = session.run_ps(create_dir_command)
    if create_dir_result.status_code == 0:
        print(f"Directory creation success: {REMOTE_TOOL_DIR} exists or was created.")
    else:
        print(f"Directory creation error: {create_dir_result.std_err.decode()}")
        return f"Failed to create directory on remote host: {create_dir_result.std_err.decode()}"

    # PowerShell command to copy the file from the network share to the remote directory
    copy_command = f"""
    Invoke-Command -ScriptBlock {{
        if (Test-Path -Path '{network_share_path}\\{file_name}') {{
            Write-Output 'Source file found on network share.'
            Copy-Item -Path '{network_share_path}\\{file_name}' -Destination '{remote_path}' -Force
            if (Test-Path -Path '{remote_path}') {{
                Write-Output 'File successfully copied to remote directory.'
            }} else {{
                Write-Output 'File copy failed: file not found in remote directory after copy.'
            }}
        }} else {{
            Write-Output 'Source file not found on network share.'
        }}
    }}
    """
    copy_result = session.run_ps(copy_command)
    copy_output = copy_result.std_out.decode()
    copy_error = copy_result.std_err.decode()

    print("Copy Command Output:")
    print(copy_output)
    print("Copy Command Error (if any):")
    print(copy_error)

    if "Source file not found on network share." in copy_output:
        return f"Error: Source file '{file_name}' not found on network share '{network_share_path}'."
    elif "File successfully copied to remote directory." in copy_output:
        return f"Successfully uploaded {file_name} to {remote_path}."
    elif "File copy failed" in copy_output:
        return f"Error copying {file_name}: {copy_output}"
    else:
        return f"Unknown error during copy: {copy_output or copy_error}"

class CybersecurityToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cybersecurity Artifact Hunter")

        # Initialize history storage and file paths for upload
        self.history = {}
        self.selected_files = []
        self.network_share_path = ""  # Dynamically set by Select Tool Files

        # Configure the root grid to make it resizable
        root.grid_rowconfigure(10, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Hosts input for multiple hosts or IPs
        tk.Label(root, text="Hosts (comma-separated):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.host_entry = tk.Entry(root, width=50)
        self.host_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Username and Password fields for remote connection
        tk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = tk.Entry(root, show="*", width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Buttons for selecting files and sending to host
        tk.Button(root, text="Select Tool Files (Network Share Drive)", command=self.select_tool_files).grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        tk.Button(root, text="Send to Host", command=self.send_tools_to_host).grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # PowerShell script selection dropdown
        # Load PowerShell scripts from directory and populate dropdown
        self.ps1_files = load_ps1_files(PS1_DIRECTORY)
        tk.Label(root, text="Select PowerShell Script:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.script_combobox = ttk.Combobox(root, values=self.ps1_files, width=30)
        self.script_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.script_combobox.set("Select a Script")
        self.script_combobox.bind("<<ComboboxSelected>>", self.on_script_select)

        # Editable text area to display and edit the selected script
        tk.Label(root, text="Script to Run:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.script_text = tk.Text(root, height=10, width=60)
        self.script_text.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # History dropdown to view previous command outputs
        tk.Label(root, text="View History:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.history_combobox = ttk.Combobox(root, width=50, state="readonly")
        self.history_combobox.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        self.history_combobox.bind("<<ComboboxSelected>>", self.on_history_select)

        # Output area with resizing configuration
        self.output_text = tk.Text(root, height=10, width=60)
        self.output_text.grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Command preview area for debugging
        self.command_preview = tk.Label(root, text="", wraplength=500, anchor="w", justify="left")
        self.command_preview.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Run Locally, Run Remotely, Export Results, and Export History buttons
        tk.Button(root, text="Run Locally", command=self.run_local_script).grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        tk.Button(root, text="Run Remotely", command=self.run_remote_script).grid(row=7, column=1, padx=10, pady=5, sticky="ew")
        tk.Button(root, text="Export Results", command=self.export_results).grid(row=8, column=0, padx=10, pady=5, sticky="ew")
        tk.Button(root, text="Export History", command=self.export_history).grid(row=8, column=1, padx=10, pady=5, sticky="ew")

    def on_script_select(self, event):
        """Load selected script contents into the editable text area, handling BOM if present."""
        selected_script = self.script_combobox.get()
        self.selected_script_path = os.path.join(PS1_DIRECTORY, selected_script)
        with open(self.selected_script_path, 'r', encoding='utf-8-sig') as file:
            script_content = file.read()
            self.script_text.delete("1.0", tk.END)  # Clear previous content
            self.script_text.insert(tk.END, script_content)  # Load new content

    def select_tool_files(self):
        """Select local tool files to upload from the shared directory."""
        self.selected_files = filedialog.askopenfilenames(title="Select Tool Files")
        if self.selected_files:
            # Update NETWORK_SHARE_PATH to the directory of the selected files
            self.network_share_path = os.path.dirname(self.selected_files[0])
            selected_files_text = "\n".join(os.path.basename(f) for f in self.selected_files)
            self.command_preview.config(text=f"Selected files for upload from {self.network_share_path}:\n{selected_files_text}")
        else:
            self.command_preview.config(text="No files selected for upload.")

    def send_tools_to_host(self):
        """Send selected tool files to the remote hosts."""
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files selected for upload. Please select tool files first.")
            return
        if not self.network_share_path:
            messagebox.showwarning("Warning", "Network share path not set. Please select files from a network share.")
            return

        hosts = self.host_entry.get().split(',')
        username = self.username_entry.get()
        password = self.password_entry.get()

        for host in hosts:
            host = host.strip()
            if not host:
                continue

            session = create_winrm_session(host, username, password)
            if isinstance(session, str):
                self.display_output(host, session)
            elif session:
                for file_path in self.selected_files:
                    file_name = os.path.basename(file_path)
                    upload_result = upload_tool_via_network_share(session, file_name, self.network_share_path)
                    self.display_output(host, upload_result)

    def display_output(self, host, output):
        """Display the output in the text widget, prefixed by the host name."""
        self.output_text.insert(tk.END, f"--- Output from {host} ---\n")
        self.output_text.insert(tk.END, output + "\n\n")
        self.output_text.see(tk.END)

    def on_script_select(self, event):
        """Load selected script contents into the editable text area."""
        selected_script = self.script_combobox.get()
        self.selected_script_path = os.path.join(PS1_DIRECTORY, selected_script)
        with open(self.selected_script_path, 'r') as file:
            script_content = file.read()
            self.script_text.delete("1.0", tk.END)  # Clear previous content
            self.script_text.insert(tk.END, script_content)  # Load new content

    def run_local_script(self):
        """Run the PowerShell script content in the text area locally."""
        # Clear previous output
        self.output_text.delete("1.0", tk.END)
        script_content = self.script_text.get("1.0", tk.END).strip()

        if script_content:
            output = execute_powershell_script(script_content)
            self.display_output("Local Machine", output)
            self.save_to_history("Local Machine", script_content, output)
        else:
            self.display_output("Local Machine", "No script content to execute.")

    def run_remote_script(self):
        """Run the PowerShell script content in the text area on remote hosts."""
        # Clear previous output
        self.output_text.delete("1.0", tk.END)
        script_content = self.script_text.get("1.0", tk.END).strip()

        hosts = self.host_entry.get().split(',')
        username = self.username_entry.get()
        password = self.password_entry.get()

        for host in hosts:
            session = create_winrm_session(host.strip(), username, password)
            if isinstance(session, str):
                self.display_output(host, session)
            elif session and script_content:
                output = execute_remote_powershell_script(session, script_content)
                self.display_output(host, output)
                self.save_to_history(host, script_content, output)


    def export_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.output_text.get("1.0", tk.END))
            messagebox.showinfo("Export Results", f"Results exported to {file_path}")

    def export_history(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                for key, (command, output) in self.history.items():
                    file.write(f"{key}\n--- Command ---\n{command}\n\n--- Output ---\n{output}\n\n")
            messagebox.showinfo("Export History", f"History exported to {file_path}")

    def save_to_history(self, host, command, output):
        """Save command output to history with a descriptive key."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        short_command = (command[:30] + '...') if len(command) > 30 else command
        history_key = f"{timestamp} - {host} - {short_command}"
        self.history[history_key] = (command, output)
        self.history_combobox['values'] = list(self.history.keys())

    def on_history_select(self, event):
        """Display selected history output in the output text area."""
        selected_history = self.history_combobox.get()
        if selected_history in self.history:
            command, output = self.history[selected_history]
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"--- Command ---\n{command}\n\n--- Output ---\n{output}")

# Main application launch
if __name__ == "__main__":
    root = tk.Tk()
    app = CybersecurityToolGUI(root)
    root.mainloop()
