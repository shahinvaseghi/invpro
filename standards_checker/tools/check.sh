#!/bin/bash

# Standards Checker - ابزار چک سریع
# استفاده روزانه برای توسعه‌دهندگان

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# تنظیمات
SHOW_WARNINGS=${SHOW_WARNINGS:-true}
MAX_ISSUES_DISPLAY=${MAX_ISSUES_DISPLAY:-10}
COLORED_OUTPUT=${COLORED_OUTPUT:-true}

# مسیر ابزار اصلی
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$CHECKER_DIR")"
CHECKER_SCRIPT="$CHECKER_DIR/check_standards.py"

# تابع نمایش header
show_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║              Standards Checker - Quick Check             ║${NC}"
    echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# تابع نمایش راهنما
show_help() {
    cat << EOF
استفاده:
    $0                  # چک فایل‌های staged در git
    $0 <module>         # چک یک ماژول خاص
    $0 all              # چک همه پروژه
    $0 --help           # نمایش این راهنما

مثال‌ها:
    $0                  # فایل‌های staged
    $0 inventory        # ماژول inventory
    $0 production       # ماژول production
    $0 all              # همه پروژه

گزینه‌های محیطی:
    SHOW_WARNINGS=false     # عدم نمایش warnings
    MAX_ISSUES_DISPLAY=5    # تعداد issues نمایش داده شود

مثال:
    SHOW_WARNINGS=false $0 inventory
EOF
}

# تابع چک فایل‌های staged
check_staged() {
    echo -e "${BLUE}🔍 Checking staged files...${NC}"
    echo ""
    
    cd "$PROJECT_DIR"
    
    # گرفتن لیست فایل‌های staged
    staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|html)$')
    
    if [ -z "$staged_files" ]; then
        echo -e "${YELLOW}⚠️  No Python or HTML files staged${NC}"
        echo ""
        echo "💡 Tip: Stage files first:"
        echo "   git add <file>"
        echo ""
        return 0
    fi
    
    # شمارش فایل‌ها
    file_count=$(echo "$staged_files" | wc -l)
    echo -e "${CYAN}Found ${BOLD}$file_count${NC}${CYAN} staged file(s)${NC}"
    echo ""
    
    # اجرای checker روی فایل‌های staged
    temp_report=$(mktemp)
    
    cd "$CHECKER_DIR"
    python check_standards.py --json "$temp_report" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        # پردازش نتایج
        process_results "$temp_report" "$file_count"
    else
        echo -e "${RED}❌ Error running checker${NC}"
        rm -f "$temp_report"
        return 1
    fi
    
    rm -f "$temp_report"
}

