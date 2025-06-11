#!/usr/bin/env python3
"""
Beautiful OCR GUI Application
A modern, user-friendly interface for PDF to text conversion using OCR
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import tempfile
import shutil

class ModernOCRApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.setup_styles()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("OCR Studio - PDF to Text Converter")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"800x700+{x}+{y}")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def setup_variables(self):
        """Initialize variables"""
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.temp_dir = tk.StringVar(value=tempfile.gettempdir())
        self.language = tk.StringVar(value="eng")
        self.cleanup_images = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to process PDF files")
        
        # Available languages
        self.languages = {
            "eng": "English",
            "deu": "German", 
            "fra": "French",
            "spa": "Spanish",
            "ita": "Italian",
            "por": "Portuguese",
            "rus": "Russian",
            "chi_sim": "Chinese (Simplified)",
            "jpn": "Japanese",
            "kor": "Korean",
            "ara": "Arabic",
            "hin": "Hindi"
        }
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        
        # Configure colors
        bg_color = "#f8f9fa"
        accent_color = "#007bff"
        success_color = "#28a745"
        
        self.root.configure(bg=bg_color)
        
        # Configure styles
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 20, "bold"),
                       background=bg_color,
                       foreground="#2c3e50")
        
        style.configure("Subtitle.TLabel",
                       font=("Segoe UI", 11),
                       background=bg_color,
                       foreground="#6c757d")
        
        style.configure("Section.TLabel",
                       font=("Segoe UI", 12, "bold"),
                       background=bg_color,
                       foreground="#495057")
        
        style.configure("Modern.TButton",
                       font=("Segoe UI", 10),
                       padding=(20, 10))
        
        style.configure("Primary.TButton",
                       font=("Segoe UI", 12, "bold"),
                       padding=(30, 15))
        
    def create_widgets(self):
        """Create and arrange all widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(6, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # File selection section
        self.create_file_section(main_frame)
        
        # Options section
        self.create_options_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Control buttons
        self.create_controls(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create the header section"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = ttk.Label(header_frame, text="OCR Studio", style="Title.TLabel")
        title.grid(row=0, column=0)
        
        subtitle = ttk.Label(header_frame, 
                           text="Transform PDF documents into editable text with optical character recognition",
                           style="Subtitle.TLabel")
        subtitle.grid(row=1, column=0, pady=(5, 0))
        
    def create_file_section(self, parent):
        """Create file selection section"""
        file_frame = ttk.LabelFrame(parent, text="📁 File Selection", padding="20")
        file_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        file_frame.grid_columnconfigure(1, weight=1)
        
        # PDF input
        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w", pady=(0, 10))
        pdf_frame = ttk.Frame(file_frame)
        pdf_frame.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        pdf_frame.grid_columnconfigure(0, weight=1)
        
        self.pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_path, font=("Segoe UI", 10))
        self.pdf_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ttk.Button(pdf_frame, text="Browse", command=self.browse_pdf,
                  style="Modern.TButton").grid(row=0, column=1)
        
        # Output file
        ttk.Label(file_frame, text="Output Text:").grid(row=1, column=0, sticky="w")
        output_frame = ttk.Frame(file_frame)
        output_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, font=("Segoe UI", 10))
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output,
                  style="Modern.TButton").grid(row=0, column=1)
        
    def create_options_section(self, parent):
        """Create options section"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ Options", padding="20")
        options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Language selection
        ttk.Label(options_frame, text="Language:").grid(row=0, column=0, sticky="w", pady=(0, 10))
        lang_combo = ttk.Combobox(options_frame, textvariable=self.language, 
                                 values=list(self.languages.keys()),
                                 state="readonly", font=("Segoe UI", 10))
        lang_combo.grid(row=0, column=1, sticky="w", pady=(0, 10), padx=(10, 0))
        
        # Format display for language
        self.lang_display = ttk.Label(options_frame, text=self.languages[self.language.get()],
                                     style="Subtitle.TLabel")
        self.lang_display.grid(row=0, column=2, sticky="w", pady=(0, 10), padx=(10, 0))
        lang_combo.bind('<<ComboboxSelected>>', self.update_language_display)
        
        # Cleanup option
        cleanup_check = ttk.Checkbutton(options_frame, text="Clean up temporary images after processing",
                                       variable=self.cleanup_images)
        cleanup_check.grid(row=1, column=0, columnspan=3, sticky="w")
        
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progress", padding="20")
        progress_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready", font=("Segoe UI", 10))
        self.progress_label.grid(row=1, column=0)
        
        # Log area
        log_frame = ttk.Frame(progress_frame)
        log_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, font=("Consolas", 9),
                               bg="#2c3e50", fg="#ecf0f1", insertbackground="#ecf0f1")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
    def create_controls(self, parent):
        """Create control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, sticky="ew", pady=20)
        control_frame.grid_columnconfigure(1, weight=1)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start OCR Processing",
                                      command=self.start_processing, style="Primary.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.cancel_button = ttk.Button(control_frame, text="❌ Cancel",
                                       command=self.cancel_processing, style="Modern.TButton",
                                       state="disabled")
        self.cancel_button.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # View result button
        self.view_button = ttk.Button(control_frame, text="📄 View Result",
                                     command=self.view_result, style="Modern.TButton",
                                     state="disabled")
        self.view_button.grid(row=0, column=2, sticky="e")
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, sticky="ew", pady=(20, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        separator = ttk.Separator(status_frame, orient="horizontal")
        separator.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                               font=("Segoe UI", 9), style="Subtitle.TLabel")
        status_label.grid(row=1, column=0, sticky="w")
        
    def log_message(self, message, level="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"INFO": "#3498db", "SUCCESS": "#2ecc71", "WARNING": "#f39c12", "ERROR": "#e74c3c"}
        
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        
        # Color coding
        if level in colors:
            start_line = self.log_text.index(tk.END + "-2l linestart")
            end_line = self.log_text.index(tk.END + "-1l lineend")
            self.log_text.tag_add(level, start_line, end_line)
            self.log_text.tag_config(level, foreground=colors[level])
        
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_language_display(self, event=None):
        """Update language display"""
        lang_code = self.language.get()
        self.lang_display.config(text=self.languages.get(lang_code, "Unknown"))
        
    def browse_pdf(self):
        """Browse for PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            # Auto-generate output filename
            base_name = Path(filename).stem
            output_file = Path(filename).parent / f"{base_name}_extracted.txt"
            self.output_path.set(str(output_file))
            
    def browse_output(self):
        """Browse for output file"""
        filename = filedialog.asksaveasfilename(
            title="Save Extracted Text As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            
    def check_dependencies(self):
        """Check if required tools are installed"""
        tools = ["pdftoppm", "tesseract"]
        missing = []
        
        for tool in tools:
            if shutil.which(tool) is None:
                missing.append(tool)
        
        if missing:
            missing_str = ", ".join(missing)
            messagebox.showerror("Missing Dependencies", 
                               f"The following tools are required but not installed:\n{missing_str}\n\n"
                               f"Please install them using your package manager.")
            return False
        return True
        
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file.")
            return False
            
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return False
            
        if not Path(self.pdf_path.get()).exists():
            messagebox.showerror("Error", "The selected PDF file does not exist.")
            return False
            
        return True
        
    def start_processing(self):
        """Start OCR processing"""
        if not self.validate_inputs() or not self.check_dependencies():
            return
            
        # Update UI state
        self.start_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.view_button.config(state="disabled")
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(target=self.process_pdf, daemon=True)
        self.processing_cancelled = False
        self.processing_thread.start()
        
    def cancel_processing(self):
        """Cancel processing"""
        self.processing_cancelled = True
        self.log_message("Processing cancelled by user", "WARNING")
        self.reset_ui()
        
    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.progress_var.set(0)
        self.progress_label.config(text="Ready")
        self.status_var.set("Ready to process PDF files")
        
    def process_pdf(self):
        """Process PDF file (runs in separate thread)"""
        try:
            pdf_path = self.pdf_path.get()
            output_path = self.output_path.get()
            language = self.language.get()
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="ocr_")
            
            self.log_message("Starting OCR processing...", "INFO")
            self.status_var.set("Converting PDF to images...")
            
            # Step 1: Convert PDF to images
            self.progress_var.set(10)
            self.progress_label.config(text="Converting PDF to images...")
            
            cmd = ["pdftoppm", pdf_path, f"{temp_dir}/page", "-png"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"PDF conversion failed: {result.stderr}")
                
            if self.processing_cancelled:
                return
                
            # Count pages
            image_files = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])
            total_pages = len(image_files)
            
            if total_pages == 0:
                raise Exception("No images generated from PDF")
                
            self.log_message(f"Generated {total_pages} images from PDF", "SUCCESS")
            
            # Step 2: OCR processing
            self.status_var.set("Extracting text using OCR...")
            
            with open(output_path, 'w', encoding='utf-8') as output_file:
                for i, image_file in enumerate(image_files):
                    if self.processing_cancelled:
                        return
                        
                    page_num = i + 1
                    progress = 20 + (70 * i / total_pages)
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"Processing page {page_num} of {total_pages}")
                    
                    image_path = os.path.join(temp_dir, image_file)
                    
                    # Run OCR on image
                    cmd = ["tesseract", image_path, "stdout", "-l", language]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        output_file.write(f"\n\n--- Page {page_num} ---\n")
                        output_file.write(result.stdout)
                        self.log_message(f"Processed page {page_num}", "INFO")
                    else:
                        self.log_message(f"OCR failed for page {page_num}: {result.stderr}", "WARNING")
            
            # Step 3: Cleanup
            if self.cleanup_images.get():
                self.progress_var.set(95)
                self.progress_label.config(text="Cleaning up temporary files...")
                shutil.rmtree(temp_dir)
                self.log_message("Temporary files cleaned up", "INFO")
            
            # Completion
            self.progress_var.set(100)
            self.progress_label.config(text="Processing complete!")
            self.log_message(f"OCR processing completed successfully!", "SUCCESS")
            self.log_message(f"Output saved to: {output_path}", "SUCCESS")
            self.status_var.set("Processing completed successfully")
            
            # Enable view button
            self.view_button.config(state="normal")
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                                                         "OCR processing completed successfully!\n\n"
                                                         f"Text extracted and saved to:\n{output_path}"))
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "ERROR")
            self.status_var.set("Error occurred during processing")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))
        
        finally:
            # Reset UI
            self.root.after(0, self.reset_ui)
            
    def view_result(self):
        """Open the result file"""
        output_path = self.output_path.get()
        if output_path and Path(output_path).exists():
            try:
                if sys.platform.startswith('darwin'):  # macOS
                    subprocess.run(['open', output_path])
                elif sys.platform.startswith('win'):   # Windows
                    os.startfile(output_path)
                else:  # Linux
                    subprocess.run(['xdg-open', output_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
        else:
            messagebox.showwarning("Warning", "Output file not found.")
            
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main entry point"""
    app = ModernOCRApp()
    app.run()

if __name__ == "__main__":
    main()
