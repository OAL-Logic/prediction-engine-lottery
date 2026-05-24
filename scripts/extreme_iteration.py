import subprocess
import json
import re

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def get_lotofacil_15_hit():
    print("Running Extreme Iteration for Lotofácil 15-hit search...")
    # Generate 20 tickets from Stacking AI
    output = run_cmd("./lottery suggest br/lotofacil --strategy stacking_ai --limit 150 --count 20 --temp 0.2")
    
    # Extract tickets
    tickets = re.findall(r"Ticket \d+: ([\d, ]+)", output)
    
    best_hit = 0
    best_ticket = ""
    
    for t_str in tickets:
        # Simulate against the full history to see best historical hit
        sim_out = run_cmd(f'./lottery simulate br/lotofacil "{t_str}" --range all')
        # Check if 15-match exists
        if "15-match" in sim_out:
            print(f"FOUND 15-HIT CANDIDATE: {t_str}")
            return t_str
        
        # Keep track of best hit found
        match = re.search(r"(\d+)-match\s+(\d+)", sim_out)
        if match:
            hit_level = int(match.group(1))
            if hit_level > best_hit:
                best_hit = hit_level
                best_ticket = t_str
                
    print(f"No 15-hit found in this batch. Best was {best_hit}-match.")
    return best_ticket

ticket = get_lotofacil_15_hit()
print(f"Final Suggestion for Lotofácil: {ticket}")
