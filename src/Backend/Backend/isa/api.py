import requests
import tempfile
import os
import zipfile
import traceback
from datetime import datetime

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool

import pandas as pd

from isa.core.io import load_settings, load_data
from isa.core.wear import detect_wear, detect_wear_blocks

from isa.analysis import nappa_analysis


app = FastAPI()

def get_ip_location(ip):
    """
    Get the location of an IP address using the ipinfo.io API.
    Parameters:
    ip (str): The IP address to look up.
    Returns:
    dict: A dictionary containing the location information.
    """
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching IP location: {e}")
        return None


@app.post("/startup")
async def startup_info(payload: dict):
    ip = payload.get("IP")
    location = None
    if ip:
        location = get_ip_location(ip)
    
    if location:
        country = location.get("country", "Unknown")
        city = location.get("city", "Unknown")
        payload["location"] = f"{country}, {city}"

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_df = pd.read_csv("log.csv")

    log_row = {'time':current_time, 'ip':ip, 'location': payload['location'],
     'app_version':payload['app_version'], 'machine_name':payload['machine_name'], 
     'os_version':payload['os_version']}

    print(f'User connected with payload: f{log_row}')

    log_df.loc[len(log_df)] = log_row
    log_df.to_csv("log.csv", index=False)

    return {"status": "received"}

@app.get("/downloadplugin", response_class=FileResponse)
async def download_plugin():
    """
    Downloads the NAPPA plugin dll file.
    Returns:
    FileResponse: the NAPPA plugin dll.
    """
    return FileResponse(
        "NappaPlugin.dll",
        media_type="application/octet-stream",
        filename="NappaPlugin.dll"
    )


@app.post("/import")
async def import_recording(
    zip_archive: UploadFile = File(...),
    settings: UploadFile = File(...)):
    """
    Import a sleep-recording archive and detect candidate sleep periods.

    Uploads
    -------
    zip_archive : ZIP produced by the wearable (AccFeatures*, GyroFeatures*).
    settings    : settings.json from the client.

    Returns
    -------
    JSON dict
        {
          "sleep_periods": [[start, end], ...],
          "duration": "0 days 10:23:00"
        }
    or HTTP 500 with {"error": "...", "traceback": "..."} on failure.
    """
    try:
        tempfolder = tempfile.mkdtemp()
        print(f"Temporary folder created: {tempfolder}")

        zip_path = os.path.join(tempfolder, zip_archive.filename) #type:ignore
        settings_path = os.path.join(tempfolder, settings.filename) #type:ignore


        with open(zip_path, "wb") as f:
            f.write(await zip_archive.read())
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tempfolder)
        with open(settings_path, "wb") as f:
            f.write(await settings.read())

        parsed_settings = load_settings(settings_path)
        time_offset = parsed_settings['data']['time_offset']

        sleepRecording = load_data(tempfolder, time_offset)
        if sleepRecording.duration > pd.Timedelta(days=1):
            wear_idx = detect_wear(sleepRecording.features.loc[:, 'activity']) #type:ignore
            parsed_settings['data']['sleep_periods'] = detect_wear_blocks(wear_idx)
        else:
            wear_idx = pd.Series([True for i in range(len(sleepRecording))],
                                  index=sleepRecording.features.index, name='wear')
            parsed_settings['data']['sleep_periods'] = [[sleepRecording.start.strftime("%Y-%m-%d %H:%M:%S"), sleepRecording.end.strftime("%Y-%m-%d %H:%M:%S")]]

    except Exception as e:
        traceback_str = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback_str}
        )
    return {"sleep_periods": parsed_settings["data"]["sleep_periods"], "duration": str(sleepRecording.duration)} #type:ignore


@app.post("/analysis")
async def nappa_online_analysis(
    zip_archive: UploadFile = File(...),
    settings: UploadFile = File(...)):
    """
    Full pipeline: classify, plot, package results.

    Uploads
    -------
    zip_archive : Raw feature zip.
    settings    : settings.json from the GUI.

    Returns
    -------
    FileResponse
        analysed_<input>.zip (200 OK) on success.
    JSONResponse
        {"error": "...", "traceback": "..."} (500) on failure.
    """

    try:
        # Remove .zip from filename
        input_filename = zip_archive.filename[:-4] #type:ignore
        if not "analyzed" in input_filename:
            output_filename = input_filename + "_analyzed.zip"
        else:
            output_filename = input_filename + ".zip"

        tempfolder = tempfile.mkdtemp()

        output_path = os.path.join(tempfolder, output_filename)

        zip_path = os.path.join(tempfolder, zip_archive.filename) #type:ignore
        settings_path = os.path.join(tempfolder, settings.filename) #type:ignore

        with open(zip_path, "wb") as f:
            f.write(await zip_archive.read())

        with open(settings_path, "wb") as f:
            f.write(await settings.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tempfolder)

        print("Running analysis...")

        parsed_settings = load_settings(settings_path)
        time_offset = parsed_settings['data']['time_offset']

        sleepRecording = load_data(tempfolder, time_offset)
        wear_idx = detect_wear(sleepRecording.features.loc[:, 'activity']) #type:ignore

        await run_in_threadpool(
            nappa_analysis,
            recording=sleepRecording,
            wear_idx=wear_idx,
            output_file=output_path,
            tempfolder=tempfolder,
            settings=parsed_settings
        )

        return FileResponse(output_path, media_type="application/zip", filename=output_filename)
    
    except Exception as e:
        traceback_str = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback_str}
        )