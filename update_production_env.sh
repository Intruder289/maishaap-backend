#!/bin/bash
# Script to update production .env file with AzamPay webhook URL
# Run this on your production server

ENV_FILE=".env"
BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Updating Production .env File"
echo "=========================================="

# Step 1: Backup current .env file
if [ -f "$ENV_FILE" ]; then
    echo "[1/4] Backing up current .env file..."
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo "✅ Backup created: $BACKUP_FILE"
else
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Step 2: Update BASE_URL if needed
echo "[2/4] Updating BASE_URL..."
if grep -q "^BASE_URL=" "$ENV_FILE"; then
    sed -i 's|^BASE_URL=.*|BASE_URL=https://portal.maishaapp.co.tz|' "$ENV_FILE"
    echo "✅ BASE_URL updated"
else
    echo "BASE_URL=https://portal.maishaapp.co.tz" >> "$ENV_FILE"
    echo "✅ BASE_URL added"
fi

# Step 3: Update AZAM_PAY_WEBHOOK_URL
echo "[3/4] Updating AZAM_PAY_WEBHOOK_URL..."
if grep -q "^AZAM_PAY_WEBHOOK_URL=" "$ENV_FILE"; then
    sed -i 's|^AZAM_PAY_WEBHOOK_URL=.*|AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/|' "$ENV_FILE"
    echo "✅ AZAM_PAY_WEBHOOK_URL updated"
else
    echo "AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_WEBHOOK_URL added"
fi

# Step 4: Ensure AZAM_PAY_SANDBOX is False for production
echo "[4/4] Ensuring AZAM_PAY_SANDBOX=False..."
if grep -q "^AZAM_PAY_SANDBOX=" "$ENV_FILE"; then
    sed -i 's|^AZAM_PAY_SANDBOX=.*|AZAM_PAY_SANDBOX=False|' "$ENV_FILE"
    echo "✅ AZAM_PAY_SANDBOX set to False"
else
    echo "AZAM_PAY_SANDBOX=False" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_SANDBOX added"
fi

echo ""
echo "=========================================="
echo "✅ .env file updated successfully!"
echo "=========================================="
echo ""
echo "Updated values:"
echo "  BASE_URL=https://portal.maishaapp.co.tz"
echo "  AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/"
echo "  AZAM_PAY_SANDBOX=False"
echo ""
echo "Next steps:"
echo "  1. Review the updated .env file: cat .env | grep -E '(BASE_URL|AZAM_PAY)'"
echo "  2. Restart your Django/Gunicorn server"
echo "  3. Test the webhook endpoint"
echo ""
