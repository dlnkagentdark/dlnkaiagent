# Installation Guide - dLNk Admin Console

This guide provides detailed installation instructions for dLNk Admin Console on different operating systems.

## System Requirements

The dLNk Admin Console requires Python 3.8 or higher and tkinter support for the graphical interface. The application has been tested on Windows 10/11, Ubuntu 20.04+, and macOS 11+.

## Prerequisites

Before installing the Admin Console, ensure that Python is properly installed on your system. You can verify this by opening a terminal or command prompt and running `python --version` or `python3 --version`. The output should show Python 3.8 or higher.

### Windows Installation

On Windows, Python typically comes with tkinter pre-installed. Download Python from the official website at python.org if you don't have it installed. During installation, make sure to check the box that says "Add Python to PATH" to ensure Python commands are accessible from the command prompt.

### Linux Installation

On Linux systems, you may need to install tkinter separately. For Ubuntu and Debian-based distributions, open a terminal and run the following commands:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

For Fedora and Red Hat-based distributions, use:

```bash
sudo dnf install python3 python3-pip python3-tkinter
```

### macOS Installation

On macOS, Python 3 can be installed using Homebrew. If you don't have Homebrew installed, visit brew.sh for installation instructions. Once Homebrew is ready, install Python with:

```bash
brew install python-tk
```

## Installing dLNk Admin Console

Once Python and tkinter are properly set up, navigate to the admin-console directory in your terminal or command prompt. Install the required Python packages by running:

```bash
pip install -r requirements.txt
```

On some systems, you may need to use `pip3` instead of `pip` to ensure you're installing packages for Python 3.

## Configuration

Before running the Admin Console, you may want to configure the API endpoint and other settings. Open the `config.py` file in a text editor and adjust the following settings as needed:

The `API_BASE_URL` should point to your dLNk backend server. By default, it's set to `http://localhost:5001`, but you can change this to your production server URL.

If you want to enable Telegram notifications, set the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ADMIN_CHAT_ID` environment variables. You can obtain a bot token by creating a new bot through BotFather on Telegram.

## Running the Application

To start the Admin Console, run:

```bash
python main.py
```

On some systems, you may need to use `python3` instead of `python`.

The application window should open, displaying the login screen. Use your Admin Key to log in. For testing purposes, you can use the test key `DLNK-ADMIN-TEST-1234-5678`.

## Troubleshooting

If you encounter an error about tkinter not being found, ensure that tkinter is properly installed for your Python version. On Linux, this usually means installing the `python3-tk` package.

If the application fails to connect to the backend API, check that the API server is running and that the `API_BASE_URL` in `config.py` is correct. The Admin Console will fall back to mock data if the API is unavailable, allowing you to test the interface.

If you see import errors related to missing packages, try reinstalling the requirements with `pip install -r requirements.txt --upgrade`.

## Environment Variables

For production deployments, you can set the following environment variables:

- `DLNK_API_URL`: Backend API URL (default: http://localhost:5001)
- `DLNK_TELEGRAM_BOT_TOKEN`: Telegram bot token for notifications
- `DLNK_TELEGRAM_ADMIN_ID`: Telegram chat ID for admin notifications
- `DLNK_SECRET_KEY`: Secret key for session encryption

On Windows, set environment variables through System Properties > Environment Variables. On Linux and macOS, add them to your `.bashrc` or `.zshrc` file.

## Next Steps

After successful installation, refer to the README.md file for usage instructions and feature documentation. For API integration details, see the API Integration section in the README.
