"""Các lỗi biên bổ sung cho loop, không gọi API."""
import unittest
from agent import run_agent
from status_tools import StatusTools
from test_lab import FakeProvider, tool_call, final


class RobustnessTests(unittest.TestCase):
    def test_provider_failure_is_traceable(self):
        result = run_agent('x', FakeProvider([]), StatusTools())
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['trace'][0]['event'], 'provider_error')

    def test_non_object_arguments(self):
        fake = FakeProvider([tool_call('a', 'get_status', '[]'), final()])
        result = run_agent('x', fake, StatusTools())
        self.assertEqual(result['trace'][1]['result']['error'], 'INVALID_ARGUMENTS')

    def test_unexpected_tool_exception_is_observation(self):
        class BrokenTools:
            def execute(self, name, args):
                raise RuntimeError('sensitive exception body')
        result = run_agent('x', FakeProvider([tool_call('a', 'get_status', '{}'), final()]), BrokenTools())
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['trace'][1]['result']['error'], 'RuntimeError')
        self.assertNotIn('sensitive', str(result))

    def test_rate_limit_budget_and_live_wait(self):
        for delay, expected_calls in [(0, 2), ('60', 1), (None, 1)]:
            with self.subTest(delay=delay):
                class Limited:
                    count = 0
                    def execute(self, name, args):
                        self.count += 1
                        return dict(ok=False, error='RATE_LIMITED', retry_after=delay)
                tools = Limited()
                responses = [tool_call(str(i), 'get_status', '{"provider":"github"}') for i in range(3)] + [final('Chưa lấy được dữ liệu.')]
                result = run_agent('x', FakeProvider(responses), tools)
                self.assertEqual(tools.count, expected_calls)
                self.assertEqual(result['status'], 'completed')

    def test_invalid_budget_and_empty_answer(self):
        self.assertEqual(run_agent('x', FakeProvider([]), StatusTools(), 0)['status'], 'error')
        self.assertEqual(run_agent('x', FakeProvider([final('')]), StatusTools())['status'], 'error')
