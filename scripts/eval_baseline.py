"""Chạy runner gốc với baseline tắt source gate; mọi cấu hình khác giữ nguyên."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'evals'))
from artifacts.agent_before import _run_agent
import run_evals


def baseline(question, provider, tools, max_steps=6):
    return _run_agent(question, provider, tools, max_steps, validate_sources=False)


if __name__ == '__main__':
    run_evals.run_agent = baseline
    sys.exit(run_evals.main())
