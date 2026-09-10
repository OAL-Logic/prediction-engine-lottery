import pytest
import time
import json
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def mock_fetch_cooldown():
    import engine
    
    # Pre-import heavy modules on the main thread to prevent PySide6/Shiboken import deadlocks in QThreads during tests
    try:
        import engine.modules.environment
        import engine.modules.cosmic
        import engine.modules.geometry
        import engine.strategies
        import engine.cli.utils
    except ImportError:
        pass

    engine_dir = Path(engine.__file__).resolve().parent
    project_root = engine_dir.parent
    data_dir = project_root / "data"
    cache_dir = data_dir / "cache"
    
    # Write cooldown files to prevent network fetches during tests
    game_slugs = ["lotofacil", "megasena", "quina"]
    for slug in game_slugs:
        cooldown_file = data_dir / f".last_fetch_{slug}"
        try:
            cooldown_file.write_text(str(time.time()))
        except Exception:
            pass
            
    # Write environment jitter cache to prevent solar/seismic network fetches
    cache_file = cache_dir / "env_jitter.json"
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        jitter_mock = {
            "timestamp": time.time(),
            "jitter": {
                "kp": 3.0,
                "f107": 120.0,
                "seismic_mag": 0.0,
                "j_solar": 0.0,
                "j_seismic": 0.0,
                "total_boost": 0.0
            }
        }
        cache_file.write_text(json.dumps(jitter_mock))
    except Exception:
        pass
            
    yield
    
    # Clean up cooldown files after session
    for slug in game_slugs:
        cooldown_file = data_dir / f".last_fetch_{slug}"
        if cooldown_file.exists():
            try:
                cooldown_file.unlink()
            except Exception:
                pass
                
    # Clean up mock jitter cache
    if cache_file.exists():
        try:
            cache_file.unlink()
        except Exception:
            pass

