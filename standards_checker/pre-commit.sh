#!/bin/bash

# Pre-commit Hook - Standards Checker
# این اسکریپت قبل از هر commit اجرا می‌شود و استانداردها را چک می‌کند

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "🔍 Running standards checker..."
echo ""

# اجرای standards checker
python check_standards.py

# ذخیره exit code
EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Standards check FAILED!${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}لطفاً قبل از commit مشکلات را رفع کنید.${NC}"
    echo ""
    echo "💡 برای مشاهده جزئیات:"
    echo "   python check_standards.py --verbose"
    echo ""
    echo "💡 برای bypass کردن این چک (توصیه نمی‌شود):"
    echo "   git commit --no-verify"
    echo ""
    exit 1
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Standards check PASSED!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

exit 0

