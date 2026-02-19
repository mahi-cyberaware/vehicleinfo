#!/usr/bin/env python3
"""
===============================================
       VEHICLEINFO - Indian RTO Lookup
          Tool by: MAHI-CYBERAWARE
===============================================
Fetches vehicle details using RapidAPI (vehicle-rc-information-v2).
Supports saving output to file with --save flag.
"""

import os
import sys
import re
import json
import http.client
from datetime import datetime

# ===== CONFIG =====
RAPIDAPI_HOST = "vehicle-rc-information-v2.p.rapidapi.com"
API_ENDPOINT = "/"
REPORTS_DIR = "reports"          # Folder where output files will be saved
# ==================

# ===== MANUAL .ENV LOADER =====
def load_env():
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('\'"')
load_env()
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
# ===============================

# ===== BANNER =====
def show_banner():
    print("\033[1;36m")  # Cyan bold
    print("╔══════════════════════════════════════════╗")
    print("║         VEHICLEINFO - RTO LOOKUP        ║")
    print("║          Tool by: MAHI-CYBERAWARE       ║")
    print("╚══════════════════════════════════════════╝")
    print("\033[0m")  # Reset

# ===== VALIDATION =====
def validate_vehicle_number(number):
    pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$'
    return re.match(pattern, number.upper()) is not None

# ===== API CALL =====
def fetch_from_api(vehicle_no):
    try:
        conn = http.client.HTTPSConnection(RAPIDAPI_HOST, timeout=10)
        payload = json.dumps({"vehicle_number": vehicle_no})
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': RAPIDAPI_HOST,
            'Content-Type': "application/json"
        }
        conn.request("POST", API_ENDPOINT, payload, headers)
        res = conn.getresponse()
        data = res.read()
        status = res.status
        conn.close()

        if status == 200:
            return json.loads(data.decode("utf-8"))
        else:
            return {"error": f"HTTP {status}", "details": data.decode("utf-8")}
    except Exception as e:
        return {"error": str(e)}

# ===== DEMO DATA =====
def demo_data(vehicle_no):
    return {
        "license_plate": vehicle_no.upper(),
        "owner_name": "DEMO OWNER",
        "registration_date": "01-01-2020",
        "class": "Motor Car",
        "fuel_type": "Petrol",
        "engine_number": "DEMO12345",
        "chassis_number": "DEMO67890",
        "maker_model": "Maruti Suzuki Swift",
        "insurance_expiry": "31-12-2024",
        "fit_up_to": "31-12-2025",
        "rc_status": "Active",
        "_note": "This is demo data – API not used."
    }

# ===== RESPONSE PARSER =====
def extract_vehicle_data(api_response):
    if isinstance(api_response, dict):
        if "error" in api_response:
            return None, api_response["error"]
        if api_response.get("status") == "success" and "response" in api_response:
            return api_response["response"], None
        if "license_plate" in api_response or "owner_name" in api_response:
            return api_response, None
        return None, "Unknown response format"
    return None, "Response is not a dictionary"

