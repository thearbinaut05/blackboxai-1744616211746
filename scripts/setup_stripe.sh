#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stripe Account Setup Script${NC}"
echo "--------------------------------"

# Check if stripe CLI is installed
if ! command -v stripe &> /dev/null; then
    echo -e "${RED}Stripe CLI not found. Installing...${NC}"
    
    # Check OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation
        curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg
        echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" | sudo tee -a /etc/apt/sources.list.d/stripe.list
        sudo apt update
        sudo apt install stripe
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # MacOS installation
        brew install stripe/stripe-cli/stripe
    else
        echo -e "${RED}Unsupported operating system${NC}"
        exit 1
    fi
fi

# Login to Stripe
echo -e "\n${YELLOW}Logging into Stripe...${NC}"
stripe login

# Get account info
echo -e "\n${YELLOW}Fetching account information...${NC}"
ACCOUNT_INFO=$(stripe get account)
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to fetch account information${NC}"
    exit 1
fi

# Extract account ID
ACCOUNT_ID=$(echo "$ACCOUNT_INFO" | grep -o '"id": "[^"]*' | cut -d'"' -f4)

# Get API keys
echo -e "\n${YELLOW}Fetching API keys...${NC}"
API_KEYS=$(stripe api-keys list)
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to fetch API keys${NC}"
    exit 1
fi

# Extract publishable and secret keys
PUBLISHABLE_KEY=$(echo "$API_KEYS" | grep -o 'pk_[a-zA-Z0-9_]*' | head -1)
SECRET_KEY=$(echo "$API_KEYS" | grep -o 'sk_[a-zA-Z0-9_]*' | head -1)

# Create .env file
echo -e "\n${YELLOW}Creating environment file...${NC}"
cat > .env << EOF
STRIPE_ACCOUNT_ID=$ACCOUNT_ID
STRIPE_PUBLISHABLE_KEY=$PUBLISHABLE_KEY
STRIPE_SECRET_KEY=$SECRET_KEY
STRIPE_API_VERSION=2023-10-16
EOF

# Set up webhook listener
echo -e "\n${YELLOW}Setting up webhook endpoint...${NC}"
WEBHOOK_OUTPUT=$(stripe listen --forward-to http://localhost:8000/webhook)
WEBHOOK_SECRET=$(echo "$WEBHOOK_OUTPUT" | grep -o 'whsec_[a-zA-Z0-9]*')

# Add webhook secret to .env
echo "STRIPE_WEBHOOK_SECRET=$WEBHOOK_SECRET" >> .env

# Update config
echo -e "\n${YELLOW}Updating configuration...${NC}"
python3 - << EOF
import os
from src.infrastructure.config_manager import ConfigManager

config = ConfigManager()
config.update_stripe_settings({
    'account_id': os.getenv('STRIPE_ACCOUNT_ID'),
    'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
    'secret_key': os.getenv('STRIPE_SECRET_KEY'),
    'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET'),
    'api_version': os.getenv('STRIPE_API_VERSION')
})
EOF

# Enable required capabilities
echo -e "\n${YELLOW}Enabling required capabilities...${NC}"
stripe capabilities update card_payments requested=true
stripe capabilities update transfers requested=true

# Verify setup
echo -e "\n${YELLOW}Verifying setup...${NC}"
if [ -f .env ] && [ -n "$ACCOUNT_ID" ] && [ -n "$PUBLISHABLE_KEY" ] && [ -n "$SECRET_KEY" ] && [ -n "$WEBHOOK_SECRET" ]; then
    echo -e "${GREEN}Setup completed successfully!${NC}"
    echo -e "Account ID: $ACCOUNT_ID"
    echo -e "Environment variables have been saved to .env"
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "1. Complete account verification if not done"
    echo "2. Add bank account for payouts"
    echo "3. Set up webhook endpoints in production"
else
    echo -e "${RED}Setup incomplete. Please check the error messages above.${NC}"
fi

# Instructions for webhook handling
echo -e "\n${YELLOW}Webhook Information:${NC}"
echo "To handle webhooks in production:"
echo "1. Set up your webhook endpoint at: https://your-domain.com/webhook"
echo "2. Add this endpoint in Stripe Dashboard"
echo "3. Update STRIPE_WEBHOOK_SECRET in production"

echo -e "\n${YELLOW}Testing Connection:${NC}"
echo "Run: stripe balance to verify your connection"
