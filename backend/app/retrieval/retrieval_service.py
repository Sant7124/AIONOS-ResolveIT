import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.models.source_reference import SourceReference
from app.schemas.retrieval import RetrievalResultSchema, SourceMetadataSchema, RetrievalResponseSchema

class PolicyRetrievalService:
    """Authoritative Knowledge Base Retrieval Engine grounded in the Veridian Corp Data Pack."""

    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, top_k: int = 3) -> RetrievalResponseSchema:
        """Retrieve relevant policies ranked by relevance score and grounded in the database."""
        if not query or not query.strip():
            return RetrievalResponseSchema(
                query="",
                results_count=0,
                results=[],
                has_authoritative_match=False
            )

        clean_query = query.strip()
        tokens = set(re.findall(r"\w+", clean_query.lower()))

        # Load all policies from database
        policies = self.db.query(Policy).all()
        scored_policies: List[Tuple[float, Policy, SourceReference]] = []

        # Domain term boosts for high precision
        domain_boosts = {
            "KB-01": ["password", "lockout", "locked", "attempts", "reset", "unlock", "portal"],
            "KB-02": ["vpn", "credential", "credentials", "expired", "contractor", "renewal", "90"],
            "KB-03": ["laptop", "turn on", "dead", "replacement", "replace", "years", "hardware", "flicker", "flickering", "repair"],
            "KB-04": ["software", "install", "catalog", "extension", "browser", "security review", "tool"],
            "KB-05": ["printer", "queue", "spooler", "print", "jam", "paper jam", "asset tag"],
            "KB-06": ["mailbox", "quota", "25gb", "50gb", "full", "archive", "storage"],
            "KB-07": ["guest", "wi-fi", "wifi", "visitor", "kiosk", "24 hours", "tomorrow"],
            "KB-08": ["expense", "login", "credentials", "finance", "admin", "reporting server"],
            "KB-09": ["phishing", "malware", "suspicious", "forwarding", "forward", "teammates", "unauthorized"],
            "KB-10": ["wfh", "home office", "monitor", "chair", "allowance", "working from home", "remote"],
            "ASSET-01": ["refresh", "cycle", "4-year", "4 years", "asset", "hardware refresh", "early replacement"]
        }

        for policy in policies:
            score = 0.0
            p_id = policy.id.upper()
            title_lower = policy.title.lower()
            summary_lower = policy.summary.lower()
            text_lower = policy.source_text.lower()
            conds_lower = " ".join([c.lower() for c in (policy.conditions or [])])

            # Exact ID query match
            if p_id in clean_query.upper():
                score += 5.0

            # Direct title match
            for t in tokens:
                if len(t) > 2:
                    if t in title_lower:
                        score += 2.5
                    if t in summary_lower:
                        score += 1.8
                    if t in conds_lower:
                        score += 1.5
                    if t in text_lower:
                        score += 1.0

            # Domain keyword boosts
            if p_id in domain_boosts:
                for boost_word in domain_boosts[p_id]:
                    if boost_word in clean_query.lower():
                        score += 2.8

            # Fetch source reference for document citation
            source_ref = self.db.query(SourceReference).filter(SourceReference.policy_id == policy.id).first()

            if score > 0.5:
                scored_policies.append((score, policy, source_ref))

        # Hardware cross-policy resolution: if KB-03 scored high, surface ASSET-01 as well
        kb03_entry = next((item for item in scored_policies if item[1].id == "KB-03"), None)
        if kb03_entry and kb03_entry[0] >= 3.0:
            asset_entry = next((item for item in scored_policies if item[1].id == "ASSET-01"), None)
            if not asset_entry:
                asset_policy = self.db.query(Policy).filter(Policy.id == "ASSET-01").first()
                if asset_policy:
                    asset_ref = self.db.query(SourceReference).filter(SourceReference.policy_id == "ASSET-01").first()
                    scored_policies.append((kb03_entry[0] * 0.85, asset_policy, asset_ref))

        # Sort descending by score
        scored_policies.sort(key=lambda x: x[0], reverse=True)

        results: List[RetrievalResultSchema] = []
        max_score = scored_policies[0][0] if scored_policies else 1.0

        for score, pol, src in scored_policies[:top_k]:
            normalized_score = min(round(score / max(max_score, 1.0), 3), 1.0)
            
            section_name = src.section_name if src else ("Asset Management Policy (Extract)" if pol.id == "ASSET-01" else "1. Knowledge Base / Policies")
            page_num = src.page_number if src else (1 if pol.id != "ASSET-01" else 1)

            source_meta = SourceMetadataSchema(
                document_name=pol.source_document or "Assignment 2_DataPack_InternalServiceAgent.pdf",
                page_number=page_num,
                section=section_name,
                required_approvals=pol.required_approvals or [],
                time_constraints=pol.time_constraints,
                prohibited_actions=pol.prohibited_actions or []
            )

            results.append(RetrievalResultSchema(
                policy_id=pol.id,
                policy_title=pol.title,
                category=pol.category,
                relevant_text=pol.source_text,
                relevance_score=normalized_score,
                source_metadata=source_meta
            ))

        return RetrievalResponseSchema(
            query=clean_query,
            results_count=len(results),
            results=results,
            has_authoritative_match=len(results) > 0 and results[0].relevance_score >= 0.5
        )

    def validate_citations(self, cited_policy_ids: List[str], retrieved_results: List[RetrievalResultSchema]) -> Tuple[bool, List[str]]:
        """
        Enforce strict anti-hallucination constraint:
        Ensures the agent/LLM only cites policies that were explicitly returned by the retrieval engine.
        """
        valid_retrieved_ids = {r.policy_id for r in retrieved_results}
        valid_citations = [pid for pid in cited_policy_ids if pid in valid_retrieved_ids]
        is_strictly_grounded = (len(valid_citations) == len(cited_policy_ids)) and len(valid_citations) > 0
        return is_strictly_grounded, valid_citations
