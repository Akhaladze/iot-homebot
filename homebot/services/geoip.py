import geoip2.database
import os

class GeoIPService:
    def __init__(self, db_path="data/GeoLite2-City.mmdb"):
        self.db_path = db_path
        self.reader = None
        if os.path.exists(self.db_path):
            try:
                self.reader = geoip2.database.Reader(self.db_path)
            except Exception as e:
                print(f"Error loading GeoIP database: {e}")
        else:
            print(f"GeoIP database not found at {self.db_path}. Please download GeoLite2-City.mmdb.")

    def get_ip_info(self, ip):
        """
        Returns location info for a given IP address.
        """
        if not self.reader:
            return None

        try:
            response = self.reader.city(ip)
            return {
                "city": response.city.name,
                "region": response.subdivisions.most_specific.name,
                "country": response.country.name,
                "continent": response.continent.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude
            }
        except geoip2.errors.AddressNotFoundError:
            return None
        except Exception as e:
            print(f"Error resolving IP {ip}: {e}")
            return None

    def close(self):
        if self.reader:
            self.reader.close()
