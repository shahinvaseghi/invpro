#!/bin/bash

# Standards Checker - گزارش هفتگی
# تولید و مقایسه گزارش‌های هفتگی

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# تنظیمات
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$CHECKER_DIR")"
REPORTS_DIR="$CHECKER_DIR/reports"
CHECKER_SCRIPT="$CHECKER_DIR/check_standards.py"
COMPARE_SCRIPT="$SCRIPT_DIR/compare_reports.py"

# تنظیمات گزارش
REPORT_FORMAT="report_%Y%m%d.json"
AUTO_COMPARE=${AUTO_COMPARE:-true}

# تابع نمایش header
show_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║           Standards Checker - Weekly Report              ║${NC}"
    echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# تابع نمایش راهنما
show_help() {
    cat << EOF
استفاده:
    $0                  # تولید گزارش جدید
    $0 list             # لیست گزارش‌های موجود
    $0 compare          # مقایسه با گزارش قبلی
    $0 latest           # نمایش آخرین گزارش
    $0 --help           # نمایش این راهنما

مثال‌ها:
    $0                  # تولید گزارش امروز
    $0 list             # مشاهده تاریخچه
    $0 compare          # مقایسه با هفته قبل

گزینه‌های محیطی:
    AUTO_COMPARE=false      # عدم مقایسه خودکار

مثال:
    AUTO_COMPARE=false $0
EOF
}

# تابع تولید گزارش جدید
generate_report() {
    local report_name=$(date +"$REPORT_FORMAT")
    local report_path="$REPORTS_DIR/$report_name"
    
    echo -e "${BLUE}📊 Generating weekly report...${NC}"
    echo -e "Date: ${BOLD}$(date +%Y-%m-%d)${NC}"
    echo ""
    
    # ایجاد دایرکتوری reports اگر وجود ندارد
    mkdir -p "$REPORTS_DIR"
    
    # اجرای checker
    cd "$CHECKER_DIR"
    
    echo -e "${CYAN}Running full project scan...${NC}"
    echo -e "${YELLOW}This may take a few minutes...${NC}"
    echo ""
    
    python check_standards.py --json "$report_path" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Report generated successfully${NC}"
        echo -e "Saved to: ${BOLD}$report_path${NC}"
        echo ""
        
        # نمایش خلاصه
        show_summary "$report_path"
        
        # مقایسه خودکار
        if [ "$AUTO_COMPARE" = "true" ]; then
            echo ""
            local prev_report=$(find_previous_report "$report_name")
            if [ -n "$prev_report" ]; then
                echo -e "${CYAN}Comparing with previous report...${NC}"
                echo ""
                compare_reports "$prev_report" "$report_path"
            fi
        fi
    else
        echo -e "${RED}❌ Error generating report${NC}"
        return 1
    fi
}

# تابع نمایش خلاصه یک گزارش
show_summary() {
    local report_path=$1
    
    if [ ! -f "$report_path" ]; then
        echo -e "${RED}❌ Report not found: $report_path${NC}"
        return 1
    fi
    
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                  Summary${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo ""
    
    # خواندن summary
    local total=$(jq -r '.summary.total_issues' "$report_path")
    local critical=$(jq -r '.summary.critical' "$report_path")
    local errors=$(jq -r '.summary.errors' "$report_path")
    local warnings=$(jq -r '.summary.warnings' "$report_path")
    local info=$(jq -r '.summary.info' "$report_path")
    
    echo -e "  Total Issues:     ${BOLD}$total${NC}"
    
    if [ "$critical" -gt 0 ]; then
        echo -e "  ${RED}${BOLD}Critical:         $critical${NC}"
    else
        echo -e "  Critical:         0"
    fi
    
    if [ "$errors" -gt 0 ]; then
        echo -e "  ${RED}Errors:           $errors${NC}"
    else
        echo -e "  Errors:           0"
    fi
    
    if [ "$warnings" -gt 0 ]; then
        echo -e "  ${YELLOW}Warnings:         $warnings${NC}"
    else
        echo -e "  Warnings:         0"
    fi
    
    echo -e "  Info:             $info"
    echo ""
    
    # Top categories
    echo -e "${BOLD}Top Categories:${NC}"
    jq -r '.issues | group_by(.category) | 
           map({category: .[0].category, count: length}) | 
           sort_by(.count) | reverse | .[:5] | 
           .[] | "  \(.count) - \(.category)"' "$report_path"
    
    echo ""
}

# تابع یافتن گزارش قبلی
find_previous_report() {
    local current_report=$1
    
    # لیست گزارش‌ها به ترتیب تاریخ
    local reports=($(ls -1 "$REPORTS_DIR"/report_*.json 2>/dev/null | sort -r))
    
    # پیدا کردن گزارش قبل از current
    local found=false
    for report in "${reports[@]}"; do
        local basename=$(basename "$report")
        if [ "$found" = true ]; then
            echo "$report"
            return 0
        fi
        if [ "$basename" = "$current_report" ]; then
            found=true
        fi
    done
    
    return 1
}

# تابع مقایسه دو گزارش
compare_reports() {
    local old_report=$1
    local new_report=$2
    
    if [ ! -f "$old_report" ] || [ ! -f "$new_report" ]; then
        echo -e "${RED}❌ Report files not found${NC}"
        return 1
    fi
    
    local old_date=$(basename "$old_report" | sed 's/report_\(.*\).json/\1/')
    local new_date=$(basename "$new_report" | sed 's/report_\(.*\).json/\1/')
    
    # خواندن summaries
    local old_total=$(jq -r '.summary.total_issues' "$old_report")
    local new_total=$(jq -r '.summary.total_issues' "$new_report")
    
    local old_critical=$(jq -r '.summary.critical' "$old_report")
    local new_critical=$(jq -r '.summary.critical' "$new_report")
    
    local old_errors=$(jq -r '.summary.errors' "$old_report")
    local new_errors=$(jq -r '.summary.errors' "$new_report")
    
    local old_warnings=$(jq -r '.summary.warnings' "$old_report")
    local new_warnings=$(jq -r '.summary.warnings' "$new_report")
    
    # محاسبه تغییرات
    local diff_total=$((new_total - old_total))
    local diff_critical=$((new_critical - old_critical))
    local diff_errors=$((new_errors - old_errors))
    local diff_warnings=$((new_warnings - old_warnings))
    
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo -e "${BOLD}           Comparison with Previous Week${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "Previous: $old_date"
    echo -e "Current:  $new_date"
    echo ""
    
    # نمایش تغییرات
    echo -e "${BOLD}Changes:${NC}"
    echo ""
    
    print_change "Total Issues" "$old_total" "$new_total" "$diff_total"
    print_change "Critical" "$old_critical" "$new_critical" "$diff_critical"
    print_change "Errors" "$old_errors" "$new_errors" "$diff_errors"
    print_change "Warnings" "$old_warnings" "$new_warnings" "$diff_warnings"
    
    echo ""
    
    # نتیجه کلی
    if [ "$diff_total" -lt 0 ]; then
        local improvement=$((diff_total * -1))
        echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}${BOLD}║  📈 Improving! -$improvement issues             ║${NC}"
        echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════╝${NC}"
    elif [ "$diff_total" -gt 0 ]; then
        echo -e "${RED}${BOLD}╔═══════════════════════════════════════════════╗${NC}"
        echo -e "${RED}${BOLD}║  📉 Regression! +$diff_total issues              ║${NC}"
        echo -e "${RED}${BOLD}╚═══════════════════════════════════════════════╝${NC}"
    else
        echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}${BOLD}║  ➡️  No change in total issues               ║${NC}"
        echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════╝${NC}"
    fi
    
    echo ""
}

