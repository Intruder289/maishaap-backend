#!/bin/bash
# Script to prepare local .env file for production deployment
# Run this on your LOCAL machine before uploading to production

ENV_FILE=".env"
BACKUP_FILE=".env.local.backup.$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Preparing Production .env File"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will modify your local .env file!"
echo "    A backup will be created: $BACKUP_FILE"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Step 1: Backup current .env file
if [ -f "$ENV_FILE" ]; then
    echo "[1/6] Backing up current .env file..."
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo "✅ Backup created: $BACKUP_FILE"
else
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Step 2: Update DEBUG to False
echo "[2/6] Setting DEBUG=False..."
if grep -q "^DEBUG=" "$ENV_FILE"; then
    sed -i 's/^DEBUG=.*/DEBUG=False/' "$ENV_FILE"
    echo "✅ DEBUG set to False"
else
    echo "DEBUG=False" >> "$ENV_FILE"
    echo "✅ DEBUG added"
fi

# Step 3: Update BASE_URL
echo "[3/6] Updating BASE_URL..."
if grep -q "^BASE_URL=" "$ENV_FILE"; then
    sed -i 's|^BASE_URL=.*|BASE_URL=https://portal.maishaapp.co.tz|' "$ENV_FILE"
    echo "✅ BASE_URL updated"
else
    echo "BASE_URL=https://portal.maishaapp.co.tz" >> "$ENV_FILE"
    echo "✅ BASE_URL added"
fi

# Step 4: Update AZAM_PAY_SANDBOX
echo "[4/6] Setting AZAM_PAY_SANDBOX=False..."
if grep -q "^AZAM_PAY_SANDBOX=" "$ENV_FILE"; then
    sed -i 's/^AZAM_PAY_SANDBOX=.*/AZAM_PAY_SANDBOX=False/' "$ENV_FILE"
    echo "✅ AZAM_PAY_SANDBOX set to False"
else
    echo "AZAM_PAY_SANDBOX=False" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_SANDBOX added"
fi

# Step 5: Update AZAM_PAY_WEBHOOK_URL
echo "[5/6] Updating AZAM_PAY_WEBHOOK_URL..."
if grep -q "^AZAM_PAY_WEBHOOK_URL=" "$ENV_FILE"; then
    sed -i 's|^AZAM_PAY_WEBHOOK_URL=.*|AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/|' "$ENV_FILE"
    echo "✅ AZAM_PAY_WEBHOOK_URL updated"
else
    echo "AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_WEBHOOK_URL added"
fi

# Step 6: Update AZAM_PAY_BASE_URL
echo "[6/6] Updating AZAM_PAY_BASE_URL..."
if grep -q "^AZAM_PAY_BASE_URL=" "$ENV_FILE"; then
    sed -i 's|^AZAM_PAY_BASE_URL=.*|AZAM_PAY_BASE_URL=https://api.azampay.co.tz|' "$ENV_FILE"
    echo "✅ AZAM_PAY_BASE_URL updated"
else
    echo "AZAM_PAY_BASE_URL=https://api.azampay.co.tz" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_BASE_URL added"
fi

echo ""
echo "=========================================="
echo "✅ Production .env file prepared!"
echo "=========================================="
echo ""
echo "Updated values:"
echo "  DEBUG=False"
echo "  BASE_URL=https://portal.maishaapp.co.tz"
echo "  AZAM_PAY_SANDBOX=False"
echo "  AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/"
echo "  AZAM_PAY_BASE_URL=https://api.azampay.co.tz"
echo ""
echo "⚠️  IMPORTANT: You still need to manually update:"
echo "  - DATABASE_PASSWORD (production database password)"
echo "  - SECRET_KEY (production secret key)"
echo "  - AZAM_PAY_CLIENT_ID (production client ID)"
echo "  - AZAM_PAY_CLIENT_SECRET (production client secret)"
echo "  - AZAM_PAY_API_KEY (production API key)"
echo "  - ALLOWED_HOSTS (if not already set)"
echo ""
echo "Next steps:"
echo "  1. Review: cat .env | grep -E '(DEBUG|BASE_URL|AZAM_PAY)'"
echo "  2. Update production credentials manually"
echo "  3. Upload entire project to production server"
echo "  4. Verify .env on production server"
echo "  5. Restart production server"
echo ""
