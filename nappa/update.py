import requests
import os
import logging

REPO_URL = "https://api.github.com/repos/matiashaggman/NAPPA-ISA/contents"
COMMITS_URL = "https://api.github.com/repos/matiashaggman/NAPPA-ISA/commits"
TOKEN = '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'
BASE_URL = "https://raw.githubusercontent.com/matiashaggman/NAPPA-ISA/main"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_json(url, token=None):
    """Helper to fetch JSON from a GitHub API URL with optional token."""
    headers = {'Authorization': f'token {token}'} if token else {}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch {url} (status: {resp.status_code})")
        return []
    return resp.json()

def extract_version_from_commits(commits):
    """Helper to extract the first 'version' mentioned in commit messages."""
    for c in commits:
        msg = c['commit']['message'].lower()
        if "version" in msg:
            try:
                return float(msg.split("version")[-1].strip())
            except ValueError:
                pass
    return None

def list_files_in_directories(repo_url=REPO_URL, token=None):
    data = fetch_json(repo_url, token)
    result = {}
    for item in data:
        if item['type'] == 'dir':
            contents = fetch_json(item['url'], token)
            result[item['name']] = [f['name'] for f in contents if f['type'] == 'file']
    return result

def read_directory_versions(files_dict, commits_url=COMMITS_URL, token=None):
    """Reads versions for directories in files_dict."""
    version_map = {}
    for d in files_dict:
        commits = fetch_json(f"{commits_url}?path={d}", token)
        version = extract_version_from_commits(commits)
        if version is not None:
            version_map[d] = version
    return version_map

def read_file_versions(repo_url=REPO_URL, commits_url=COMMITS_URL, token=None):
    """Reads versions for top-level files in the repository."""
    data = fetch_json(repo_url, token)
    result = {}
    for item in data:
        if item['type'] == 'file':
            commits = fetch_json(f"{commits_url}?path={item['name']}", token)
            version = extract_version_from_commits(commits)
            if version is not None:
                result[item['name']] = version
    return result

def download_files_if_newer(main_files_and_versions, main_directories_and_versions, files_in_directories, current_version, token):
    headers = {'Authorization': f'token {token}'} if token else {}
    success = True

    # Download directories & contents
    for folder, version in main_directories_and_versions.items():
        if version > current_version:
            for fname in files_in_directories.get(folder, []):
                file_url = f"{BASE_URL}/{folder}/{fname}"
                path_to_save = os.path.join(folder, fname)
                os.makedirs(os.path.dirname(path_to_save), exist_ok=True)
                resp = requests.get(file_url, headers=headers)
                if resp.status_code == 200:
                    try:
                        with open(path_to_save, 'wb') as f:
                            f.write(resp.content)
                    except IOError:
                        success = False
                else:
                    success = False

    # Download individual files
    for fname, version in main_files_and_versions.items():
        if version > current_version:
            file_url = f"{BASE_URL}/{fname}"
            resp = requests.get(file_url, headers=headers)
            if resp.status_code == 200:
                try:
                    with open(fname, 'wb') as f:
                        f.write(resp.content)
                except IOError:
                    success = False
            else:
                success = False

    return success

def get_files_and_versions():

    files_in_directories            = list_files_in_directories(repo_url=REPO_URL, token=TOKEN)
    main_directories_and_versions   = read_directory_versions(files_in_directories,commits_url=COMMITS_URL,token=TOKEN)
    main_files_and_versions         = read_file_versions(repo_url=REPO_URL,commits_url=COMMITS_URL,token=TOKEN)
    
    return files_in_directories, main_directories_and_versions, main_files_and_versions
    

def check_for_update(current_version, status_callback=None):

    msg='Checking for updates...'
    if status_callback:
        status_callback(msg)
    logger.info(msg)

    files_in_directories, main_directories_and_versions, main_files_and_versions = get_files_and_versions()
    if any(version > current_version for version in main_directories_and_versions.values()) or any(version > current_version for version in main_files_and_versions.values()):
        msg = 'An update was found.'
        if status_callback:
            status_callback(msg)
        logger.info(msg)
        return True
    else:
        return False
    

def do_update(current_version, status_callback=None):

    files_in_directories, main_directories_and_versions, main_files_and_versions = get_files_and_versions()
    success = download_files_if_newer(main_files_and_versions, main_directories_and_versions, files_in_directories, current_version, token=TOKEN)
    if success:
        msg = 'Update downloaded successfully.'
    else:
        msg = 'Update failed. Please visit https://github.com/matiashaggman/NAPPA-ISA/ and download latest files manually.'
        if status_callback:
            status_callback(msg)
        logger.info(msg)
    return success