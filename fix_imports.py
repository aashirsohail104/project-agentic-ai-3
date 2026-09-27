import os
import re

project_packages = ['context', 'config', 'data', 'guardrails', 'hooks', 'runner', 'tools', 'tracing', 'support_agents']

for root, dirs, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()

            original = content
            for pkg in project_packages:
                content = re.sub(
                    rf'^from {pkg}\b',
                    f'from src.{pkg}',
                    content,
                    flags=re.MULTILINE
                )
                content = re.sub(
                    rf'^import {pkg}\b',
                    f'import src.{pkg}',
                    content,
                    flags=re.MULTILINE
                )

            if content != original:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                print(f'Fixed: {path}')

print('Done')