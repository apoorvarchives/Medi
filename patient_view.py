# --------------------------- patient_view.py ---------------------------
import os
import json
import sys

def view_patient_history(patient_id):
    folder = "patient_records"
    filepath = os.path.join(folder, f"{patient_id}.json")

    if not os.path.exists(filepath):
        print(f"[❌] No history found for Patient ID: {patient_id}")
        return

    with open(filepath, "r") as f:
        history = json.load(f)

    if not history:
        print(f"[⚠️] No records for Patient ID: {patient_id}")
        return

    # Header
    print(f"\n🩺 Patient History Lookup")
    print(f"👤 Patient ID: {patient_id}")
    print(f"📄 Total Records: {len(history)}")
    print("=============================================")

    # Print all records
    for i, record in enumerate(history, start=1):
        print(f"📌 Record #{i}")
        print(f"   - Name      : {record['name']}")
        print(f"   - Age       : {record['age']}")
        print(f"   - Gender    : {record['gender']}")
        print(f"   - Type      : {record['record_type']}")
        print(f"   - Vitals    : {record['vitals']}")
        print("")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patient_view.py <patient_id>")
        sys.exit(1)

    pid = sys.argv[1]
    view_patient_history(pid)
