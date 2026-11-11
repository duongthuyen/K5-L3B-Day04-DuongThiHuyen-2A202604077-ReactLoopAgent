"""Nạp .env cục bộ và chạy script Python; không in giá trị key, không eval shell."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'PROVIDER', 'MODEL', 'JUDGE_PROVIDER', 'JUDGE_MODEL',
           'OPENAI_API_KEY', 'GEMINI_API_KEY', 'ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY'}


def main():
    env = os.environ.copy()
    for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].strip()
        name, separator, value = line.partition('=')
        name, value = name.strip(), value.strip()
        if not separator or name not in ALLOWED:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if value:
            env[name] = value
    env['PYTHONUTF8'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    if len(sys.argv) < 2:
        print('Usage: python scripts/with_env.py <script.py> [arguments]')
        return 2
    return subprocess.call([sys.executable, '-X', 'utf8', *sys.argv[1:]], cwd=ROOT, env=env)


if __name__ == '__main__':
    sys.exit(main())
