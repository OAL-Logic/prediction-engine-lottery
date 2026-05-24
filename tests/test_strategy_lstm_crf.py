import pytest
import pandas as pd
import torch
import os
from engine.adapters.br.lotofacil import LotofacilAdapter
from engine.strategies.deep.lstm_crf import LSTMCRFStrategy

def test_lstm_crf_strategy_initialization():
    strategy = LSTMCRFStrategy()
    assert strategy.name == "lstm_crf"

def test_lstm_crf_model_forward():
    from engine.strategies.deep.lstm_crf import LstmCRFModel
    input_dim = 10
    hidden_dim = 20
    output_dim = 25
    seq_length = 15
    model = LstmCRFModel(input_dim, hidden_dim, output_dim, seq_length)
    
    x = torch.randn(1, 10, input_dim) # batch, seq, features
    preds = model(x)
    assert len(preds) == 1 # batch size
    assert len(preds[0]) == seq_length

@pytest.mark.asyncio
async def test_lstm_crf_scoring():
    # Setup Mock Data
    df = pd.DataFrame({
        "draw_id": list(range(1, 61)),
        "numbers": [[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]] * 60
    })
    
    adapter = LotofacilAdapter()
    strategy = LSTMCRFStrategy()
    
    # We might need to train first or mock the model load
    scores = strategy.score(df, adapter.rules)
    assert len(scores) == 25
    assert all(0.0 <= s <= 1.0 for s in scores.values())

def test_lstm_crf_save_load():
    df = pd.DataFrame({
        "draw_id": list(range(1, 61)),
        "numbers": [[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]] * 60
    })
    adapter = LotofacilAdapter()
    strategy = LSTMCRFStrategy(hidden_dim=16)
    
    # Train and Save
    strategy.train(df, adapter.rules, epochs=1)
    
    game_slug = adapter.rules.name.lower().replace(" ", "_")
    assert os.path.exists(f"data/model_cache/lstm_crf_{game_slug}.pt")
    
    # New instance and Load
    strategy2 = LSTMCRFStrategy()
    loaded = strategy2.load(adapter.rules)
    assert loaded is True
    assert strategy2.hidden_dim == 16
    assert strategy2.model is not None
