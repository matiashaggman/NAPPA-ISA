import requests
import os
import sys
import zipfile
from io import BytesIO

CURRENT_VERSION = 0.5
DOWNLOAD_URL_TEMPLATE = "https://github.com/matiashaggman/NAPPA-ISA/archive/refs/heads/main.zip"
REPO_URL = "https://api.github.com/repos/matiashaggman/NAPPA-ISA/commits/main"

def get_latest_commit():
    """Fetch the latest commit from the main branch on GitHub."""
    try:
        response = requests.get(REPO_URL)
        if response.status_code == 200:
            commit = response.json()
            return commit  # Single commit as a dictionary
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching commit: {e}")
        return None

def find_version_in_commit(commit):
    message = commit['commit']['message']
    if "version" in message.lower():
        try:
            version = float(message.lower().split("version")[-1].strip())
            return version
        except ValueError:
            return None
    return None


def download(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to download the file (status code: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"Error downloading the latest version: {e}")
        return None

def extract_zip(content, extract_to="."):
    try:
        with zipfile.ZipFile(BytesIO(content)) as zip_file:
            zip_file.extractall(extract_to)
    except zipfile.BadZipFile as e:
        print(f"Error extracting .zip file: {e}")

def update():
    zip_content = download(DOWNLOAD_URL_TEMPLATE)
    if zip_content:
        extract_to = os.getcwd()
        extract_zip(zip_content, extract_to)
        restart_application()
    else:
        print("Update failed: Could not download the update.")
    extract_to = os.getcwd()
    extract_zip(zip_content, extract_to)

    restart_application()

def check_for_update():
    commit = get_latest_commit()
    git_version = None
    if commit:
        git_version = find_version_in_commit(commit)
        if git_version and CURRENT_VERSION < git_version:
            update()
        else:
            print("No update available or failed to fetch the latest version.")

def restart_application():
    """Restart the current application."""
    try:
        print("Restarting application...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        print(f"Error restarting application: {e}")

if __name__ == "__main__":
    check_for_update()
