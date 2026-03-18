from typing import Dict, Any

def router(state: Dict[str, Any]) -> str:
    # Agar error hai toh turant workflow rok do
    if state.get("final_error"):
        return "end"
        
    # Agar aur URLs process karne bache hain, toh loop continue rakho
    if state["current_index"] < len(state["urls"]):
        return "continue"
        
    # Jab saari list khatam ho jaye, tab LLM agent ko call lagao
    return "match_jobs"
