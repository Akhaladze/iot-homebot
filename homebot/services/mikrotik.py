import requests
import urllib3

# Disable SSL warnings for self-signed certificatesurllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MikroTikService:
    def __init__(self, ip, user, password):
        self.base_url = f"https://{ip}/rest"
        self.auth = (user, password)

    def get_dhcp_leases(self):
        """Fetch all entries from DHCP Server Lease via REST API"""
        url = f"{self.base_url}/ip/dhcp-server/lease"
        response = requests.get(url, auth=self.auth, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    