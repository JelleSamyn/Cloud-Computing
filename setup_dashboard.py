import urllib.request
import json
import time
import sys

host = "http://localhost:8086"
token = "my-super-secret-admin-token-123456789"
org_name = "sensor_gateway"

def make_request(url, method="GET", payload=None):
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode('utf-8')
            return json.loads(res_data) if res_data else {}
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        raise e

def main():
    try:
        # 1. Wait for InfluxDB to be ready
        print("Waiting for InfluxDB to be ready...")
        ready = False
        for i in range(30):
            try:
                urllib.request.urlopen(f"{host}/ping")
                print("InfluxDB is ready!")
                ready = True
                break
            except Exception:
                time.sleep(2)
        
        if not ready:
            print("InfluxDB did not become ready in time. Skipping dashboard setup.")
            sys.exit(1)

        # 2. Get Org ID
        orgs = make_request(f"{host}/api/v2/orgs?org={org_name}")
        if not orgs.get("orgs"):
            raise Exception(f"Organization {org_name} not found!")
        org_id = orgs["orgs"][0]["id"]
        print(f"Found Org: {org_name} (ID: {org_id})")

        # 3. Clean up existing dashboard to apply updates
        existing_dashboards = make_request(f"{host}/api/v2/dashboards?org={org_name}")
        for dash in existing_dashboards.get("dashboards", []):
            if dash.get("name") == "Smart Sensor Gateway Dashboard":
                dash_id = dash.get("id")
                print(f"Removing old dashboard (ID: {dash_id}) to apply updates...")
                make_request(f"{host}/api/v2/dashboards/{dash_id}", "DELETE")

        # 4. Create Dashboard
        dash_payload = {
            "orgID": org_id,
            "name": "Smart Sensor Gateway Dashboard",
            "description": "Dashboard for Joystick and Button telemetry"
        }
        dash = make_request(f"{host}/api/v2/dashboards", "POST", dash_payload)
        dash_id = dash["id"]
        print(f"Created Dashboard (ID: {dash_id})")

        # Helper to add cells and update views
        def add_cell(name, x, y, w, h, flux_query, view_type="xy"):
            # Add cell
            cell_payload = {
                "x": x,
                "y": y,
                "w": w,
                "h": h
            }
            cell = make_request(f"{host}/api/v2/dashboards/{dash_id}/cells", "POST", cell_payload)
            cell_id = cell["id"]
            
            # Update cell view
            view_payload = {
                "properties": {
                    "type": view_type,
                    "queries": [
                        {
                            "text": flux_query,
                            "editMode": "advanced",
                            "name": "query"
                        }
                    ],
                    "shape": "chronograf-v2",
                    "axes": {
                        "x": {"bounds": ["", ""], "label": "Time", "name": "x", "scale": "linear"},
                        "y": {"bounds": ["", ""], "label": name, "name": "y", "scale": "linear"}
                    }
                },
                "name": name
            }
            
            make_request(f"{host}/api/v2/dashboards/{dash_id}/cells/{cell_id}/view", "PATCH", view_payload)
            print(f"Added and configured cell: {name}")

        # 5. Add the 4 required cells (with corrected Flux queries for line-graphs)
        # Cell 1: Live Joystick (X/Y)
        q1 = 'from(bucket: "sensor_data") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "joystick") |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y") |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)'
        add_cell("Live Joystick (X/Y)", 0, 0, 6, 4, q1, "xy")

        # Cell 2: Live Buttons
        q2 = 'from(bucket: "sensor_data") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "buttons") |> aggregateWindow(every: 10s, fn: last, createEmpty: false)'
        add_cell("Live Buttons (A/B)", 6, 0, 6, 4, q2, "xy")

        # Cell 3: Avg Distance (1h)
        q3 = 'from(bucket: "sensor_data") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "joystick") |> filter(fn: (r) => r["_field"] == "distance") |> mean()'
        add_cell("Avg Joystick Distance (1 Hour)", 0, 4, 6, 4, q3, "single-stat")

        # Cell 4: Avg Distance (24h)
        q4 = 'from(bucket: "sensor_data") |> range(start: -24h) |> filter(fn: (r) => r["_measurement"] == "joystick") |> filter(fn: (r) => r["_field"] == "distance") |> mean()'
        add_cell("Avg Joystick Distance (24 Hours)", 6, 4, 6, 4, q4, "single-stat")

        print("Dashboard setup complete!")
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    main()
