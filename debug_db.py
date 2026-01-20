import duckdb
import pandas as pd

try:
    with duckdb.connect('network.db') as con:
        print("--- Active Shelly Devices ---")
        # Fetch as a DataFrame for a nice table display
        df = con.execute("SELECT * FROM active_shelly").df()
        if df.empty:
            print("No devices found in 'active_shelly' view.")
        else:
            print(df.to_string(index=False))
except Exception as e:
    print(f"Error connecting to database: {e}")
