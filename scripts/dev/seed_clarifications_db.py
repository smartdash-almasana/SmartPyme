# This is a standalone script to seed the clarifications database for validation.
import os
from app.core.clarification.models import ClarificationRequest
from app.core.clarification.persistence import save_clarification, init_clarifications_db, _get_db_path

def seed():
    print("Initializing clarifications database...")
    db_path = _get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
    init_clarifications_db()
    
    print("Seeding with test clarification 'CL-SEED-001'...")
    
    seed_request = ClarificationRequest(
        clarification_id="CL-SEED-001",
        entity_type="invoice_match",
        value_a="Invoice #123",
        value_b="Payment #456",
        reason="Amount mismatch: 100.00 vs 99.95",
        blocking=True
    )
    
    save_clarification(seed_request)
    
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