# ===== DISPLAY =====
def format_vehicle_text(vehicle_data, source="Live API"):
    """Return a formatted string of vehicle details (for display and saving)."""
    lines = []
    lines.append("═" * 56)
    lines.append(f"🔍 VEHICLE DETAILS [Source: {source}]")
    lines.append("═" * 56)

    field_labels = {
        "license_plate": "Registration No",
        "owner_name": "Owner Name",
        "father_name": "Father's Name",
        "registration_date": "Registration Date",
        "class": "Vehicle Class",
        "fuel_type": "Fuel Type",
        "engine_number": "Engine No",
        "chassis_number": "Chassis No",
        "brand_name": "Make",
        "brand_model": "Model",
        "maker_model": "Model",
        "insurance_expiry": "Insurance Upto",
        "insurance_company": "Insurance Co",
        "insurance_policy": "Policy No",
        "fit_up_to": "Fitness Upto",
        "tax_upto": "Tax Upto",
        "rc_status": "RC Status",
        "color": "Colour",
        "norms": "Emission Norms",
        "seating_capacity": "Seating",
        "cubic_capacity": "Engine CC",
        "cylinders": "Cylinders",
        "vehicle_age": "Vehicle Age",
        "pucc_upto": "PUCC Upto",
        "pucc_number": "PUCC No",
        "noc_details": "NOC Details",
        "present_address": "Present Address",
        "permanent_address": "Permanent Address",
        "financer": "Financer",
        "is_financed": "Financed",
        "owner_count": "Owner Count",
        "blacklist_status": "Blacklist Status",
        "national_permit_number": "National Permit No",
        "national_permit_upto": "National Permit Upto",
        "permit_number": "Permit No",
        "permit_issue_date": "Permit Issue Date",
        "permit_valid_upto": "Permit Valid Upto",
        "permit_type": "Permit Type",
        "sleeper_capacity": "Sleeper Capacity",
        "standing_capacity": "Standing Capacity",
        "gross_weight": "Gross Weight",
        "unladen_weight": "Unladen Weight",
        "wheelbase": "Wheelbase",
        "body_type": "Body Type",
        "note": "Note",
        "_note": "Note"
    }

    for key, value in vehicle_data.items():
        if key in ["id", "createdAt", "updatedAt", "vehicleId", "source", "latest_by"]:
            continue
        if value in [None, "", "null", "NA", "Not Available"]:
            continue
        label = field_labels.get(key, key.replace('_', ' ').title())
        lines.append(f"  {label:<25}: {value}")
    lines.append("═" * 56)
    return "\n".join(lines)

def display_info(vehicle_data, source="Live API"):
    """Print the formatted info to console."""
    print("\n" + format_vehicle_text(vehicle_data, source))

# ===== SAVE TO FILE =====
def save_to_file(vehicle_no, content):
    """Save content to a timestamped file in reports/ directory."""
    # Create reports directory if it doesn't exist
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        print(f"📁 Created directory: {REPORTS_DIR}/")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"vehicle_{vehicle_no}_{timestamp}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Output saved to: {filepath}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

# ===== MAIN =====
def main():
    show_banner()

    if not RAPIDAPI_KEY:
        print("\033[1;31m❌ ERROR: RAPIDAPI_KEY not found in .env file.\033[0m")
        print("Please create a .env file with your key (see .env.example).")
        sys.exit(1)

    # Parse arguments
    save_output = False
    vehicle_no = None

    # Simple argument parsing
    args = sys.argv[1:]
    if "-s" in args or "--save" in args:
        save_output = True
        # Remove the flag from args list to find vehicle number
        args = [arg for arg in args if arg not in ("-s", "--save")]

    if len(args) > 0:
        vehicle_no = args[0].strip()
    else:
        vehicle_no = input("Enter vehicle number (e.g., PB65AM0008): ").strip()

    if not validate_vehicle_number(vehicle_no):
        print("\033[1;31m❌ Invalid format. Use e.g., MH02FB2727\033[0m")
        sys.exit(1)

    print(f"\n🔎 Fetching details for \033[1;33m{vehicle_no.upper()}\033[0m...")

    # Try API
    print("🌐 Using live API...")
    api_response = fetch_from_api(vehicle_no)

    vehicle_data, error = extract_vehicle_data(api_response)

    if vehicle_data:
        output_text = format_vehicle_text(vehicle_data, "Live API")
        print("\n" + output_text)
        source_type = "Live API"
    else:
        print(f"\033[1;33m⚠️  API issue: {error}\033[0m")
        if error == "Unknown response format":
            print("\n📦 Raw response received:")
            print(json.dumps(api_response, indent=2))
        print("\n🔄 Falling back to demo data...")
        vehicle_data = demo_data(vehicle_no)
        output_text = format_vehicle_text(vehicle_data, "Demo")
        print("\n" + output_text)
        source_type = "Demo"

    # Save to file if requested
    if save_output:
        # Include a header with timestamp and source info
        full_output = f"VEHICLEINFO Report\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nVehicle: {vehicle_no.upper()}\nSource: {source_type}\n\n{output_text}"
        save_to_file(vehicle_no, full_output)

if __name__ == "__main__":
    main()
