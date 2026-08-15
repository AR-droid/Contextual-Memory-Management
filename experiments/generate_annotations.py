import json
import os
import re

def classify_memory(mem):
    mem_lower = mem.lower()
    
    if "believes" in mem_lower or "feels that" in mem_lower or "strongly believes" in mem_lower or "thesis is that" in mem_lower or "stated opinion" in mem_lower:
        return "USER_BELIEF", "Explicit ideological or philosophical belief."
    elif "prefers" in mem_lower or "enjoys" in mem_lower or "favorite" in mem_lower or "despises" in mem_lower or "unwinds" in mem_lower:
        return "USER_PREFERENCE", "Subjective taste or preference."
    elif "planning" in mem_lower or "training" in mem_lower or "wants to" in mem_lower:
        return "USER_GOAL", "Current objective or aspiration."
    elif "stated:" in mem_lower or "vetoed" in mem_lower or "insists" in mem_lower:
        return "USER_OPINION", "Specific behavioral stance or opinion."
    else:
        return "USER_FACT", "Objective background information."

def main():
    target_samples = [
        "sycophancy_001", "sycophancy_002", "sycophancy_004", "sycophancy_005", 
        "sycophancy_006", "sycophancy_008", "sycophancy_009",
        "beneficial_000", "beneficial_001", "beneficial_002"
    ]
    
    annotations = {}
    
    for cat in ["sycophancy", "beneficial"]:
        cat_dir = os.path.join("results/pilot/raw", cat)
        if not os.path.exists(cat_dir):
            continue
        for f in os.listdir(cat_dir):
            if not f.endswith(".json"): continue
            
            with open(os.path.join(cat_dir, f)) as file:
                data = json.load(file)
                sample_id = data["sample"]["sample_id"]
                
                if sample_id in target_samples:
                    sample_anns = []
                    for mem in data["sample"]["memories"]:
                        mtype, reason = classify_memory(mem)
                        sample_anns.append({
                            "original_memory": mem,
                            "assigned_type": mtype,
                            "reason": reason
                        })
                    annotations[sample_id] = sample_anns
                    
    os.makedirs("results/epistemic_pilot", exist_ok=True)
    with open("results/epistemic_pilot/memory_annotations.json", "w") as out:
        json.dump(annotations, out, indent=2)
        
    print("Generated memory_annotations.json")

if __name__ == "__main__":
    main()
