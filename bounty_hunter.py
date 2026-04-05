import os
import json
import opengradient as og
from web3 import Web3
from opengradient.client.opg_token import _get_web3_and_contract
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, List

# Load environment variables
load_dotenv()

# --- MODELS ---
class SecurityAnalysis(BaseModel):
    """Schema for the security analyst's report."""
    vulnerabilities_found: List[str] = Field(description="List of potential security regressions or bugs found in the diff.")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(description="Overall security risk level of the PR.")
    summary: str = Field(description="Summary of the security scan.")

class FinalVerification(BaseModel):
    """Schema for the final verifier's report."""
    reasoning: str = Field(description="Detailed analysis combining the security report and the original issue.")
    status: Literal["VERIFIED", "REJECTED", "NEEDS_HUMAN_REVIEW"] = Field(description="The final status of the verification.")
    confidence_score: int = Field(description="Confidence score from 0 to 100.", ge=0, le=100)

# --- UTILS ---
def get_llm_client():
    # Prefer `AGENT_PRIVATE_KEY`, fall back to `OG_PRIVATE_KEY` for convenience.
    AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
    OG_PRIVATE_KEY = os.getenv("OG_PRIVATE_KEY")
    private_key = AGENT_PRIVATE_KEY or OG_PRIVATE_KEY

    if not private_key or private_key == "0x0000000000000000000000000000000000000000000000000000000000000000":
        st.error("❌ AGENT_PRIVATE_KEY (or OG_PRIVATE_KEY) is missing! Please set it in your environment variables or secrets.")
        st.stop()

    try:
        return og.LLM(private_key=private_key)
    except Exception as e:
        st.error(f"Failed to initialize LLM client: {e}")
        st.stop()

def setup_agent_wallet(llm):
    """Ensures the agent's wallet is ready for autonomous commerce."""
    try:
        # Show the on-chain OPG balance for the agent wallet so you can
        # verify the exact address being checked by the SDK matches the one
        # you inspected in a block explorer.
        try:
            w3, token, _ = _get_web3_and_contract()
            owner = Web3.to_checksum_address(llm._wallet_account.address)
            balance_raw = token.functions.balanceOf(owner).call()
            balance = balance_raw / 10**18
            st.sidebar.write(f"**Agent Address:** {owner}")
            st.sidebar.write(f"**OPG Balance (on-chain):** {balance}")
        except Exception as e:
            st.sidebar.error(f"Failed to read on-chain OPG balance: {e}")
            balance = None
        if balance < 0.05:
            st.sidebar.warning("Low OPG balance! Visit [faucet.opengradient.ai](https://faucet.opengradient.ai)")
    except Exception as e:
        st.sidebar.error(f"Balance check failed: {e}")

    # The SDK requires a minimum `min_allowance` of 0.1 OPG
    approval = llm.ensure_opg_approval(0.1)
    st.sidebar.write(f"**Current Allowance:** {approval.allowance_before}")
    return approval

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bounty-Hunter Audit", page_icon="🛡️")

st.title("🛡️ Bounty-Hunter: Verifiable AI Audit")
st.markdown("""
This agent uses **OpenGradient's TEE-secured LLMs** to perform verifiable audits of GitHub Pull Requests. 
All reasoning is recorded on-chain via the **x402 protocol** for immutable 'Proof of Reasoning'.
""")

# Sidebar for Wallet Info
st.sidebar.header("Agent Wallet (Nova Testnet)")
llm = get_llm_client()
setup_agent_wallet(llm)

# Main Inputs
st.subheader("Audit Inputs")
issue_desc = st.text_area("GitHub Issue Description", placeholder="Describe the bug or feature request...", height=150)
pr_diff = st.text_area("PR Code Diff", placeholder="Paste the git diff here...", height=200)

if st.button("🚀 Launch Verifiable Audit", type="primary"):
    if not issue_desc or not pr_diff:
        st.error("Please provide both the Issue Description and the PR Diff.")
    else:
        with st.status("Running Multi-Agent Audit...", expanded=True) as status:
            # --- AGENT 1: THE ANALYST ---
            st.write("🔍 [Agent 1: The Analyst] Scanning for security regressions...")
            analyst_prompt = f"Security audit this diff: {pr_diff}. Return JSON: vulnerabilities_found, risk_level, summary."
            
            analyst_res = llm.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",
                messages=[{"role": "system", "content": "You are a security analyst. Return valid JSON."},
                          {"role": "user", "content": analyst_prompt}],
                response_format={"type": "json_object"},
                tee=True,
                x402_settlement_mode="INDIVIDUAL_FULL"
            )
            analyst_data = json.loads(analyst_res.choices[0].message.content)
            security_report = SecurityAnalysis(**analyst_data)
            
            # --- AGENT 2: THE VERIFIER ---
            st.write("✅ [Agent 2: The Verifier] Confirming issue resolution...")
            verifier_prompt = f"Issue: {issue_desc}\nDiff: {pr_diff}\nSecurity Report: {security_report.model_dump_json()}\nReturn JSON: reasoning, status, confidence_score."
            
            verifier_res = llm.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",
                messages=[{"role": "system", "content": "You are a bounty verifier. Return valid JSON."},
                          {"role": "user", "content": verifier_prompt}],
                response_format={"type": "json_object"},
                tee=True,
                x402_settlement_mode="INDIVIDUAL_FULL"
            )
            verifier_data = json.loads(verifier_res.choices[0].message.content)
            
            # Logic for status
            if verifier_data.get("confidence_score", 0) < 80 or security_report.risk_level in ["HIGH", "CRITICAL"]:
                verifier_data["status"] = "NEEDS_HUMAN_REVIEW"
            
            final_report = FinalVerification(**verifier_data)
            status.update(label="Audit Complete!", state="complete", expanded=False)

        # --- DISPLAY RESULTS ---
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Final Status", final_report.status)
        with col2:
            st.metric("Confidence Score", f"{final_report.confidence_score}%")

        st.subheader("Reasoning")
        st.info(final_report.reasoning)

        st.subheader("Security Scan Summary")
        if security_report.risk_level in ["HIGH", "CRITICAL"]:
            st.error(f"Risk Level: {security_report.risk_level}")
        else:
            st.warning(f"Risk Level: {security_report.risk_level}")
        st.write(security_report.summary)
        
        # On-Chain Proofs
        st.subheader("⛓️ On-Chain Proofs (x402)")
        
        # Analyst Proof
        st.markdown(f"**Analyst TX:** [{analyst_res.x402_info.transaction_hash}](https://explorer.opengradient.ai/tx/{analyst_res.x402_info.transaction_hash})")
        if hasattr(analyst_res.x402_info, 'tee_signature') and analyst_res.x402_info.tee_signature:
            st.success("✅ Hardware Attested (Analyst)")
            
        # Verifier Proof
        st.markdown(f"**Verifier TX:** [{verifier_res.x402_info.transaction_hash}](https://explorer.opengradient.ai/tx/{verifier_res.x402_info.transaction_hash})")
        if hasattr(verifier_res.x402_info, 'tee_signature') and verifier_res.x402_info.tee_signature:
            st.success("✅ Hardware Attested (Verifier)")

st.caption("Powered by OpenGradient Nova Testnet & x402 Payment Standard.")
