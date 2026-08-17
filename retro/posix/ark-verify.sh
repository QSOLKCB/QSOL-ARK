#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
ROOT=$(CDPATH= cd "$SCRIPT_DIR/../.." && pwd)
FILE=${1:-"$ROOT/capsules/minimal/ARK-CANARY.txt"}
RECEIPT=${2:-"$ROOT/capsules/minimal/SHA256SUMS"}
NAME=$(basename "$FILE")
EXPECTED=$(awk -v name="$NAME" '$2 == name { print $1; exit }' "$RECEIPT")

if [ -z "$EXPECTED" ]; then
    echo "ARK_RECEIPT_MISSING file=$NAME" >&2
    exit 2
fi

if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL=$(sha256sum "$FILE" | awk '{print $1}')
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL=$(shasum -a 256 "$FILE" | awk '{print $1}')
elif command -v openssl >/dev/null 2>&1; then
    ACTUAL=$(openssl dgst -sha256 "$FILE" | sed 's/^.*= //')
else
    echo "ARK_HASH_PROVIDER_MISSING need=sha256sum|shasum|openssl" >&2
    exit 2
fi

if [ "$ACTUAL" != "$EXPECTED" ]; then
    echo "ARK_HASH_MISMATCH expected=$EXPECTED actual=$ACTUAL" >&2
    exit 1
fi

printf '%s\n' "ARK_HASH_OK tier=T1 file=$NAME sha256=$ACTUAL"
