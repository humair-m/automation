#!/bin/bash
# Author : Humair Munir
# email : humairmunirawan@gmail.com
# Script: tesseract_ocr_gui.sh
# Purpose: Convert PDF to images and extract text using OCR with a GUI interface

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if zenity is installed
if ! command -v zenity &> /dev/null; then
    echo -e "${RED}[ERROR] Zenity is not installed. Please install it with:${NC}"
    echo -e "${YELLOW}    sudo apt-get install zenity${NC} (for Debian/Ubuntu)"
    echo -e "${YELLOW}    sudo yum install zenity${NC} (for CentOS/RHEL)"
    exit 1
fi

# Default values
DEFAULT_LANG="eng"
LOG_FILE="ocr_log.txt"
CLEANUP_IMAGES=false
AVAILABLE_LANGS=$(tesseract --list-langs 2>/dev/null | tail -n +2 | tr '\n' '|')

# Function to display console usage
usage() {
    echo -e "${CYAN}Usage: $0 [OPTIONS]${NC}"
    echo -e "${CYAN}Options:${NC}"
    echo -e "${CYAN}  --no-gui         Run in command-line mode${NC}"
    echo -e "${CYAN}  --help           Display this help message${NC}"
    echo -e "${CYAN}${NC}"
    echo -e "${CYAN}For CLI mode, additional arguments:${NC}"
    echo -e "${CYAN}  <PDF_PATH> <IMG_DIR> <EXT_TEXT> [OPTIONS]${NC}"
    echo -e "${CYAN}  --lang=<LANG>    Set Tesseract language (default: $DEFAULT_LANG)${NC}"
    echo -e "${CYAN}  --cleanup        Remove temporary images after processing${NC}"
    echo -e "${CYAN}  --log=<FILE>     Specify log file (default: $LOG_FILE)${NC}"
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
            if [ "$GUI_MODE" = true ]; then
                zenity --info --title="OCR Information" --text="$msg" --width=300 &
            fi
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS] $msg${NC}"
            echo "[$timestamp] [SUCCESS] $msg" >> "$LOG_FILE"
            if [ "$GUI_MODE" = true ]; then
                zenity --info --title="OCR Success" --text="$msg" --width=300
            fi
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING] $msg${NC}"
            echo "[$timestamp] [WARNING] $msg" >> "$LOG_FILE"
            if [ "$GUI_MODE" = true ]; then
                zenity --warning --title="OCR Warning" --text="$msg" --width=300
            fi
            ;;
        "ERROR")
            echo -e "${RED}[ERROR] $msg${NC}"
            echo "[$timestamp] [ERROR] $msg" >> "$LOG_FILE"
            if [ "$GUI_MODE" = true ]; then
                zenity --error --title="OCR Error" --text="$msg" --width=300
            fi
            return 1
            ;;
    esac
}

# Function to display progress bar
progress_bar() {
    local current=$1
    local total=$2
    
    if [ "$GUI_MODE" = true ]; then
        echo "$current"
        echo "# Processing page $current of $total..."
    else
        local width=40
        local percent=$((current * 100 / total))
        local filled=$((width * current / total))
        local empty=$((width - filled))
        local bar=""
        for ((i=0; i<filled; i++)); do bar+="█"; done
        for ((i=0; i<empty; i++)); do bar+=" "; done
        echo -ne "${CYAN}[${bar}] $percent% ($current/$total)\r${NC}"
    fi
}

# Function to check dependencies
check_dependencies() {
    local deps=("pdftoppm" "tesseract")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_message "ERROR" "'$dep' is not installed. Please install it."
            return 1
        fi
    done
    return 0
}

