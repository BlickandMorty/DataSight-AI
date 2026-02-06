#!/bin/bash
# just run this to create your .env file (or use: make setup-env)
# it does 3 things:
# 1) stop if .env already exists
# 2) ask you for your GEMINI_API_KEY
# 3) write .env for you

set -e  # stop if any command fails

if [ -f .env ]; then
  echo ".env already exists. leaving it alone."
  exit 0
fi

read -p "Enter your Gemini API Key (leave blank to skip): " GEMINI_API_KEY

cat <<EOF > .env
GEMINI_API_KEY="$GEMINI_API_KEY"
EOF

echo ".env created. edit it later if you want to add more."
