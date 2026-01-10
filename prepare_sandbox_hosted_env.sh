#!/bin/bash
# Script to prepare .env file for sandbox testing on hosted server
# Run this on your HOSTED SERVER (not local)

ENV_FILE=".env"
BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Preparing Sandbox Testing .env File"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will modify your .env file!"
echo "    A backup will be created: $BACKUP_FILE"
echo ""
read -p "Enter your hosted domain (e.g., portal.maishaapp.co.tz): " HOSTED_DOMAIN
if [ -z "$HOSTED_DOMAIN" ]; then
    echo "❌ Error: Domain is required!"
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

# Step 2: Update BASE_URL
echo "[2/6] Updating BASE_URL..."
if grep -q "^BASE_URL=" "$ENV_FILE"; then
    sed -i "s|^BASE_URL=.*|BASE_URL=https://$HOSTED_DOMAIN|" "$ENV_FILE"
    echo "✅ BASE_URL updated to https://$HOSTED_DOMAIN"
else
    echo "BASE_URL=https://$HOSTED_DOMAIN" >> "$ENV_FILE"
    echo "✅ BASE_URL added"
fi

# Step 3: Set AZAM_PAY_SANDBOX to True
echo "[3/6] Setting AZAM_PAY_SANDBOX=True..."
if grep -q "^AZAM_PAY_SANDBOX=" "$ENV_FILE"; then
    sed -i 's/^AZAM_PAY_SANDBOX=.*/AZAM_PAY_SANDBOX=True/' "$ENV_FILE"
    echo "✅ AZAM_PAY_SANDBOX set to True (Sandbox mode)"
else
    echo "AZAM_PAY_SANDBOX=True" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_SANDBOX added"
fi

# Step 4: Update AZAM_PAY_BASE_URL to sandbox
echo "[4/6] Updating AZAM_PAY_BASE_URL to sandbox..."
if grep -q "^AZAM_PAY_BASE_URL=" "$ENV_FILE"; then
    sed -i 's|^AZAM_PAY_BASE_URL=.*|AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz|' "$ENV_FILE"
    echo "✅ AZAM_PAY_BASE_URL updated to sandbox"
else
    echo "AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_BASE_URL added"
fi

# Step 5: Update AZAM_PAY_WEBHOOK_URL
echo "[5/6] Updating AZAM_PAY_WEBHOOK_URL..."
WEBHOOK_URL="https://$HOSTED_DOMAIN/api/v1/payments/webhook/azam-pay/"
if grep -q "^AZAM_PAY_WEBHOOK_URL=" "$ENV_FILE"; then
    sed -i "s|^AZAM_PAY_WEBHOOK_URL=.*|AZAM_PAY_WEBHOOK_URL=$WEBHOOK_URL|" "$ENV_FILE"
    echo "✅ AZAM_PAY_WEBHOOK_URL updated"
else
    echo "AZAM_PAY_WEBHOOK_URL=$WEBHOOK_URL" >> "$ENV_FILE"
    echo "✅ AZAM_PAY_WEBHOOK_URL added"
fi

# Step 6: Update ALLOWED_HOSTS
echo "[6/6] Updating ALLOWED_HOSTS..."
if grep -q "^ALLOWED_HOSTS=" "$ENV_FILE"; then
    # Check if domain already in ALLOWED_HOSTS
    if ! grep -q "$HOSTED_DOMAIN" "$ENV_FILE"; then
        sed -i "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$HOSTED_DOMAIN,www.$HOSTED_DOMAIN|" "$ENV_FILE"
        echo "✅ ALLOWED_HOSTS updated"
    else
        echo "✅ ALLOWED_HOSTS already contains domain"
    fi
else
    echo "ALLOWED_HOSTS=$HOSTED_DOMAIN,www.$HOSTED_DOMAIN" >> "$ENV_FILE"
    echo "✅ ALLOWED_HOSTS added"
fi

echo ""
echo "=========================================="
echo "✅ Sandbox Testing .env file prepared!"
echo "=========================================="
echo ""
echo "Updated values:"
echo "  BASE_URL=https://$HOSTED_DOMAIN"
echo "  AZAM_PAY_SANDBOX=True"
echo "  AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz"
echo "  AZAM_PAY_WEBHOOK_URL=$WEBHOOK_URL"
echo "  ALLOWED_HOSTS=$HOSTED_DOMAIN,www.$HOSTED_DOMAIN"
echo ""
echo "⚠️  IMPORTANT: Next steps:"
echo "  1. Verify sandbox credentials are correct in .env"
echo "  2. Configure webhook URL in AzamPay SANDBOX dashboard:"
echo "     $WEBHOOK_URL"
echo "  3. Restart your Django/Gunicorn server"
echo "  4. Test payment flow"
echo ""
echo "To verify:"
echo "  grep -E '(AZAM_PAY_SANDBOX|AZAM_PAY_WEBHOOK_URL|BASE_URL)' .env"
echo ""
