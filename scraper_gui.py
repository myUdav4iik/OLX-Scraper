import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import json
import os
from datetime import datetime
from main import OLXScraper

class OLXScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OLX Scraper - Parking Spots")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize scraper
        self.scraper = OLXScraper()
        self.is_scraping = False
        self.current_thread = None
        
        # Style configuration
        self.setup_styles()
        
        # Create main interface
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="OLX Parking Spots Scraper", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL Section
        url_frame = ttk.LabelFrame(main_frame, text="URL Configuration", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="OLX URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.url_var = tk.StringVar(value="https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/?search%5Bphotos%5D=1&search%5Border%5D=created_at:desc")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(url_frame, text="Reset Default", command=self.reset_url).grid(row=0, column=2)
        
        # Scraping Options
        options_frame = ttk.LabelFrame(main_frame, text="Scraping Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Max pages
        ttk.Label(options_frame, text="Max Pages:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.max_pages_var = tk.StringVar(value="20")
        ttk.Entry(options_frame, textvariable=self.max_pages_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Target records
        ttk.Label(options_frame, text="Target Records:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.target_records_var = tk.StringVar(value="300")
        ttk.Entry(options_frame, textvariable=self.target_records_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Detailed scraping
        self.detailed_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Get detailed info", variable=self.detailed_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Max detailed records
        ttk.Label(options_frame, text="Max Detailed:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.max_detailed_var = tk.StringVar(value="50")
        ttk.Entry(options_frame, textvariable=self.max_detailed_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2)
        
        ttk.Label(output_frame, text="Filename Prefix:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.filename_prefix_var = tk.StringVar(value="parking_listings")
        ttk.Entry(output_frame, textvariable=self.filename_prefix_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to start scraping...")
        ttk.Label(progress_frame, textvariable=self.progress_var, style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Statistics
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        ttk.Label(stats_frame, text="Found:").grid(row=0, column=0, sticky=tk.W)
        self.found_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.found_var, foreground='blue').grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(stats_frame, text="Current Page:").grid(row=0, column=2, sticky=tk.W)
        self.page_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.page_var, foreground='blue').grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial log message
        self.log("OLX Scraper initialized. Ready to start scraping.")
    
    def reset_url(self):
        """Reset URL to default parking URL"""
        default_url = "https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/?search%5Bphotos%5D=1&search%5Border%5D=created_at:desc"
        self.url_var.set(default_url)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def open_output_folder(self):
        """Open output folder in file manager"""
        import subprocess
        import platform
        
        path = self.output_dir_var.get()
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
    
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, message, found=None, page=None):
        """Update progress indicators"""
        self.progress_var.set(message)
        if found is not None:
            self.found_var.set(str(found))
        if page is not None:
            self.page_var.set(str(page))
        self.root.update_idletasks()
    
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if self.is_scraping:
            return
        
        # Validate inputs
        try:
            max_pages = int(self.max_pages_var.get())
            target_records = int(self.target_records_var.get())
            max_detailed = int(self.max_detailed_var.get())
            
            if max_pages < 1 or target_records < 1 or max_detailed < 1:
                raise ValueError("All numeric values must be positive")
                
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input values: {e}")
            return
        
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Invalid Input", "Please enter a valid OLX URL")
            return
        
        # Update UI state
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start(10)
        
        # Clear previous stats
        self.found_var.set("0")
        self.page_var.set("0")
        
        # Start scraping thread
        self.current_thread = threading.Thread(
            target=self.scrape_worker,
            args=(url, max_pages, target_records, max_detailed),
            daemon=True
        )
        self.current_thread.start()
    
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.is_scraping:
            self.log("Stopping scraper... (current page will complete)")
            self.is_scraping = False
            self.update_progress("Stopping...")
    
    def scrape_worker(self, url, max_pages, target_records, max_detailed):
        """Worker function that runs in separate thread"""
        try:
            self.log(f"Starting scraping process...")
            self.log(f"URL: {url}")
            self.log(f"Max pages: {max_pages}, Target records: {target_records}")
            
            self.update_progress("Initializing scraper...")
            
            # Create custom scraper with progress callbacks
            scraper = OLXScraperWithProgress(self)
            
            # Start basic scraping
            self.update_progress("Scraping basic listings...")
            listings = scraper.scrape_url(url, max_pages=max_pages)
            
            if not self.is_scraping:
                self.scraping_finished("Scraping stopped by user")
                return
            
            # Limit to target records
            if len(listings) > target_records:
                listings = listings[:target_records]
            
            self.log(f"Found {len(listings)} basic listings")
            
            # Save basic listings
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            basic_filename = f"{self.filename_prefix_var.get()}_basic_{timestamp}.json"
            basic_filepath = os.path.join(self.output_dir_var.get(), basic_filename)
            
            with open(basic_filepath, 'w', encoding='utf-8') as f:
                json.dump(listings, f, ensure_ascii=False, indent=2)
            
            self.log(f"Basic listings saved to: {basic_filename}")
            
            # Detailed scraping if requested
            detailed_listings = []
            if self.detailed_var.get() and listings and self.is_scraping:
                self.update_progress("Getting detailed information...")
                self.log(f"Getting detailed info for up to {max_detailed} listings...")
                
                detailed_count = min(max_detailed, len(listings))
                for i, listing in enumerate(listings[:detailed_count]):
                    if not self.is_scraping:
                        break
                    
                    if not listing.get('url'):
                        continue
                    
                    self.update_progress(f"Getting details {i+1}/{detailed_count}...")
                    self.log(f"Getting details for listing {i+1}/{detailed_count}: {listing.get('title', 'N/A')[:50]}...")
                    
                    try:
                        details = scraper.get_listing_details(listing['url'])
                        detailed_listing = {**listing, **details}
                        detailed_listings.append(detailed_listing)
                        
                        # Update progress
                        self.root.after(0, lambda: self.found_var.set(str(len(detailed_listings))))
                        
                        # Respectful delay
                        import time
                        time.sleep(3)
                        
                    except Exception as e:
                        self.log(f"Error getting details for listing {i+1}: {e}")
                        detailed_listings.append(listing)
                        continue
                
                # Save detailed listings
                if detailed_listings:
                    detailed_filename = f"{self.filename_prefix_var.get()}_detailed_{timestamp}.json"
                    detailed_filepath = os.path.join(self.output_dir_var.get(), detailed_filename)
                    
                    with open(detailed_filepath, 'w', encoding='utf-8') as f:
                        json.dump(detailed_listings, f, ensure_ascii=False, indent=2)
                    
                    self.log(f"Detailed listings saved to: {detailed_filename}")
            
            # Final summary
            summary = f"Scraping completed successfully!\n"
            summary += f"Basic listings: {len(listings)}\n"
            if detailed_listings:
                summary += f"Detailed listings: {len(detailed_listings)}\n"
            summary += f"Files saved to: {self.output_dir_var.get()}"
            
            self.scraping_finished(summary)
            
        except Exception as e:
            error_msg = f"Error during scraping: {str(e)}"
            self.log(error_msg)
            self.scraping_finished(error_msg, is_error=True)
    
    def scraping_finished(self, message, is_error=False):
        """Called when scraping is complete"""
        self.root.after(0, self._finish_scraping, message, is_error)
    
    def _finish_scraping(self, message, is_error):
        """Update UI after scraping completion (runs in main thread)"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        if is_error:
            self.update_progress("Error occurred")
            messagebox.showerror("Scraping Error", message)
        else:
            self.update_progress("Completed")
            messagebox.showinfo("Scraping Complete", message)
        
        self.log(message)

class OLXScraperWithProgress(OLXScraper):
    """Extended scraper class with progress callbacks"""
    
    def __init__(self, gui):
        super().__init__()
        self.gui = gui
    
    def _scrape_listings_page(self, url: str):
        """Override to add progress updates"""
        # Extract page number for progress
        import re
        page_match = re.search(r'page=(\d+)', url)
        page_num = int(page_match.group(1)) if page_match else 1
        
        # Update progress
        self.gui.root.after(0, lambda: self.gui.page_var.set(str(page_num)))
        self.gui.root.after(0, lambda: self.gui.update_progress(f"Scraping page {page_num}..."))
        
        return super()._scrape_listings_page(url)
    
    def scrape_url(self, url: str, max_pages: int = 10):
        """Override to add progress tracking"""
        listings = []
        
        for page in range(1, max_pages + 1):
            if not self.gui.is_scraping:  # Check if stopped
                break
                
            self.gui.log(f"Scraping page {page}")
            
            # Add page parameter to URL
            page_url = f"{url}&page={page}" if '?' in url else f"{url}?page={page}"
            page_listings = self._scrape_listings_page(page_url)
            
            if not page_listings:
                self.gui.log(f"No listings found on page {page}, stopping...")
                break
            
            # Filter out invalid listings
            valid_listings = [l for l in page_listings if l.get('title') != 'N/A' and l.get('url')]
            listings.extend(valid_listings)
            
            # Update progress
            self.gui.root.after(0, lambda: self.gui.found_var.set(str(len(listings))))
            
            self.gui.log(f"Page {page}: Found {len(page_listings)} total, {len(valid_listings)} valid listings")
            
            # Respectful delay
            import time
            time.sleep(2)
        
        return listings

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = OLXScraperGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_scraping:
            if messagebox.askokcancel("Quit", "Scraping is in progress. Do you want to quit?"):
                app.is_scraping = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()