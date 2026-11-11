"""Tổng hợp số liệu từ eval nguyên bản; không sửa file eval."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def summarize(path):
    report = json.loads(path.read_text(encoding='utf-8'))
    agent_usage = [u for c in report['cases'] for u in c['result']['usage']]
    judge_usage = [c['grade'].get('judge_usage', {}) for c in report['cases']]
    def tokens(items):
        return {key: sum(u.get(key, 0) for u in items) for key in ('prompt_tokens', 'completion_tokens', 'total_tokens')}
    return {
        'summary': report['summary'], 'config': report['config'],
        'agent_calls': len(agent_usage), 'agent_tokens': tokens(agent_usage),
        'judge_tokens': tokens(judge_usage),
        'cases': [{
            'id': c['id'], 'score': c['grade']['score'], 'status': c['result']['status'],
            'model_calls': len(c['result']['usage']),
            'tool_calls': sum(t['event'] == 'tool' for t in c['result']['trace']),
            'validations': sum(t['event'] == 'validation_missing_source' for t in c['result']['trace']),
            'violations': c['grade'].get('mechanical', {}).get('violations', []),
        } for c in report['cases']],
    }


if __name__ == '__main__':
    data = {name: summarize(ROOT / name) for name in ('eval_before.json', 'eval_after.json', 'eval_bonus.json') if (ROOT / name).exists()}
    if 'eval_before.json' in data and 'eval_after.json' in data:
        assert data['eval_before.json']['config'] == data['eval_after.json']['config'], 'Cấu hình trước/sau khác nhau'
    output = ROOT / 'artifacts' / 'eval_comparison.json'
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))
