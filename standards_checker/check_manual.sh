#!/bin/bash
# اسکریپت ساده برای اجرای Interactive Checker
# استفاده: ./check_manual.sh

# رنگ‌ها
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Standards Checker - Manual Check        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# رفتن به پوشه standards_checker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# چک کردن Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# اجرا
echo -e "${YELLOW}🚀 Starting Interactive Checker...${NC}"
echo ""

python3 interactive_checker_v2.py

echo ""
echo -e "${GREEN}✓ Done!${NC}"

