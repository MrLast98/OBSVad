# OBSVad
### Voice Activity Detection for OBS Image Control

This application leverages Voice Activity Detection (VAD) to trigger the visibility of two or three image sources in OBS (Open Broadcaster Software) while speaking. It communicates with OBS through the OBS WebSocket, providing dynamic control over your streaming visuals based on audio input.

[![OBSVAD Windows Build](https://github.com/MrLast98/OBSVad/actions/workflows/python-app.yml/badge.svg)](https://github.com/MrLast98/OBSVad/actions/workflows/python-app.yml)

## Features

- Dynamically show/hide image sources in OBS based on voice activity.
- Support for two or three image sources for flexible scene management.
- Easy setup with automatic configuration file generation.
- Automatic scene detection when switching

## Planned Features
- Idle animation
- Mute image support

## How to Use (Executable)

1. **First-Time Setup**: Run the provided `.exe` file. This action generates a `config.json` file in the application directory.

2. **Configure OBS WebSocket**:
   - Start the OBS WebSocket server by navigating to `Tools` > `WebSocket Server Settings` in OBS.
   - Set a password for added security.

3. **Edit Configuration File**:
   - Open `config.json` and fill in the names of your image sources under `"on_image_source"`, `"off_image_source"`, and optionally `"additional_on_image_source"` for a third triggerable image.
   - Save your changes.

4. **Restart Application**: Run the `.exe` file again. You'll be prompted to select which audio source to monitor for voice activity. After selecting, the application starts monitoring and controlling your OBS image sources accordingly.

## How to Use (Script)

For those preferring to run the application as a Python script:

1. **Install Python**: Ensure Python is installed on your system. Download from [python.org](https://www.python.org/downloads/) if necessary.

2. **Optional - Create Virtual Environment**:
   - Open a terminal/command prompt and navigate to your project directory.
   - Run `python -m venv vad-env` to create a virtual environment named `vad-env`.
   - Activate the virtual environment:
     - On Windows: `vad-env\Scripts\activate`
     - On macOS/Linux: `source vad-env/bin/activate`

3. **Install Requirements**:
   - With your virtual environment activated (or without, if you skipped that step), run `pip install -r requirements.txt` to install necessary dependencies.

4. **Run the Script**:
   - Execute the script directly by running `python main.py` (assuming `main.py` is the entry point of your application).
   - Follow the prompts to configure and start the VAD service.

## Configuration

The `config.json` file controls the behavior of the application. It requires the following fields:

- `"on_image_source"`: Name of the image source to display when voice activity is detected.
- `"off_image_source"`: Name of the image source to display when no voice activity is present.
- `"additional_on_image_source"` (optional): An additional image source to toggle alongside the primary `"on_image_source"`.

Example `config.json`:

```json
{
  "on_image_source": "SpeakingImage",
  "off_image_source": "IdleImage",
  "additional_on_image_source": "ExtraImage"
}
```
Ensure OBS WebSocket server settings match those configured in `config.json`, and that the names used in the configuration file match the source image names in your scenes.

-----
## Thanks
- OBS Websocket communication thanks to https://github.com/Elektordi/obs-websocket-py
