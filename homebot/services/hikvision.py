import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from requests.auth import HTTPDigestAuth
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HikVisionService:
    def __init__(self, user, password):
        self.auth = HTTPDigestAuth(user, password)
        self.parquet_dir = "data"

    def _parse_device_info(self, xml_content):
        """Parses the XML response from /ISAPI/System/deviceInfo"""
        try:
            root = ET.fromstring(xml_content)
            # Remove namespace if present (ISAPI usually has one)
            # Simple approach: ignore namespace in tag lookup or just strip it
            data = {}
            for child in root:
                tag = child.tag.split('}')[-1] # Strip namespace
                data[tag] = child.text
            return data
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return {}

    def get_config(self, ips):
        """
        Fetches device info for a list of IPs and saves to Parquet.
        """
        results = []
        scan_time = datetime.now()

        for ip in ips:
            try:
                url = f"http://{ip}/ISAPI/System/deviceInfo"
                # HikVision usually supports HTTP, if not switch to HTTPS and verify=False
                res = requests.get(url, auth=self.auth, timeout=5)
                
                if res.status_code == 200:
                    info = self._parse_device_info(res.text)
                    info['ip'] = ip
                    info['scanned_at'] = scan_time
                    results.append(info)
                else:
                    print(f"Failed to fetch config from {ip}: {res.status_code}")
            except Exception as e:
                print(f"Error connecting to {ip}: {e}")

        if results:
            df = pd.DataFrame(results)
            os.makedirs(self.parquet_dir, exist_ok=True)
            # Append or overwrite? Assuming overwrite for 'latest' config
            # But the prompt says "adds parquet file", let's name it specifically or overwrite 'latest'
            output_path = os.path.join(self.parquet_dir, "hikvision_config_latest.parquet")
            df.to_parquet(output_path, engine='pyarrow', index=False)
            return len(results)
        return 0

    def get_screenshot(self, ip, channel=101):
        """
        Downloads a JPEG snapshot from the specified channel.
        """
        try:
            url = f"http://{ip}/ISAPI/Streaming/channels/{channel}/picture"
            res = requests.get(url, auth=self.auth, timeout=10, stream=True)
            
            if res.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{ip}_{channel}_{timestamp}.jpg"
                save_dir = os.path.join(self.parquet_dir, "screenshots")
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, filename)
                
                with open(file_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                return file_path
            else:
                print(f"Failed to fetch screenshot from {ip}: {res.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching screenshot from {ip}: {e}")
            return None
