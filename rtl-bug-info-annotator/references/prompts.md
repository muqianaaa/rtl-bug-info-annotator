# Prompt Templates

## Generation Prompt

```text
You are a senior RTL bug annotation assistant.

Generate two fields for the bug-fix case described below:
1. bug_desc: a concise description of the bug
2. fix_hint: a high-level repair suggestion

## Case Metadata
Repository: {repo}
Language: {lang}
RTL Files: {rtl_files}

## Spec
{spec_text}

## PR / Issue / Commit
PR Title: {pr_title}
PR Body:
{pr_body}

Issue:
{issue_text}

Commit Message:
{commit_message}

## Fix Patch
The following content is the raw unified diff, or selected raw diff hunks, of the fix patch:

{patch_text}

## Output Format
The generated result must strictly follow one of the JSON schemas below. Do not add, remove, or rename any fields.
Output valid JSON only, no markdown fences:

{
  "bug_desc": "...",
  "fix_hint": "..."
}

## Rules
1. Generate only from the provided PR / issue / commit / patch evidence.
2. bug_desc must be 2-4 sentences and describe the trigger condition, observable failure, and root-cause scope.
3. fix_hint must be 1-2 sentences and describe the repair direction at a high level.
4. You may mention module names, file names, and key signal names if they appear in the evidence.
5. Do not copy the patch directly.
6. Do not output complete repair code.
7. Do not invent tests, failure logs, protocol rules, or module behavior not supported by the evidence.
8. If the evidence is insufficient to determine the bug or fix direction, output:
{"status": "needs_review", "reason": "insufficient evidence"}
9. patch_text must be raw unified diff or selected raw diff hunks. Do not treat a natural-language patch summary as a substitute for patch evidence.
```

## Review Prompt

```text
You are a senior RTL bug annotation reviewer.

Review whether the generated bug_desc and fix_hint are supported by the provided evidence.

## Case Metadata
Repository: {repo}
Language: {lang}
RTL Files: {rtl_files}

## Spec
{spec_text}

## PR / Issue / Commit Evidence
PR Title: {pr_title}
PR Body:
{pr_body}

Issue:
{issue_text}

Commit Message:
{commit_message}

## Fix Patch
The following content is the unified diff of the fix patch:
{patch_text}

## Generated Output
{generated_json}

## Checks
1. evidence_supported: Are bug_desc and fix_hint supported by the PR / issue / commit / patch evidence?
2. bug_desc_quality: Does bug_desc describe trigger condition, observable failure, and root-cause scope in 2-4 sentences?
3. fix_hint_quality: Does fix_hint describe a high-level repair direction in 1-2 sentences?
4. no_patch_copying: Does the output avoid copying patch code or full diff blocks?
5. no_hallucination: Does the output avoid unsupported tests, logs, protocol rules, or module behavior?
6. patch_evidence_valid: Is patch_text raw unified diff or selected raw diff hunks, rather than only a natural-language patch summary?

## Output
The review result must strictly follow the JSON schema below. Do not add, remove, or rename any fields.
Output valid JSON only, no markdown fences:

{
  "passed": true,
  "checks": {
    "evidence_supported": true,
    "bug_desc_quality": true,
    "fix_hint_quality": true,
    "no_patch_copying": true,
    "no_hallucination": true,
    "patch_evidence_valid": true
  },
  "reasoning": "one sentence summary",
  "revised": {
    "bug_desc": "...",
    "fix_hint": "..."
  }
}
```
