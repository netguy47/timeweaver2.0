from src.predictive_core.core import PredictiveCore

def test_calculate_returns_expected_shape():
    core = PredictiveCore(cfg={})
    result = core.calculate("Test inquiry")
    for k in ["probability","band","drivers","scenarios","narrative","evidence"]:
        assert k in result, f"Missing key: {k}"
    assert 0.0 <= result["probability"] <= 1.0
    lo, hi = result["band"]
    assert 0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0 and lo <= hi
    assert isinstance(result["drivers"], list) and len(result["drivers"]) >= 1
    assert isinstance(result["scenarios"], list) and len(result["scenarios"]) >= 1
    assert "Our calculation" in result["narrative"]
