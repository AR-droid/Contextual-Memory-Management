import json

results = []
import os
for cat in ['cross_domain', 'sycophancy', 'beneficial']:
    for f in os.listdir(f'results/pilot/raw/{cat}'):
        if f.endswith('.json'):
            with open(f'results/pilot/raw/{cat}/{f}') as file:
                results.append(json.load(file))

failed = [r for r in results if r['evaluation'].get('is_failure')]
with open('results/pilot/failure_analysis.md', 'w') as f:
    f.write('# Failure Analysis\n\n')
    for r in failed:
        f.write(f"## Sample {r['sample']['sample_id']} ({r['metadata']['category']})\n")
        f.write(f"- **Score:** {r['evaluation']['score']}\n")
        f.write(f"- **Judge Reasoning:** {r['judgment']['reasoning']}\n\n")
        f.write(f"### Query\n{r['sample']['query']}\n\n")
        f.write(f"### Model Response\n{r['generation']['response']}\n\n")
        f.write(f"### Classification\n")
        
        reasoning = r['judgment']['reasoning'].lower()
        if 'astrology' in reasoning or 'fact' in reasoning:
            cat = 'belief treated as fact'
        else:
            cat = 'memory-induced agreement'
            
        opts = [
            'irrelevant personalization', 'cross-domain leakage', 
            'belief treated as fact', 'memory-induced agreement', 
            'inappropriate use of sensitive information', 'unclear', 'other'
        ]
        
        for opt in opts:
            check = 'x' if opt == cat else ' '
            f.write(f"- [{check}] {opt.capitalize()}\n")
        f.write("---\n\n")
