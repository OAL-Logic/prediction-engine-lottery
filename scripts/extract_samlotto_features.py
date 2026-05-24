import re
import json
import os

def extract_features(input_path, output_path):
    # Regex patterns
    # Matches strings in quotes: "..."
    string_pattern = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
    # Matches function-like names (sub_XXXXXX, j_sub_XXXXXX, or names with CamelCase/Underscores)
    symbol_pattern = re.compile(r'\b(sub_[0-9a-fA-F]+|j_sub_[0-9a-fA-F]+|[a-zA-Z_][a-zA-Z0-9_]{5,})\b')
    
    features = {
        "strings": set(),
        "potential_functions": set(),
        "ui_elements": set(),
        "sql_queries": set(),
        "network_indicators": set()
    }
    
    # Common UI keywords in Win32/Delphi/C++ apps
    ui_keywords = {'Form', 'Button', 'Btn', 'Edit', 'Label', 'Menu', 'Grid', 'List', 'Dialog', 'Wnd', 'Click', 'Show', 'Hide'}
    # SQL keywords
    sql_keywords = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE', 'JOIN', 'CREATE TABLE', 'DROP TABLE'}
    # Network keywords
    net_keywords = {'http://', 'https://', 'ftp://', 'www.', '.com', '.net', '.org', 'socket', 'connect', 'send', 'recv'}

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Processing {input_path}...")
    line_count = 0
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_count += 1
            if line_count % 100000 == 0:
                print(f"Processed {line_count} lines...")

            # Extract strings
            found_strings = string_pattern.findall(line)
            for s in found_strings:
                if len(s) > 3:
                    # Basic cleaning
                    s_clean = s.strip()
                    if s_clean:
                        features["strings"].add(s_clean)
                        
                        # Check for SQL in strings
                        if any(k in s_clean.upper() for k in sql_keywords):
                            features["sql_queries"].add(s_clean)
                        
                        # Check for Network in strings
                        if any(k in s_clean.lower() for k in net_keywords):
                            features["network_indicators"].add(s_clean)
                        
                        # Check for UI in strings
                        if any(k in s_clean for k in ui_keywords):
                            features["ui_elements"].add(s_clean)

            # Extract symbols/functions
            found_symbols = symbol_pattern.findall(line)
            for sym in found_symbols:
                # Filter out some noise
                if sym.startswith('sub_') or sym.startswith('j_sub_'):
                    features["potential_functions"].add(sym)
                elif any(k in sym for k in ui_keywords):
                    features["ui_elements"].add(sym)
                elif len(sym) > 8: # Longer names are more likely to be descriptive
                    features["potential_functions"].add(sym)

    # Convert sets to sorted lists for JSON serialization
    output_data = {
        "summary": {
            "total_lines": line_count,
            "unique_strings_count": len(features["strings"]),
            "unique_functions_count": len(features["potential_functions"]),
            "ui_elements_count": len(features["ui_elements"]),
            "sql_queries_count": len(features["sql_queries"]),
            "network_indicators_count": len(features["network_indicators"])
        },
        "strings_sample": sorted(list(features["strings"]))[:1000], # Limit samples to keep file size reasonable
        "potential_functions_sample": sorted(list(features["potential_functions"]))[:1000],
        "ui_elements": sorted(list(features["ui_elements"])),
        "sql_queries": sorted(list(features["sql_queries"])),
        "network_indicators": sorted(list(features["network_indicators"]))
    }

    # If strings are too many, we might want to filter more or just take the most "interesting" ones
    # For now, let's just save the categorized ones and a sample of others.
    
    # Refined strings: filter out common garbage
    interesting_strings = [s for s in features["strings"] if any(c.isalpha() for c in s) and len(s) > 5]
    output_data["interesting_strings"] = sorted(interesting_strings)[:2000]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Done! Summary saved to {output_path}")

if __name__ == "__main__":
    extract_features("BinaryNinja_SamLotto_linear.txt", "data/extracted_samlotto_summary.json")
