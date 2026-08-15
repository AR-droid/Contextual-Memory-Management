import os
import json
import csv

def main():
    conditions = ["original", "typed", "typed_epistemic"]
    target_samples = [
        "sycophancy_001", "sycophancy_002", "sycophancy_004", "sycophancy_005", 
        "sycophancy_006", "sycophancy_008", "sycophancy_009",
        "beneficial_000", "beneficial_001", "beneficial_002"
    ]
    
    results_flat = []
    summary = {c: {"sycophancy": {"count":0, "fails":0, "scores":[]}, "beneficial": {"count":0, "fails":0, "scores":[]}} for c in conditions}
    
    all_data = {c: {} for c in conditions}
    
    for cond in conditions:
        cond_dir = f"results/epistemic_pilot/raw/{cond}"
        if not os.path.exists(cond_dir): continue
        
        for f in os.listdir(cond_dir):
            if not f.endswith(".json"): continue
            
            with open(os.path.join(cond_dir, f)) as file:
                data = json.load(file)
                
            sample_id = data["sample_id"]
            cat = data["category"]
            score = data["judge_score"]
            is_fail = data["is_failure"]
            
            all_data[cond][sample_id] = data
            
            results_flat.append({
                "sample_id": sample_id,
                "category": cat,
                "condition": cond,
                "score": score,
                "is_failure": is_fail
            })
            
            summary[cond][cat]["count"] += 1
            if is_fail:
                summary[cond][cat]["fails"] += 1
            if score > 0:
                summary[cond][cat]["scores"].append(score)
                
    # Calculate stats
    for cond in conditions:
        for cat in ["sycophancy", "beneficial"]:
            s = summary[cond][cat]
            if s["count"] > 0:
                s["failure_rate"] = s["fails"] / s["count"]
                s["mean_score"] = sum(s["scores"]) / len(s["scores"]) if s["scores"] else 0
            else:
                s["failure_rate"] = 0
                s["mean_score"] = 0
                
    with open("results/epistemic_pilot/summary.json", "w") as out:
        json.dump(summary, out, indent=2)
        
    with open("results/epistemic_pilot/results.csv", "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["sample_id", "category", "condition", "score", "is_failure"])
        writer.writeheader()
        writer.writerows(results_flat)
        
    # Generate side-by-side comparison for analysis
    with open("results/epistemic_pilot/comparison.md", "w") as out:
        for sample_id in target_samples:
            out.write(f"# SAMPLE: {sample_id}\n\n")
            cat = "sycophancy" if "sycophancy" in sample_id else "beneficial"
            
            for cond in conditions:
                data = all_data[cond].get(sample_id)
                if data:
                    out.write(f"## {cond.upper()}\n")
                    out.write(f"**Score:** {data['judge_score']}\n\n")
                    out.write(f"**Response:**\n{data['target_response']}\n\n")
                    out.write(f"**Judge Reasoning:**\n{data['judge_response']}\n\n")
                else:
                    out.write(f"## {cond.upper()}\nMissing data.\n\n")
            out.write("---\n\n")
            
    print("Post-processing complete. Wrote summary.json, results.csv, comparison.md")

if __name__ == "__main__":
    main()
