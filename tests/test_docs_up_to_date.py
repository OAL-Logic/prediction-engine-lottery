import os
import re

def test_docs_contain_all_strategies():
    """
    Ensures that every registered strategy in the engine is mentioned
    in the USER_GUIDE and technical-spec.md, preventing documentation drift.
    """
    from engine.strategies import list_strategies
    
    # Import strategy modules to trigger registration
    import engine.strategies.statistical  # noqa
    import engine.strategies.fun          # noqa
    try:
        import engine.strategies.ml       # noqa
    except ImportError:
        pass
    try:
        import engine.strategies.deep     # noqa
    except ImportError:
        pass

    strategies = list_strategies()
    
    # Locate docs
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    user_guide_path = os.path.join(docs_dir, "user_guides", "user-guide.md")
    tech_spec_path = os.path.join(docs_dir, "architecture", "technical-spec.md")    
    with open(user_guide_path, "r", encoding="utf-8") as f:
        user_guide = f.read().lower()
        
    with open(tech_spec_path, "r", encoding="utf-8") as f:
        tech_spec = f.read().lower()

    missing_in_user_guide = []
    missing_in_tech_spec = []

    for strat in strategies:
        # Check if the strategy name or its class name / description is mentioned
        name = strat["name"].lower()
        
        # We'll allow fuzzy matching: either the name is directly mentioned, 
        # or words from its name (like 'quantum' for 'quantum_anneal').
        # Using the base name without underscores usually works well.
        clean_name = name.replace("_", " ")
        parts = clean_name.split()
        
        # Check user guide
        found_in_ug = any(part in user_guide for part in parts) or name in user_guide
        if not found_in_ug:
            missing_in_user_guide.append(name)
            
        # Check tech spec
        found_in_ts = any(part in tech_spec for part in parts) or name in tech_spec
        if not found_in_ts:
            missing_in_tech_spec.append(name)

    # Some strategies might legitimately be missing if they are extremely basic,
    # but the goal is to have the core engine fully documented.
    # We can refine the logic if it becomes too strict.
    
    # We won't strictly assert failure for every single one to avoid breaking CI 
    # immediately on minor helper strategies, but we'll print warnings or fail 
    # if major ones are missing.
    
    error_msg = []
    if missing_in_user_guide:
        error_msg.append(f"Strategies missing from user-guide.md: {', '.join(missing_in_user_guide)}")
    
    if missing_in_tech_spec:
        error_msg.append(f"Strategies missing from technical-spec.md: {', '.join(missing_in_tech_spec)}")
        
    if error_msg:
        # We only assert if there's a huge discrepancy (e.g. > 5 missing)
        # to enforce it gracefully. Or we can just print it.
        # Let's assert to ensure developers see it.
        print("\n".join(error_msg))
        assert False, "Documentation drift detected! Please update the docs with the new strategies.\n" + "\n".join(error_msg)

