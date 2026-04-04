# Bounty-Hunter: Verifiable AI Bug Bounty Validator 🏹

Bounty-Hunter is an autonomous security agent built on the **OpenGradient Network**. It leverages Verifiable AI Reasoning and Trusted Execution Environments (TEEs) to automate the verification of bug fixes in bounty programs.

---

## 🔴 The Problem
In traditional bug bounty programs, human triagers must manually run and verify code submitted by researchers. This process is:
* **Slow:** Significant delays in payouts for researchers.
* **Subjective:** Vulnerable to human error, fatigue, or bias.
* **Opaque:** No immutable, public record of why a fix was accepted or rejected.

## 💡 The Solution
Bounty-Hunter uses **Verifiable AI Reasoning** to provide a "Hardware-Attested Proof of Fix."

* **Multi-Agent Audit:** A specialized "Security Analyst" agent scans for regressions, while a "Lead Auditor" verifies the fix logic.
* **Hardware Security:** Reasoning runs inside **Intel TDX enclaves (TEEs)**, ensuring the logic hasn't been tampered with by the node operator.
* **On-Chain Audit Trail:** Every verdict is recorded on the **OpenGradient Nova Testnet** via the `INDIVIDUAL_FULL` settlement mode, creating a permanent, auditable receipt for the bounty program.

---

## 🛠️ Technical Stack
* **AI Infrastructure:** [OpenGradient Network](https://opengradient.ai/)
* **Compute Layer:** Hybrid AI Compute Architecture (HACA) 
* **Verification:** Trusted Execution Environments (TEE)
* **Payment Protocol:** x402 (Autonomous stablecoin micropayments)
* **Memory Layer:** MemSync (Persistent context to prevent redundant audits)
* **Frontend:** Streamlit
* **Network:** Nova Testnet (Chain ID: `10740`) 

---

## 🧠 Key Features
* **Deterministic Token Management:** Configured for low-balance environments (testing with `0.05 $OPG`) using idempotent Permit2 approvals.
* **Proof of Reasoning:** Generates a direct link to the **OpenGradient Explorer** for every audit conducted.
* **Audit Vault:** Uses `memsync.add_memory()` to store previous PR fingerprints, ensuring you never pay for the same audit twice.
* **Autonomous Settlement:** The agent "pays for its own brain" using the **x402 gateway standard**. 

---

## 🏃 Getting Started

### 1. Prerequisites
* Python 3.10+
* A wallet funded with testnet `$OPG` (Base Sepolia) and `$ETH` (Nova Testnet). 
* *Note: Get tokens at the [OpenGradient Faucet](https://faucet.opengradient.ai/).*

### 2. Installation
```bash
git clone [https://github.com/DanFrolov/Verifiable-Bug-Bounty-Validator/](https://github.com/DanFrolov/Verifiable-Bug-Bounty-Validator/)
cd bounty-hunter
pip install -r requirements.txt
