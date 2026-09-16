"""
SatyaShield Blockchain Subsystem
--------------------------------
Implements a Proof of Authority (PoA) Blockchain to serve as a tamper-evident,
immutable ledger for all verification events, mapping directly to SentinelID
Accountability Requirements.
"""
import time
import json
import hashlib
import hmac
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from ..core.types import VerificationOutcome, ModuleResult


@dataclass
class Block:
    index: int
    timestamp: float
    document_id: str
    document_type: str
    merkle_root: str
    overall_risk: str
    trust_score: float
    previous_hash: str
    nonce: int
    block_hash: str
    authority_signature: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)


class SentinelBlockchain:
    """
    A lightweight Proof of Authority (PoA) Blockchain tailored for identity 
    verification audit trails. Provides immutable O(1) appending and O(n) validation.
    """
    GENESIS_HASH = "0" * 64

    def __init__(self, authority_key: Optional[bytes] = None):
        # The private key representing the centralized trusted authority (e.g. Government/Server)
        self.authority_key = authority_key or b"SENTINEL_AUTHORITY_MASTER_KEY_2026"
        self.chain: List[Block] = []

    def _compute_merkle_root(self, outcome: VerificationOutcome) -> str:
        """
        Creates a deterministic Merkle-style root hash from all individual 
        verification module results. If even one sub-result is altered, the root changes.
        """
        leaves = [
            f"{mod.module_name}:{mod.status.value}:{mod.confidence:.4f}"
            for mod in outcome.module_results
        ]
        
        if not leaves:
            return hashlib.sha256(b"EMPTY_EVIDENCE").hexdigest()
            
        # Simplistic Merkle hashing for the leaves
        current_layer = [hashlib.sha256(leaf.encode("utf-8")).hexdigest() for leaf in leaves]
        
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i+1] if i + 1 < len(current_layer) else left
                combined = left + right
                next_layer.append(hashlib.sha256(combined.encode("utf-8")).hexdigest())
            current_layer = next_layer
            
        return current_layer[0]

    def _calculate_block_hash(
        self,
        index: int,
        timestamp: float,
        doc_id: str,
        doc_type: str,
        merkle_root: str,
        risk: str,
        score: float,
        prev_hash: str,
        nonce: int
    ) -> str:
        """Calculates deterministic SHA-256 of the block contents without the signature."""
        content = f"{index}|{timestamp:.6f}|{doc_id}|{doc_type}|{merkle_root}|{risk}|{score:.2f}|{prev_hash}|{nonce}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _sign_block_authority(self, block_hash: str) -> str:
        """Proof of Authority seal using HMAC-SHA256."""
        return hmac.new(self.authority_key, block_hash.encode("utf-8"), hashlib.sha256).hexdigest()

    def mine_verification_block(self, outcome: VerificationOutcome) -> Block:
        """
        Mines a new block containing the verification outcome and appends it to the chain.
        """
        index = len(self.chain)
        prev_hash = self.chain[-1].block_hash if self.chain else self.GENESIS_HASH
        merkle_root = self._compute_merkle_root(outcome)
        now = time.time()
        nonce = 0 # In PoA, nonce is simply 0 as mining is instant via authority signature

        # 1. Generate Block Hash
        block_hash = self._calculate_block_hash(
            index, now, outcome.document_id, outcome.document_type.value,
            merkle_root, outcome.overall_risk.value, outcome.trust_score, prev_hash, nonce
        )
        
        # 2. Seal with Proof of Authority Signature
        sig = self._sign_block_authority(block_hash)

        block = Block(
            index=index,
            timestamp=now,
            document_id=outcome.document_id,
            document_type=outcome.document_type.value,
            merkle_root=merkle_root,
            overall_risk=outcome.overall_risk.value,
            trust_score=outcome.trust_score,
            previous_hash=prev_hash,
            nonce=nonce,
            block_hash=block_hash,
            authority_signature=sig
        )
        
        self.chain.append(block)
        outcome.audit_hash = block_hash # Attach blockchain ID back to the outcome
        return block

    def validate_chain(self) -> Tuple[bool, Optional[str]]:
        """
        Traverses the entire blockchain from genesis to head, ensuring 100% cryptographic integrity.
        """
        for i, block in enumerate(self.chain):
            # 1. Check Link Integrity (Is the chain broken?)
            expected_prev = self.chain[i - 1].block_hash if i > 0 else self.GENESIS_HASH
            if block.previous_hash != expected_prev:
                return False, f"CHAIN LINK BROKEN at Block #{i}: previous_hash does not match Block #{i-1} block_hash!"

            # 2. Check Data Integrity (Has the block data been altered?)
            recalc_hash = self._calculate_block_hash(
                block.index, block.timestamp, block.document_id, block.document_type,
                block.merkle_root, block.overall_risk, block.trust_score, block.previous_hash, block.nonce
            )
            if block.block_hash != recalc_hash:
                return False, f"TAMPER DETECTED at Block #{i}: Block hash recalculation mismatch!"

            # 3. Check Authority Consensus (Was it signed by a malicious actor?)
            expected_sig = self._sign_block_authority(block.block_hash)
            if not hmac.compare_digest(block.authority_signature, expected_sig):
                return False, f"UNAUTHORIZED SEAL at Block #{i}: Proof of Authority signature invalid!"

        return True, "Blockchain integrity 100% verified. No tampering detected."
