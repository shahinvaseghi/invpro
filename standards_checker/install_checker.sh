#!/bin/bash

# Installation script for Standards Checker
# این اسکریپت ابزار Standards Checker را نصب و راه‌اندازی می‌کند

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}       Standards Checker Installation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# بررسی وجود Python
echo "🔍 Checking Python..."
if ! command -v python &> /dev/null
then
    echo -e "${RED}❌ Python not found!${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# بررسی وجود Git
echo "🔍 Checking Git..."
if ! command -v git &> /dev/null
then
    echo -e "${RED}❌ Git not found!${NC}"
    echo "Please install Git"
    exit 1
fi

GIT_VERSION=$(git --version | awk '{print $3}')
echo -e "${GREEN}✅ Git $GIT_VERSION found${NC}"
echo ""

# دادن permission اجرا به اسکریپت‌ها
echo "🔧 Setting permissions..."
chmod +x check_standards.py
chmod +x pre-commit.sh
echo -e "${GREEN}✅ Permissions set${NC}"
echo ""

# نصب Pre-commit Hook
echo "🪝 Installing pre-commit hook..."
if [ -d .git ]; then
    if [ -f .git/hooks/pre-commit ]; then
        echo -e "${YELLOW}⚠️  Pre-commit hook already exists${NC}"
        read -p "Replace it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            cp pre-commit.sh .git/hooks/pre-commit
            chmod +x .git/hooks/pre-commit
            echo -e "${GREEN}✅ Pre-commit hook installed${NC}"
        else
            echo -e "${YELLOW}⏭️  Skipped${NC}"
        fi
    else
        cp pre-commit.sh .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo -e "${GREEN}✅ Pre-commit hook installed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Not a git repository - skipping hook installation${NC}"
fi
echo ""

# ایجاد دایرکتوری برای گزارش‌ها
echo "📁 Creating reports directory..."
mkdir -p reports
echo -e "${GREEN}✅ Reports directory created${NC}"
echo ""

# تست اجرا
echo "🧪 Testing checker..."
python check_standards.py --module shared > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Checker is working${NC}"
else
    echo -e "${YELLOW}⚠️  Checker test returned warnings (this is normal)${NC}"
fi
echo ""

# نمایش دستورات مفید
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📚 Usage examples:"
echo ""
echo "  # Check all files:"
echo "  python check_standards.py"
echo ""
echo "  # Check specific module:"
echo "  python check_standards.py --module inventory"
echo ""
echo "  # Verbose output:"
echo "  python check_standards.py --verbose"
echo ""
echo "  # Export JSON report:"
echo "  python check_standards.py --json report.json"
echo ""
echo "📖 For more information, see STANDARDS_CHECKER_README.md"
echo ""

# پیام نهایی
echo -e "${YELLOW}💡 Tip: The pre-commit hook will run automatically before each commit${NC}"
echo -e "${YELLOW}   To bypass (not recommended): git commit --no-verify${NC}"
echo ""

