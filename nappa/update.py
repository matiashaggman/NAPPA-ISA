import requests
import os
import logging

# Your repository details (change as needed)
REPO_URL = "https://api.github.com/repos/matiashaggman/NAPPA-ISA/contents"
COMMITS_URL = "https://api.github.com/repos/matiashaggman/NAPPA-ISA/commits"
BASE_URL = "https://raw.githubusercontent.com/matiashaggman/NAPPA-ISA/main"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_json(url):
    """
    Helper to fetch JSON from a GitHub API URL (no auth token).
    Returns an empty list or dict if fails.
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch {url} (status: {resp.status_code})")
        return []
    return resp.json()


def extract_version_from_commits(commits):
    """
    Helper to extract the first 'version' mentioned in commit messages.
    Expects something like "version 1.2" in the commit message.
    Returns a float if found, otherwise None.
    """
    for c in commits:
        msg = c['commit']['message'].lower()
        if "version" in msg:
            # e.g., "Update script to version 1.2"
            try:
                # Grab everything after the word 'version'
                version_str = msg.split("version", 1)[1].strip()
                return float(version_str)
            except (ValueError, IndexError):
                pass
    return None


def list_files_in_directories(repo_url=REPO_URL):
    """
    Returns a dict:
      {
        'folder_name': ['file1.py', 'file2.txt', ...],
        ...
      }
    for all subdirectories in the repo root.
    """
    data = fetch_json(repo_url)
    if not isinstance(data, list):
        return {}

    result = {}
    for item in data:
        if item.get('type') == 'dir':
            contents = fetch_json(item['url'])
            if isinstance(contents, list):
                result[item['name']] = [
                    f['name'] for f in contents if f.get('type') == 'file'
                ]
    return result


def read_directory_versions(files_dict, commits_url=COMMITS_URL):
    """
    Reads versions for each directory by fetching commit messages
    for that directory path.
    Returns a dict like:  { 'folder_name': 1.2, ... }.
    """
    version_map = {}
    for directory_name in files_dict:
        # e.g. GET .../commits?path=directory_name
        url = f"{commits_url}?path={directory_name}"
        commits = fetch_json(url)
        version = extract_version_from_commits(commits)
        if version is not None:
            version_map[directory_name] = version
    return version_map


def read_file_versions(repo_url=REPO_URL, commits_url=COMMITS_URL):
    """
    Reads versions for top-level files in the repository root
    by checking commit messages for each file.
    Returns a dict like: { 'filename.py': 1.1, ... }.
    """
    data = fetch_json(repo_url)
    if not isinstance(data, list):
        return {}

    result = {}
    for item in data:
        if item.get('type') == 'file':
            file_name = item['name']
            url = f"{commits_url}?path={file_name}"
            commits = fetch_json(url)
            version = extract_version_from_commits(commits)
            if version is not None:
                result[file_name] = version
    return result


def download_files_if_newer(
    main_files_and_versions,
    main_directories_and_versions,
    files_in_directories,
    current_version
):
    """
    Downloads files/folders only if their version is greater than current_version.
    Returns True if successful, False if any download failed.
    """
    success = True

    # Download directories & contents if version is newer
    for folder, version in main_directories_and_versions.items():
        if version > current_version:
            # Download each file in that folder
            for fname in files_in_directories.get(folder, []):
                file_url = f"{BASE_URL}/{folder}/{fname}"
                path_to_save = os.path.join(folder, fname)

                # Make sure parent folder exists
                os.makedirs(os.path.dirname(path_to_save), exist_ok=True)

                resp = requests.get(file_url)
                if resp.status_code == 200:
                    try:
                        with open(path_to_save, 'wb') as f:
                            f.write(resp.content)
                    except IOError:
                        logger.error(f"Failed to write file: {path_to_save}")
                        success = False
                else:
                    logger.error(f"Failed to download file: {file_url} (status={resp.status_code})")
                    success = False

    # Download individual top-level files if version is newer
    for fname, version in main_files_and_versions.items():
        if version > current_version:
            file_url = f"{BASE_URL}/{fname}"
            resp = requests.get(file_url)
            if resp.status_code == 200:
                try:
                    with open(fname, 'wb') as f:
                        f.write(resp.content)
                except IOError:
                    logger.error(f"Failed to write file: {fname}")
                    success = False
            else:
                logger.error(f"Failed to download file: {file_url} (status={resp.status_code})")
                success = False

    return success


def get_files_and_versions():
    """
    Aggregates:
      - The files in each directory,
      - The version for each directory,
      - The version for each top-level file.
    """
    files_in_directories = list_files_in_directories(REPO_URL)
    main_directories_and_versions = read_directory_versions(files_in_directories, COMMITS_URL)
    main_files_and_versions = read_file_versions(REPO_URL, COMMITS_URL)

    return files_in_directories, main_directories_and_versions, main_files_and_versions


def check_for_update(current_version, status_callback=None):
    """
    Checks if any directory or top-level file has a version greater than current_version.
    Returns True if an update is found, False otherwise.
    """
    msg = 'Checking for updates...'
    if status_callback:
        status_callback(msg)
    logger.info(msg)

    files_in_directories, main_directories_and_versions, main_files_and_versions = get_files_and_versions()

    # Check if any directory version > current_version
    found_newer_dir = any(v > current_version for v in main_directories_and_versions.values())
    # Check if any file version > current_version
    found_newer_file = any(v > current_version for v in main_files_and_versions.values())

    if found_newer_dir or found_newer_file:
        msg = 'An update was found.'
        if status_callback:
            status_callback(msg)
        logger.info(msg)
        return True
    else:
        msg = 'No update needed.'
        logger.info(msg)
        return False


def do_update(current_version, status_callback=None):
    """
    Performs the download of newer files/folders if an update is available.
    Returns True if successful, False otherwise.
    """
    files_in_directories, main_directories_and_versions, main_files_and_versions = get_files_and_versions()
    success = download_files_if_newer(
        main_files_and_versions,
        main_directories_and_versions,
        files_in_directories,
        current_version
    )
    if success:
        msg = 'Update downloaded successfully.'
    else:
        msg = ('Update failed. Please visit https://github.com/OWNER/REPO '
               'and download the latest files manually.')

    if status_callback:
        status_callback(msg)
    logger.info(msg)
    return success