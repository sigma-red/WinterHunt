# WinterHunt

![sfi](https://github.com/user-attachments/assets/32c4db09-fdd4-4f01-adae-c8ac75e8c3f1)


!!THIS PROJECT IS UNDER ACTIVE DEVELOPMENT -- APPLICATION MAY BE UNSTABLE OR ERRORS MAY OCCURE -- CONTINUOUS UPDATES TO FUNCTIONALITY IN PROGRESS!!

The WinterHunt is a Python-based application designed for cybersecurity professionals. It allows users to dynamically load, edit, and execute PowerShell scripts either locally or on remote hosts. This tool is ideal for executing `.ps1` scripts on multiple systems, facilitating remote administration and artifact collection.

## Features

- **Dynamic Script Loading**: Select and load `.ps1` PowerShell scripts from a specified directory.
- **Editable Script Interface**: View and edit PowerShell scripts before execution.
- **Local and Remote Execution**: Run PowerShell scripts locally or remotely via WinRM.
- **File Transfer**: Upload selected tools to a remote directory on the target host.
- **Execution History**: Save command execution history and results for future reference.
- **Export Options**: Export command outputs and history to text files.

## Dependencies

The application requires the following dependencies:

- **Python 3.7+**
- **Tkinter**: Included with Python standard library (for the GUI).
- **WinRM**: For remote PowerShell script execution on Windows hosts. Install via:
  ```bash
  pip install pywinrm