# تابع نمایش تغییر
print_change() {
    local label=$1
    local old_val=$2
    local new_val=$3
    local diff=$4
    
    local arrow=""
    local color=""
    
    if [ "$diff" -lt 0 ]; then
        arrow="↓"
        color="${GREEN}"
    elif [ "$diff" -gt 0 ]; then
        arrow="↑"
        color="${RED}"
    else
        arrow="="
        color="${CYAN}"
    fi
    
    printf "  %-15s: %3d → %3d   " "$label" "$old_val" "$new_val"
    echo -e "${color}${BOLD}$arrow $diff${NC}"
}

# تابع لیست گزارش‌ها
list_reports() {
    echo -e "${BLUE}📋 Available Reports:${NC}"
    echo ""
    
    if [ ! -d "$REPORTS_DIR" ] || [ -z "$(ls -A "$REPORTS_DIR"/report_*.json 2>/dev/null)" ]; then
        echo -e "${YELLOW}No reports found${NC}"
        echo ""
        echo "Generate your first report:"
        echo "  $0"
        echo ""
        return 0
    fi
    
    local reports=($(ls -1t "$REPORTS_DIR"/report_*.json))
    local count=1
    
    for report in "${reports[@]}"; do
        local basename=$(basename "$report")
        local date_str=$(echo "$basename" | sed 's/report_\(.*\).json/\1/')
        local formatted_date=$(date -d "$date_str" "+%Y-%m-%d (%A)" 2>/dev/null || echo "$date_str")
        local total=$(jq -r '.summary.total_issues' "$report")
        
        printf "%2d. %s - %s issues\n" "$count" "$formatted_date" "$total"
        ((count++))
    done
    
    echo ""
    echo -e "Total reports: ${BOLD}$((count - 1))${NC}"
    echo ""
}

# تابع نمایش آخرین گزارش
show_latest() {
    local latest=$(ls -1t "$REPORTS_DIR"/report_*.json 2>/dev/null | head -1)
    
    if [ -z "$latest" ]; then
        echo -e "${YELLOW}No reports found${NC}"
        echo ""
        echo "Generate your first report:"
        echo "  $0"
        echo ""
        return 0
    fi
    
    local date_str=$(basename "$latest" | sed 's/report_\(.*\).json/\1/')
    
    echo -e "${BLUE}📊 Latest Report${NC}"
    echo -e "Date: ${BOLD}$(date -d "$date_str" "+%Y-%m-%d" 2>/dev/null || echo "$date_str")${NC}"
    echo ""
    
    show_summary "$latest"
}

# تابع مقایسه با قبلی
compare_with_previous() {
    local latest=$(ls -1t "$REPORTS_DIR"/report_*.json 2>/dev/null | head -1)
    
    if [ -z "$latest" ]; then
        echo -e "${YELLOW}No reports found${NC}"
        return 0
    fi
    
    local previous=$(find_previous_report "$(basename "$latest")")
    
    if [ -z "$previous" ]; then
        echo -e "${YELLOW}No previous report found for comparison${NC}"
        echo ""
        echo "Current report: $(basename "$latest")"
        echo ""
        return 0
    fi
    
    compare_reports "$previous" "$latest"
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
    case "${1:-generate}" in
        --help|-h|help)
            show_help
            ;;
        list|ls)
            list_reports
            ;;
        compare|cmp)
            compare_with_previous
            ;;
        latest|last)
            show_latest
            ;;
        generate|"")
            generate_report
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# اجرا
main "$@"