# تابع چک یک ماژول
check_module() {
    local module=$1
    
    echo -e "${BLUE}🔍 Checking module: ${BOLD}$module${NC}"
    echo ""
    
    cd "$CHECKER_DIR"
    
    # بررسی وجود ماژول
    if [ ! -d "$PROJECT_DIR/$module" ]; then
        echo -e "${RED}❌ Module '$module' not found${NC}"
        echo ""
        echo "Available modules:"
        ls -d "$PROJECT_DIR"/*/ | grep -v -E '(venv|env|__pycache__|\.git|static|media|locale)' | xargs -n 1 basename
        return 1
    fi
    
    # اجرای checker
    temp_report=$(mktemp)
    python check_standards.py --module "$module" --json "$temp_report" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        # شمارش فایل‌ها در ماژول
        file_count=$(find "$PROJECT_DIR/$module" -type f \( -name "*.py" -o -name "*.html" \) | wc -l)
        process_results "$temp_report" "$file_count"
    else
        echo -e "${RED}❌ Error running checker${NC}"
        rm -f "$temp_report"
        return 1
    fi
    
    rm -f "$temp_report"
}

# تابع چک همه پروژه
check_all() {
    echo -e "${BLUE}🔍 Checking entire project...${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  This may take a few minutes...${NC}"
    echo ""
    
    cd "$CHECKER_DIR"
    
    # اجرای checker
    temp_report=$(mktemp)
    python check_standards.py --json "$temp_report" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        # شمارش کل فایل‌ها
        file_count=$(find "$PROJECT_DIR" -type f \( -name "*.py" -o -name "*.html" \) | \
                     grep -v -E '(venv|env|__pycache__|\.git|static|media|locale)' | wc -l)
        process_results "$temp_report" "$file_count"
    else
        echo -e "${RED}❌ Error running checker${NC}"
        rm -f "$temp_report"
        return 1
    fi
    
    rm -f "$temp_report"
}

# تابع پردازش نتایج
process_results() {
    local report_file=$1
    local file_count=$2
    
    # خواندن summary
    local total_issues=$(jq -r '.summary.total_issues' "$report_file")
    local critical=$(jq -r '.summary.critical' "$report_file")
    local errors=$(jq -r '.summary.errors' "$report_file")
    local warnings=$(jq -r '.summary.warnings' "$report_file")
    
    # نمایش آمار
    echo -e "${BOLD}Files Checked:${NC} $file_count"
    echo ""
    
    echo -e "${BOLD}Summary:${NC}"
    echo -e "  Total Issues: $total_issues"
    
    if [ "$critical" -gt 0 ]; then
        echo -e "  ${RED}${BOLD}Critical: $critical${NC}"
    fi
    
    if [ "$errors" -gt 0 ]; then
        echo -e "  ${RED}Errors: $errors${NC}"
    fi
    
    if [ "$warnings" -gt 0 ] && [ "$SHOW_WARNINGS" = "true" ]; then
        echo -e "  ${YELLOW}Warnings: $warnings${NC}"
    fi
    
    echo ""
    
    # نمایش issues
    if [ "$total_issues" -gt 0 ]; then
        echo -e "${BOLD}Issues:${NC}"
        echo ""
        
        # نمایش critical و error issues
        local count=0
        jq -r '.issues[] | select(.severity == "critical" or .severity == "error") | 
               "\(.file):\(.line) [\(.severity | ascii_upcase)] \(.category)\n  \(.message)"' "$report_file" | \
        while IFS= read -r line; do
            if [ "$count" -lt "$MAX_ISSUES_DISPLAY" ]; then
                if [[ $line == *"CRITICAL"* ]]; then
                    echo -e "${RED}${BOLD}$line${NC}"
                elif [[ $line == *"ERROR"* ]]; then
                    echo -e "${RED}$line${NC}"
                else
                    echo -e "$line"
                fi
                ((count++))
            fi
        done
        
        # بررسی issues بیشتر
        local remaining=$((total_issues - MAX_ISSUES_DISPLAY))
        if [ "$remaining" -gt 0 ]; then
            echo ""
            echo -e "${CYAN}... and $remaining more issue(s)${NC}"
            echo ""
            echo -e "💡 For full report: ${BOLD}python check_standards.py --verbose${NC}"
        fi
        
        echo ""
        
        # نتیجه نهایی
        if [ "$critical" -gt 0 ] || [ "$errors" -gt 0 ]; then
            echo -e "${RED}${BOLD}╔════════════════════════════════════════╗${NC}"
            echo -e "${RED}${BOLD}║  ❌ FAILED - Fix errors before commit ║${NC}"
            echo -e "${RED}${BOLD}╚════════════════════════════════════════╝${NC}"
            echo ""
            return 1
        elif [ "$warnings" -gt 0 ]; then
            echo -e "${YELLOW}${BOLD}╔═══════════════════════════════════════════╗${NC}"
            echo -e "${YELLOW}${BOLD}║  ⚠️  WARNINGS - Consider fixing these    ║${NC}"
            echo -e "${YELLOW}${BOLD}╚═══════════════════════════════════════════╝${NC}"
            echo ""
            return 0
        fi
    else
        echo -e "${GREEN}${BOLD}╔════════════════════════════════════╗${NC}"
        echo -e "${GREEN}${BOLD}║  ✅ PASSED - All checks passed!   ║${NC}"
        echo -e "${GREEN}${BOLD}╚════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${GREEN}Ready to commit!${NC}"
        echo ""
        return 0
    fi
}

# تابع اصلی
main() {
    # بررسی وجود jq
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ Error: jq is not installed${NC}"
        echo ""
        echo "Install jq:"
        echo "  Ubuntu/Debian: sudo apt install jq"
        echo "  macOS: brew install jq"
        echo ""
        exit 1
    fi
    
    # بررسی وجود checker script
    if [ ! -f "$CHECKER_SCRIPT" ]; then
        echo -e "${RED}❌ Error: check_standards.py not found${NC}"
        echo "Expected at: $CHECKER_SCRIPT"
        exit 1
    fi
    
    show_header
    
    # پردازش آرگومان‌ها
    case "${1:-staged}" in
        --help|-h|help)
            show_help
            ;;
        all)
            check_all
            ;;
        staged|"")
            check_staged
            ;;
        *)
            check_module "$1"
            ;;
    esac
    
    exit $?
}

# اجرا
main "$@"

