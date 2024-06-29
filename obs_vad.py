import json
import os.path
import sys
import time
import numpy as np
import pyaudio
from obswebsocket import obsws, requests
import webrtcvad
from obswebsocket.exceptions import ConnectionFailure


class ObsVad:
    def __init__(self):
        self.input_list = []
        self.selected_device = {}
        self.last_detection = False
        self.current_scene = ''
        self.vad = webrtcvad.Vad(3)
        self.config = {
            "off_source_image_name": '',
            "on_source_image_name": '',
            "optional_image_name": '',
            "url": '',
            "port": 0,
            "password": ''
        }
        if self.get_configuration():
            if self.config['off_source_image_name'] != '' and self.config['on_source_image_name'] != '':
                self.list_input_devices()
                print("Available audio devices:")
                for i in range(len(self.input_list)):
                    print(f"{i}: {self.input_list[i]['name']}")

                self.selected_device = self.input_list[int(input("Select device index: "))]['device_info']
                self.chunk = int(self.selected_device['defaultSampleRate'] * 0.030)
                self.audio_stream = self.get_audio_stream()
                self.ws = obsws(self.config['url'], self.config['port'], self.config['password'])
                self.main()
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            else:
                print("Off or On image configuration invalid - quitting")
                print("Please revise the configuration")
        else:
            print("No configuration found - default file created")
            print("Please fill the necessary configuration")
        time.sleep(1)
        sys.exit(0)

    def main(self):
        try:
            self.ws.connect()
            while True:
                scene_list = self.ws.call(requests.GetSceneList()).datain
                if scene_list['currentProgramSceneUuid'] is None or scene_list[
                    'currentProgramSceneUuid'] != self.current_scene:
                    self.current_scene = scene_list['currentProgramSceneUuid']
                    item_list = self.ws.call(
                        requests.GetSceneItemList(sceneUuid=scene_list['currentProgramSceneUuid'])).datain
                    self.get_image_sources_id(item_list['sceneItems'])
                pcm_data = self.audio_stream.read(self.chunk)
                np_pcm_data = np.frombuffer(pcm_data, dtype=np.int16)
                is_voice_detected = self.vad.is_speech(np_pcm_data.tobytes(),
                                                       sample_rate=int(self.selected_device['defaultSampleRate']))
                if self.last_detection != is_voice_detected:
                    self.last_detection = is_voice_detected
                    self.toggle_image_visibility(not is_voice_detected, )
                    print(f"voice detected?: {is_voice_detected}")
                time.sleep(0.030)  # Sleep for 30ms to match the CHUNK duration
        except KeyboardInterrupt:
            print("\nShutting down...")
        except ConnectionFailure:
            print("\nNo OBS istance found. Is OBS running? Did you turn on the OBS Websocket server?")
        self.ws.disconnect()

    def list_input_devices(self):
        p = pyaudio.PyAudio()
        info = p.get_device_info_by_index
        numdevices = p.get_device_count()
        allowed_rates = [8000, 16000, 32000, 48000]  # Allowed sample rates

        best_device_index = -1
        highest_rate = -1

        for i in range(numdevices):
            device_info = info(i)
            if device_info["maxInputChannels"] > 0:
                rate = int(device_info['defaultSampleRate'])
                if rate in allowed_rates and rate > highest_rate:
                    highest_rate = rate
                    best_device_index = i

        if best_device_index != -1:
            device_info = info(best_device_index)
            self.input_list.append({
                'index': best_device_index,
                'name': device_info['name'],
                'device_info': device_info
            })
        else:
            print("No suitable device found.")

        p.terminate()

    def toggle_image_visibility(self, detected):
        self.ws.call(
            requests.SetSceneItemEnabled(sceneUuid=self.current_scene, sceneItemId=self.config['off_source_image_id'],
                                         sceneItemEnabled=detected))
        self.ws.call(
            requests.SetSceneItemEnabled(sceneUuid=self.current_scene, sceneItemId=self.config['on_source_image_id'],
                                         sceneItemEnabled=not detected))
        if self.config['optional_image_name'] != '':
            self.ws.call(
                requests.SetSceneItemEnabled(sceneUuid=self.current_scene, sceneItemId=self.config['optional_image_id'],
                                             sceneItemEnabled=not detected))

    def get_audio_stream(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=self.selected_device['maxInputChannels'],
                        rate=int(self.selected_device['defaultSampleRate']),
                        input=True,
                        frames_per_buffer=self.chunk,
                        input_device_index=self.selected_device['index'])
        return stream

    def get_image_sources_id(self, sources):
        for s in sources:
            if s['inputKind'] == 'image_source':
                if s['sourceName'] == self.config['off_source_image_name']:
                    self.config['off_source_image_id'] = s['sceneItemId']
                if s['sourceName'] == self.config['on_source_image_name']:
                    self.config['on_source_image_id'] = s['sceneItemId']
                if s['sourceName'] == self.config['optional_image_name']:
                    self.config['optional_image_id'] = s['sceneItemId']

    def get_configuration(self):
        if not os.path.exists('config.json'):
            with open('config.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.config, indent=4))
            return False
        else:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.loads(f.read())
            return True


if __name__ == "__main__":
    ObsVad()
