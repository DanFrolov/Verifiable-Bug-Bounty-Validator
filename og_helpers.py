import os
import og
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def handle_permit2_approval():
    """
    Ensures the agent's wallet is authorized to pay the x402 gateway for inferences.
    This function uses Permit2 for signature-based token approvals, allowing 
    autonomous agents to manage their compute budget efficiently.
    
    Target Network: Base Sepolia (or Nova Testnet as configured in the SDK)
    """
    # 1. Load the private key from environment variables
    private_key = os.getenv("OG_PRIVATE_KEY")
    
    if not private_key:
        raise ValueError("OG_PRIVATE_KEY environment variable is not set.")

    # 2. Initialize the OpenGradient LLM client
    # The SDK handles the connection to the appropriate network (e.g., Base Sepolia)
    llm = og.LLM(private_key=private_key)

    print(f"Checking Permit2 approval for wallet: {llm.address}...")

    try:
        # 3. Ensure the agent has approved at least 10 OPG tokens for the x402 gateway.
        # This is an idempotent call: it checks current allowance and only prompts 
        # for a signature if the allowance is insufficient.
        llm.ensure_opg_approval(opg_amount=10)
        
        print("Permit2 approval successful. Wallet is ready for x402 gateway payments.")
        return llm
        
    except Exception as e:
        print(f"Error during Permit2 approval: {str(e)}")
        raise

if __name__ == "__main__":
    # Test the helper function
    try:
        client = handle_permit2_approval()
        print(f"Client initialized for address: {client.address}")
    except Exception as e:
        print(f"Failed to initialize agent wallet: {e}")
