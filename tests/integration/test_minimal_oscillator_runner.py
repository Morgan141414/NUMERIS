import importlib.util
import json
from pathlib import Path


def _load_runner():
    path = Path(__file__).parents[2] / "scripts" / "run_minimal_oscillator.py"
    spec = importlib.util.spec_from_file_location("minimal_oscillator_runner", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bounded_runner_is_explicitly_not_implemented_without_candidate(tmp_path):
    runner = _load_runner()
    report = runner.run_minimal_prototype()
    (tmp_path / "minimal.json").write_text(json.dumps(report), encoding="utf-8")

    assert report["scope"] == "exploratory"
    assert report["campaign"] == "bounded"
    assert report["protocol"]["baseline"]["method"] == "DOP853"
    assert report["protocol"]["manifest_commit"]
    assert report["protocol"]["paired_seeds"] == [0, 1]
    assert report["candidate"]["status"] == "NOT-IMPLEMENTED"
    assert report["candidate"]["substitution_forbidden"] is True
    assert len(report["runs"]) == 2
    assert all(item["candidate"]["status"] == "NOT-IMPLEMENTED" for item in report["runs"])
    assert "baseline" in report["primary"]["parameter_rmse"]
    assert report["primary"]["parameter_rmse"]["candidate"] is None
    assert report["primary"]["bootstrap"]["status"] == "not_computable"
    assert report["primary"]["decision"] == "NOT-IMPLEMENTED"
    json.loads((tmp_path / "minimal.json").read_text(encoding="utf-8"))


def test_bounded_runner_preserves_over_budget_status():
    runner = _load_runner()
    report = runner.run_minimal_prototype(seeds=[3], max_rhs_evals=1)
    assert report["runs"][0]["baseline"]["status"] == "over_budget"
    assert report["runs"][0]["candidate"]["status"] == "NOT-IMPLEMENTED"
    assert report["primary"]["bootstrap"]["status"] == "not_computable"
