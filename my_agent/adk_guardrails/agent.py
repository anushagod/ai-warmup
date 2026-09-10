
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.models import LlmRequest, LlmResponse

# ==========================================
# 1. INPUT GUARDRAIL (Prompt Shield)
# ==========================================
def guard_input(request: LlmRequest) -> Optional[LlmResponse]:
    """
    Intercepts raw user messages or model requests before the LLM processes them.
    Blocks prompt injections or unauthorized instructions.
    """
    user_prompt = request.prompt.strip().lower()
    malicious_indicators = ["ignore instruction", "system prompt", "override role"]
    
    if any(indicator in user_prompt for indicator in malicious_indicators):
        return LlmResponse(
            text="Security Block: Prompt modification attempt detected.",
            status="blocked_by_input_guardrail"
        )
    return None  # Pass-through if safe

# ==========================================
# 2. IN-TOOL GUARDRAIL (Argument Interceptor)
# ==========================================
def guard_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Intercepts the parameters an agent passes to an integration tool.
    Enforces Role-Based Access Control (RBAC) and structural compliance.
    """
    # Defensive restriction for file operations
    if tool_name == "read_database_record":
        record_id = arguments.get("record_id")
        
        # Hard constraint: Enforce corporate bounds on data query ranges
        if record_id and int(record_id) > 9999:
            # Overwrite the payload to safely halt execution down the line or raise
            raise ValueError(f"Unauthorized Access Attempt: Record {record_id} out of bounds.")
            
    return arguments  # Returns modified or validated arguments

# ==========================================
# 3. OUTPUT GUARDRAIL (Data Leak / Safety Check)
# ==========================================
def guard_output(response: LlmResponse) -> LlmResponse:
    """
    Evaluates raw generated tokens before returning them to the user.
    Mutes toxicity, redacts accidental PII leaks, or stops hallucinations.
    """
    generated_text = response.text
    
    # Simple regex or string mock representing a PII detector (e.g. SSN or internal API tokens)
    if "INTERNAL_SECRET_" in generated_text:
        return LlmResponse(
            text="System Error: The requested content could not be displayed due to security restrictions.",
            status="blocked_by_output_guardrail"
        )
        
    return response  # Returns pristine response to client application

# ==========================================
# 4. REGISTER ALL LAYERS TO THE AGENT
# ==========================================
def query_database_mock(record_id: int) -> str:
    """A standard business function exposed as an agent tool."""
    return f"Data payload for record {record_id}"

secure_agent = Agent(
    name="CorporateGovernanceAgent",
    model="gemini-3.6-flash",
    instruction="You are a data retrieval assistant. Access records via your tool.",
    tools=[query_database_mock],
    
    # Hooking the full stack lifecycle callbacks into place
    before_model_callback=guard_input,
    before_tool_callback=guard_tool_call,
    after_model_callback=guard_output
)

