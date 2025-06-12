#!/bin/bash
# Shell script to verify the API client implementation

API_CLIENT_PATH="/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client.py"

echo "=== CHECKING API CLIENT METHODS ==="
echo "API client path: $API_CLIENT_PATH"

# Check if file exists
if [ ! -f "$API_CLIENT_PATH" ]; then
  echo "❌ ERROR: API client file not found!"
  exit 1
fi

# Check file size
SIZE=$(stat --format="%s" "$API_CLIENT_PATH")
echo "File size: $SIZE bytes"

# Required methods
METHODS=(
  "get_sales_history"
  "get_orders"
  "get_categories"
  "get_expenses"
  "get_stats"
  "create_sale"
)

MISSING=0
FOUND=0

# Check each method
echo -e "\nChecking for required methods:"
for METHOD in "${METHODS[@]}"; do
  if grep -q "def $METHOD" "$API_CLIENT_PATH"; then
    echo "✅ $METHOD - FOUND"
    FOUND=$((FOUND + 1))
  else
    echo "❌ $METHOD - NOT FOUND"
    MISSING=$((MISSING + 1))
  fi
done

# Summary
echo -e "\n=== SUMMARY ==="
echo "Total methods checked: ${#METHODS[@]}"
echo "Methods found: $FOUND"
echo "Methods missing: $MISSING"

if [ $MISSING -eq 0 ]; then
  echo -e "\n✅ SUCCESS: All required methods are implemented!"
  exit 0
else
  echo -e "\n❌ ERROR: Some methods are missing from the API client!"
  exit 1
fi
