#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
ROOT=$(CDPATH= cd "$SCRIPT_DIR/../.." && pwd)
FILE=${1:-"$ROOT/capsules/minimal/ARK-CANARY.txt"}
RECEIPT=${2:-"$ROOT/capsules/minimal/SHA256SUMS"}
NAME=$(basename "$FILE")

if [ ! -r "$FILE" ]; then
    echo "ARK_INPUT_UNAVAILABLE file=$FILE" >&2
    exit 2
fi

if [ ! -r "$RECEIPT" ]; then
    echo "ARK_RECEIPT_UNAVAILABLE file=$RECEIPT" >&2
    exit 2
fi

EXPECTED=$(awk -v name="$NAME" '$2 == name { print $1; exit }' "$RECEIPT")
if [ -z "$EXPECTED" ]; then
    echo "ARK_RECEIPT_MISSING file=$NAME" >&2
    exit 2
fi

if command -v sha256sum >/dev/null 2>&1; then
    if ! OUTPUT=$(sha256sum "$FILE"); then
        echo "ARK_HASH_PROVIDER_FAILED provider=sha256sum file=$FILE" >&2
        exit 2
    fi
    ACTUAL=${OUTPUT%% *}
elif command -v shasum >/dev/null 2>&1; then
    if ! OUTPUT=$(shasum -a 256 "$FILE"); then
        echo "ARK_HASH_PROVIDER_FAILED provider=shasum file=$FILE" >&2
        exit 2
    fi
    ACTUAL=${OUTPUT%% *}
elif command -v openssl >/dev/null 2>&1; then
    if ! OUTPUT=$(openssl dgst -sha256 "$FILE"); then
        echo "ARK_HASH_PROVIDER_FAILED provider=openssl file=$FILE" >&2
        exit 2
    fi
    ACTUAL=${OUTPUT##*= }
else
    echo "ARK_HASH_PROVIDER_MISSING need=sha256sum|shasum|openssl" >&2
    exit 2
fi

if [ -z "$ACTUAL" ]; then
    echo "ARK_HASH_PROVIDER_INVALID_OUTPUT file=$FILE" >&2
    exit 2
fi

if [ "$ACTUAL" != "$EXPECTED" ]; then
    echo "ARK_HASH_MISMATCH expected=$EXPECTED actual=$ACTUAL" >&2
    exit 1
fi

printf '%s\n' "ARK_HASH_OK tier=T1 file=$NAME sha256=$ACTUAL"
