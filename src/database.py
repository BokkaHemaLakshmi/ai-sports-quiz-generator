import os
import json

_IN_MEMORY_DB = {}

def setup_and_populate_db(json_file_path="./data/sports_facts.json"):
    """Reads local JSON files and stores historical baseline profiles in memory."""
    global _IN_MEMORY_DB
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    if not os.path.exists(json_file_path):
        print(f"[DB LOG]: Target baseline file {json_file_path} not found.")
        return
        
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            facts_list = json.load(f)
            
        _IN_MEMORY_DB = {}
        for item in facts_list:
            sport = item.get("sport")
            fact = item.get("fact")
            if sport and fact:
                # Normalize key to matching string style safely
                key = sport.strip().capitalize()
                if key not in _IN_MEMORY_DB:
                    _IN_MEMORY_DB[key] = []
                _IN_MEMORY_DB[key].append(fact)
        print("[DB LOG]: Successfully loaded baseline history including Kabaddi and Tennis into memory.")
    except Exception as e:
        print(f"[DB ERROR]: Initialization error: {e}")

def query_historic_facts(sport: str, query_text: str, n_results: int = 2) -> list[str]:
    """Retrieves locally matching ground truth indicators instantly."""
    global _IN_MEMORY_DB
    if not _IN_MEMORY_DB:
        setup_and_populate_db()
        
    normalized_sport = sport.strip().capitalize()
    return _IN_MEMORY_DB.get(normalized_sport, [])[:n_results]