# Process OCR
run_ocr() {
    local PDF_PATH="$1"
    local IMG_DIR="$2"
    local EXT_TEXT="$3"
    local LANG="$4"
    local CLEANUP_IMAGES="$5"
    
    # Validate inputs
    if [ ! -f "$PDF_PATH" ]; then
        log_message "ERROR" "PDF file '$PDF_PATH' not found."
        return 1
    fi

    if [ -d "$EXT_TEXT" ]; then
        log_message "ERROR" "EXT_TEXT '$EXT_TEXT' is a directory. Please specify a file path."
        return 1
    fi

    # Check if Tesseract supports the specified language
    if ! tesseract --list-langs 2>/dev/null | grep -q "^$LANG$"; then
        log_message "ERROR" "Tesseract language '$LANG' is not installed. Available languages: $(tesseract --list-langs 2>/dev/null | tail -n +2 | tr '\n' ' ')"
        return 1
    fi

    # Check dependencies
    if ! check_dependencies; then
        return 1
    fi

    # Step 1: Convert PDF to images
    log_message "INFO" "🔄 Converting PDF to images..."
    mkdir -p "$IMG_DIR"
    pdftoppm "$PDF_PATH" "$IMG_DIR/img" -png
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to convert PDF to images."
        return 1
    fi

    # Count total images for progress
    total_images=$(ls -1 "$IMG_DIR"/img-*.png 2>/dev/null | wc -l)
    if [ "$total_images" -eq 0 ]; then
        log_message "ERROR" "No images generated from PDF."
        return 1
    fi

    # Step 2: Run OCR on all images
    log_message "INFO" "🔄 Extracting text using OCR (language: $LANG)..."
    > "$EXT_TEXT"  # Clear or create the output file
    current_image=0

    if [ "$GUI_MODE" = true ]; then
        (
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
        ) | zenity --progress \
          --title="OCR Processing" \
          --text="Starting OCR extraction..." \
          --percentage=0 \
          --auto-close \
          --auto-kill \
          --width=350 \
          --max-value=$total_images
    else
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
    fi

    # Step 3: Cleanup (if enabled)
    if [ "$CLEANUP_IMAGES" = true ]; then
        log_message "INFO" "🧹 Cleaning up temporary images..."
        rm -f "$IMG_DIR"/img-*.png
        rmdir "$IMG_DIR" 2>/dev/null
    fi

    log_message "SUCCESS" "✅ OCR processing complete. Results saved to '$EXT_TEXT'."
    
    # Option to view the file
    if [ "$GUI_MODE" = true ]; then
        if zenity --question --title="OCR Complete" --text="Would you like to open the extracted text file?" --width=300; then
            if command -v xdg-open &> /dev/null; then
                xdg-open "$EXT_TEXT"
            elif command -v open &> /dev/null; then
                open "$EXT_TEXT"
            else
                log_message "WARNING" "Unable to open file automatically. Please open '$EXT_TEXT' manually."
            fi
        fi
    fi
    
    return 0
}

# Determine if we're running in GUI mode
GUI_MODE=true
PDF_PATH=""
IMG_DIR=""
EXT_TEXT=""
LANG="$DEFAULT_LANG"

# Parse command line arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        --no-gui)
            GUI_MODE=false
            shift
            ;;
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
                usage
            fi
            shift
            ;;
    esac
done

# Create or clear log file
> "$LOG_FILE"

# Main execution
if [ "$GUI_MODE" = true ]; then
    # GUI Mode
    
    # Welcome message
    zenity --info --title="OCR Tool" \
        --text="Welcome to the OCR Tool!\n\nThis utility will help you extract text from PDF files using optical character recognition." \
        --width=350
    
    # Get PDF file
    PDF_PATH=$(zenity --file-selection --title="Select PDF File" --file-filter="PDF files | *.pdf" --file-filter="All files | *.*")
    if [ -z "$PDF_PATH" ]; then
        exit 0  # User cancelled
    fi
    
    # Get output directory for images
    IMG_DIR=$(zenity --file-selection --title="Select Directory for Temporary Images" --directory)
    if [ -z "$IMG_DIR" ]; then
        exit 0  # User cancelled
    fi
    
    # Get output text file
    EXT_TEXT=$(zenity --file-selection --title="Select Output Text File" --save --confirm-overwrite --filename="output.txt")
    if [ -z "$EXT_TEXT" ]; then
        exit 0  # User cancelled
    fi
    
    # Get language
    LANG=$(zenity --list --title="Select OCR Language" --text="Choose a language:" \
        --column="Code" --column="Language" \
        eng "English" \
        deu "German" \
        fra "French" \
        spa "Spanish" \
        ita "Italian" \
        por "Portuguese" \
        rus "Russian" \
        chi_sim "Chinese (Simplified)" \
        jpn "Japanese" \
        kor "Korean" \
        ara "Arabic" \
        hin "Hindi" \
        --width=300 --height=400)
    
    if [ -z "$LANG" ]; then
        LANG="$DEFAULT_LANG"  # Default to English if cancelled
    fi
    
    # Cleanup option
    if zenity --question --title="Cleanup Option" --text="Would you like to remove temporary image files after processing?" --width=350; then
        CLEANUP_IMAGES=true
    else
        CLEANUP_IMAGES=false
    fi
    
    # Advanced options
    if zenity --question --title="Advanced Options" --text="Would you like to set advanced options?" --width=350; then
        LOG_FILE=$(zenity --entry --title="Log File" --text="Enter log file path:" --entry-text="$LOG_FILE" --width=350)
    fi
    
    # Run OCR with selected options
    run_ocr "$PDF_PATH" "$IMG_DIR" "$EXT_TEXT" "$LANG" "$CLEANUP_IMAGES"
    
else
    # CLI Mode
    if [ -z "$PDF_PATH" ] || [ -z "$IMG_DIR" ] || [ -z "$EXT_TEXT" ]; then
        log_message "ERROR" "Missing required arguments."
        usage
    fi
    
    run_ocr "$PDF_PATH" "$IMG_DIR" "$EXT_TEXT" "$LANG" "$CLEANUP_IMAGES"
fi
