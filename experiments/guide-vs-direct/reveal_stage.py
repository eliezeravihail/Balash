#!/usr/bin/env python3
"""Reveal exactly one experiment stage to a condition workspace.

This does not run an agent. It creates/overwrites USER_REQUEST.md so an external
coding-agent session can be pointed at a workspace without exposing later stages.
"""
from pathlib import Path
import argparse
import shutil

ROOT = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('condition', choices=['direct', 'guide'])
    ap.add_argument('stage', type=int, choices=[1,2,3,4])
    ap.add_argument('workspace', type=Path)
    args = ap.parse_args()

    ws = args.workspace.resolve()
    ws.mkdir(parents=True, exist_ok=True)

    instructions = ROOT / 'conditions' / args.condition / 'INSTRUCTIONS.md'
    shutil.copy2(instructions, ws / 'AGENT_INSTRUCTIONS.md')

    if args.condition == 'guide':
        src = ROOT / 'conditions' / 'guide' / '.agents'
        dst = ws / '.agents'
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        state_src = ROOT / 'conditions' / 'guide' / '.balash'
        state_dst = ws / '.balash'
        if not state_dst.exists():
            shutil.copytree(state_src, state_dst)

    req = (ROOT / 'scenario' / f'stage-{args.stage}.md').read_text(encoding='utf-8')
    (ws / 'USER_REQUEST.md').write_text(req, encoding='utf-8')
    (ws / 'CURRENT_STAGE').write_text(str(args.stage) + '\n', encoding='utf-8')
    print(f'Revealed stage {args.stage} to {args.condition} workspace: {ws}')
    print('Later-stage requirement files were not copied.')


if __name__ == '__main__':
    main()
