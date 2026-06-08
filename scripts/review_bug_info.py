#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    add_llm_args,
    extract_json_object,
    load_json_or_jsonl,
    openai_compatible_chat,
    read_text,
    render_prompt,
    require_api_key,
    sha256_text,
    stable_case_id,
    validate_case,
    write_jsonl,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review generated RTL bug_info annotations.")
    parser.add_argument("cases", help="case JSON or JSONL")
    parser.add_argument("generated", help="generated annotation JSONL")
    parser.add_argument("output", help="review output JSONL")
    parser.add_argument("--prompt", default=str(Path(__file__).resolve().parents[1] / "prompts" / "review_bug_info.txt"))
    add_llm_args(parser)
    args = parser.parse_args()

    api_key = require_api_key(args.api_key)
    prompt_template = read_text(args.prompt)
    prompt_hash = sha256_text(prompt_template)
    cases = load_json_or_jsonl(args.cases)
    generated = {str(item.get("id")): item for item in load_json_or_jsonl(args.generated)}
    records = []

    for index, case in enumerate(cases):
        case_id = stable_case_id(case, index)
        errors = validate_case(case)
        generated_record = generated.get(case_id)
        if errors:
            records.append({"id": case_id, "error": "invalid_case", "details": errors})
            continue
        if not generated_record or "annotation" not in generated_record:
            records.append({"id": case_id, "error": "missing_generated_annotation"})
            continue

        case_json = json.dumps(case, ensure_ascii=False, sort_keys=True, indent=2)
        generated_json = json.dumps(generated_record["annotation"], ensure_ascii=False, sort_keys=True, indent=2)
        prompt = render_prompt(prompt_template, {"CASE_JSON": case_json, "GENERATED_JSON": generated_json})
        raw = openai_compatible_chat(
            base_url=args.base_url,
            api_key=api_key,
            model=args.model,
            prompt=prompt,
            temperature=args.temperature,
            top_p=args.top_p,
            seed=args.seed,
            timeout=args.timeout,
            max_retries=args.max_retries,
        )
        try:
            review = extract_json_object(raw)
            record = {"id": case_id, "review": review}
        except Exception as exc:
            record = {"id": case_id, "error": "invalid_model_output", "details": str(exc), "raw_output": raw}

        record["metadata"] = {
            "model": args.model,
            "base_url": args.base_url,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "seed": args.seed,
            "prompt_path": args.prompt,
            "prompt_sha256": prompt_hash,
        }
        records.append(record)

    write_jsonl(args.output, records)
    print(f"Wrote {len(records)} record(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
