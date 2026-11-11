"""Demo offline: provider được lập trình sẵn; không phải LLM eval."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from agent import _run_agent
from status_tools import StatusTools
from test_lab import FakeProvider, tool_call, final


def demo(validate):
    tools = StatusTools()
    incident = tools.get_status('github', 'Actions')['incidents'][0]
    detail = tools.get_incident_details('github', incident['id'])
    draft = 'Theo snapshot, incident có trạng thái ' + detail['status'] + '.'
    responses = [
        tool_call('status-1', 'get_status', json.dumps({'provider': 'github', 'component': 'Actions'})),
        tool_call('detail-1', 'get_incident_details', json.dumps({'provider': 'github', 'incident_id': incident['id']})),
        final(draft), final(draft + ' Nguồn: ' + detail['url']),
    ]
    return _run_agent('Kiểm tra GitHub Actions trong snapshot.', FakeProvider(responses), tools, 5, validate_sources=validate)


if __name__ == '__main__':
    output = {'kind': 'offline_scripted_demo_not_llm_eval', 'before': demo(False), 'after': demo(True)}
    path = ROOT / 'artifacts' / 'offline_validation_demo.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(path)
    for version in ('before', 'after'):
        item = output[version]
        print(version, item['status'], 'model_calls=', len(item['usage']))
