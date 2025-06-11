#!/bin/bash
# Author :  Humair Munir
# email : humairmunirawan@gmail.com
# Script: ocr.sh
# Purpose: Convert PDF to images and extract text using OCR with a colorful UI

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_LANG="eng"
LOG_FILE="ocr_log.txt"
CLEANUP_IMAGES=false

# Function to display usage
usage() {
    echo -e "${CYAN}Usage: $0 <PDF_PATH> <IMG_DIR> <EXT_TEXT> [OPTIONS]${NC}"
    echo -e "${CYAN}Options:${NC}"
    echo -e "${CYAN}  --lang=<LANG>    Set Tesseract language (default: $DEFAULT_LANG)${NC}"
    echo -e "${CYAN}  --cleanup        Remove temporary images after processing${NC}"
    echo -e "${CYAN}  --log=<FILE>     Specify log file (default: $LOG_FILE)${NC}"
    echo -e "${CYAN}  --help           Display this help message${NC}"
    exit 1
}

# Function to log and display messages
log_message() {
    local type="$1"
    local msg="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    case "$type" in
        "INFO")
            echo -e "${BLUE}[INFO] $msg${NC}"
            echo "[$timestamp] [INFO] $msg" >> "$LOG_FILE"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS] $msg${NC}"
            echo "[$timestamp] [SUCCESS] $msg" >> "$LOG_FILE"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING] $msg${NC}"
            echo "[$timestamp] [WARNING] $msg" >> "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR] $msg${NC}"
            echo "[$timestamp] [ERROR] $msg" >> "$LOG_FILE"
            exit 1
            ;;
    esac
}

# Function to display progress bar
progress_bar() {
    local current=$1
    local total=$2
    local width=40
    local percent=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    local bar=""
    for ((i=0; i<filled; i++)); do bar+="█"; done
    for ((i=0; i<empty; i++)); do bar+=" "; done
    echo -ne "${CYAN}[${bar}] $percent% ($current/$total)\r${NC}"
}

# Function to check dependencies
check_dependencies() {
    local deps=("pdftoppm" "tesseract")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_message "ERROR" "'$dep' is not installed. Please install it."
        fi
    done
}

# Parse arguments
PDF_PATH=""
IMG_DIR=""
EXT_TEXT=""
LANG="$DEFAULT_LANG"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --lang=*)
            LANG="${1#*=}"
            shift
            ;;
        --cleanup)
            CLEANUP_IMAGES=true
            shift
            ;;
        --log=*)
            LOG_FILE="${1#*=}"
            shift
            ;;
        --help)
            usage
            ;;
        *)
            if [ -z "$PDF_PATH" ]; then
                PDF_PATH="$1"
            elif [ -z "$IMG_DIR" ]; then
                IMG_DIR="$1"
            elif [ -z "$EXT_TEXT" ]; then
                EXT_TEXT="$1"
            else
                log_message "ERROR" "Unexpected argument '$1'."
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [ -z "$PDF_PATH" ] || [ -z "$IMG_DIR" ] || [ -z "$EXT_TEXT" ]; then
    log_message "ERROR" "Missing required arguments."
fi

# Validate inputs
if [ ! -f "$PDF_PATH" ]; then
    log_message "ERROR" "PDF file '$PDF_PATH' not found."
fi

if [ -d "$EXT_TEXT" ]; then
    log_message "ERROR" "EXT_TEXT '$EXT_TEXT' is a directory. Please specify a file path."
fi

# Check if Tesseract supports the specified language
if ! tesseract --list-langs 2>/dev/null | grep -q "^$LANG$"; then
    log_message "ERROR" "Tesseract language '$LANG' is not installed. Available languages: $(tesseract --list-langs 2>/dev/null | tail -n +2 | tr '\n' ' ')"
fi

# Check dependencies
check_dependencies

# Step 1: Convert PDF to images
log_message "INFO" "🔄 Converting PDF to images..."
mkdir -p "$IMG_DIR"
pdftoppm "$PDF_PATH" "$IMG_DIR/img" -png
if [ $? -ne 0 ]; then
    log_message "ERROR" "Failed to convert PDF to images."
fi

# Count total images for progress
total_images=$(ls -1 "$IMG_DIR"/img-*.png 2>/dev/null | wc -l)
if [ "$total_images" -eq 0 ]; then
    log_message "ERROR" "No images generated from PDF."
fi

# Step 2: Run OCR on all images
log_message "INFO" "🔄 Extracting text using OCR (language: $LANG)..."
> "$EXT_TEXT"  # Clear or create the output file
current_image=0

for img in "$IMG_DIR"/img-*.png; do
    if [ -f "$img" ]; then
        ((current_image++))
        page=$(basename "$img" .png | grep -oP '\d+')
        progress_bar $current_image $total_images
        echo -e "\n\n--- Page $page ---" >> "$EXT_TEXT"
        tesseract "$img" stdout -l "$LANG" >> "$EXT_TEXT" 2>> "$LOG_FILE"
        if [ $? -ne 0 ]; then
            log_message "WARNING" "OCR failed for page $page."
        fi
    fi
done
echo -e "\n"  # Clear progress bar line

# Step 3: Cleanup (if enabled)
if [ "$CLEANUP_IMAGES" = true ]; then
    log_message "INFO" "🧹 Cleaning up temporary images..."
    rm -f "$IMG_DIR"/img-*.png
    rmdir "$IMG_DIR" 2>/dev/null
fi

log_message "SUCCESS" "✅ OCR processing complete. Results saved to '$EXT_TEXT'."
