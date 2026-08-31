#!/usr/bin/env python3
"""Return Routing Engine CLI.

Usage:
    python main.py                          # reads data/returns.jsonl, prints decisions
    python main.py --data-dir data          # explicit data directory
    python main.py --out results.jsonl      # also write decisions to a file
"""

import argparse
import sys

from returns.models import EngineData
from returns.parser import (
    parse_category_rules,
    parse_scoring_rules,
    parse_decision_bands,
    parse_account_profiles,
    parse_account_links,
    parse_return_requests,
    decision_to_json,
)
from returns.engine import Engine
from returns.file_io import write_lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Return Routing Engine")
    parser.add_argument("--data-dir", default="data", help="Directory containing the JSON/JSONL data files")
    parser.add_argument("--out", default=None, help="Optional path to also write decisions as JSONL")
    args = parser.parse_args()

    try:
        data = EngineData(
            category_rules=parse_category_rules(f"{args.data_dir}/category_rules.json"),
            scoring_rules=parse_scoring_rules(f"{args.data_dir}/scoring_rules.json"),
            decision_bands=parse_decision_bands(f"{args.data_dir}/decision_bands.json"),
            account_profiles=parse_account_profiles(f"{args.data_dir}/account_profiles.jsonl"),
            account_links=parse_account_links(f"{args.data_dir}/account_links.jsonl"),
        )
        requests = parse_return_requests(f"{args.data_dir}/returns.jsonl")

        engine = Engine(data)

        output_lines = []
        for request in requests:
            decision = engine.evaluate(request)
            line = decision_to_json(decision)
            print(line)
            output_lines.append(line)

        if args.out:
            write_lines(args.out, output_lines)

    except Exception as ex:  # noqa: BLE001 - top-level CLI error handler
        print(f"Error: {ex}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
