from record_store import store_ehr
from ehr_chain import EHRChain
import time

chain = EHRChain()

# Upload a new EHR record
filename, record_hash, signature = store_ehr("P123", "blood_test", "Hemoglobin: 13.5 g/dL")

new_record = {
    "filename": filename,
    "hash": record_hash,
    "signature": signature.hex(),
    "uploaded_by": "Hospital_A"
}

# Simulate access log
access_log = {
    "record_hash": record_hash,
    "accessed_by": "Dr.B from Hospital_B",
    "reason": "Consultation",
    "timestamp": time.time()
}

# Add block to chain
chain.add_block(records=[new_record], access_logs=[access_log])

# Save full chain
chain.save_chain()
print("\n[✓] Blockchain saved as ehr_chain.json")
