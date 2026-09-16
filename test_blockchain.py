import time
from satyashield.data.sample_generator import SampleDocumentGenerator
from satyashield.pipeline.orchestrator import SatyaShieldPipeline

def run_blockchain_test():
    print("Initializing SentinelID Pipeline with Blockchain...")
    pipeline = SatyaShieldPipeline()
    gen = SampleDocumentGenerator()
    
    print("\n--- Mining Verification Blocks ---")
    
    # 1. Authentic Aadhaar
    print("Processing Document 1: Authentic Aadhaar...")
    doc1, qr1, ocr1, face1, meta1 = gen.generate_authentic_aadhaar()
    out1 = pipeline.verify_document("doc_001", doc1, qr_payload=qr1, ocr_text=ocr1, extra_metadata=meta1)
    print(f"Block 0 Mined! Hash: {out1.audit_hash}")
    
    # 2. Forged Aadhaar
    print("Processing Document 2: Forged Aadhaar...")
    doc2, qr2, ocr2, face2, meta2 = gen.generate_forged_aadhaar()
    out2 = pipeline.verify_document("doc_002", doc2, qr_payload=qr2, ocr_text=ocr2, extra_metadata=meta2)
    print(f"Block 1 Mined! Hash: {out2.audit_hash}")
    
    # 3. Authentic PAN
    print("Processing Document 3: Authentic PAN...")
    doc3, qr3, ocr3, face3, meta3 = gen.generate_authentic_pan()
    out3 = pipeline.verify_document("doc_003", doc3, qr_payload=qr3, ocr_text=ocr3, extra_metadata=meta3)
    print(f"Block 2 Mined! Hash: {out3.audit_hash}")
    
    # Verify Initial Integrity
    print("\n--- Validating Blockchain Integrity ---")
    is_valid, msg = pipeline.blockchain.validate_chain()
    print(f"Initial State: {msg}")
    
    # Simulating a Hacker / Insider Threat
    print("\n--- SIMULATING HACK ATTACK ---")
    print("An insider tries to retroactively change the risk score of Document 2 from HIGH_RED to LOW_GREEN in the database...")
    
    # Target Block 1 (which holds Document 2)
    pipeline.blockchain.chain[1].overall_risk = "LOW_GREEN"
    pipeline.blockchain.chain[1].trust_score = 99.0
    
    # Re-validate
    print("\n--- Validating Blockchain Integrity after Hack ---")
    is_valid, msg = pipeline.blockchain.validate_chain()
    if not is_valid:
        print(f"🚨 HACK BLOCKED: {msg}")
    else:
        print("FAIL: Hack succeeded.")

if __name__ == "__main__":
    run_blockchain_test()
