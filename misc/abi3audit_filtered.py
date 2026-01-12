#!/usr/bin/env python3
"""
Filtered abi3audit - allows known buffer protocol violations.

These functions are de facto stable but weren't officially added to
the Limited API until Python 3.11. We target 3.8+ anyway.

Usage:
    python misc/abi3audit_filtered.py wheel.whl

This script runs abi3audit and filters out expected violations for
buffer protocol functions. These functions have been stable in CPython
since Python 3.0 but were only officially added to the Limited API in 3.11.

For fully compliant abi3-3.11+ wheels, use `abi3audit --strict` directly.
"""
import sys
import json
import subprocess

# Buffer protocol functions that are de facto stable but weren't officially
# in Limited API at the version we target (3.8). These are stable since Python 3.0
# but were only added to Limited API in Python 3.11.
ALLOWED_SYMBOLS = {
    'PyObject_GetBuffer',
    'PyBuffer_Release',
    'PyBuffer_FillInfo',
    'PyBuffer_IsContiguous',
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python abi3audit_filtered.py <wheel.whl>")
        return 1

    wheel = sys.argv[1]

    # Run abi3audit with JSON output
    # Try uvx first (for environments where abi3audit isn't installed)
    try:
        result = subprocess.run(
            ['uvx', 'abi3audit', '--report', wheel],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        # Fall back to direct abi3audit
        result = subprocess.run(
            ['abi3audit', '--report', wheel],
            capture_output=True, text=True
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse abi3audit output:")
        print(result.stdout)
        print(result.stderr)
        return 1

    unexpected = []
    allowed_found = []

    for spec, info in data.get('specs', {}).items():
        for so in info.get('wheel', []):
            result_data = so.get('result', {})
            for sym in result_data.get('non_abi3_symbols', []):
                if sym in ALLOWED_SYMBOLS:
                    allowed_found.append(f"{so['name']}: {sym}")
                else:
                    unexpected.append(f"{so['name']}: {sym}")

    if allowed_found:
        print(f"Allowed buffer protocol symbols ({len(allowed_found)}):")
        for v in allowed_found[:10]:  # Show first 10
            print(f"  - {v}")
        if len(allowed_found) > 10:
            print(f"  ... and {len(allowed_found) - 10} more")

    if unexpected:
        print(f"\nERROR: Unexpected abi3 violations ({len(unexpected)}):")
        for v in unexpected:
            print(f"  - {v}")
        return 1

    print("\nabi3audit: OK (only expected buffer protocol symbols)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
