import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import re
import logging
import sys
import pkg_resources
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser
from serpapi import GoogleSearch

# Setup logging with UTF-8 encoding for compatibility with Python 3.8
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler("webcrab.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Debug mode
DEBUG = True

# Log environment info
logging.info(f"Python version: {sys.version}")
logging.info(f"google-search-results version: {pkg_resources.get_distribution('google-search-results').version}")

# --- Setup Chrome Driver (for screenshots only) ---
def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        if DEBUG:
            logging.info("Chrome driver initialized successfully")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {str(e)}")
        raise

# --- Check robots.txt ---
def is_scraping_allowed(url):
    try:
        from urllib.robotparser import RobotFileParser
        rp = RobotFileParser()
        rp.set_url(f"{url}/robots.txt")
        rp.read()
        allowed = rp.can_fetch("*", url)
        if DEBUG:
            logging.info(f"robots.txt check for {url}: {'Allowed' if allowed else 'Not allowed'}")
        return allowed
    except Exception as e:
        logging.warning(f"Could not check robots.txt for {url}: {str(e)}")
        return True

# --- Scrape Businesses from Google Search using SerpAPI ---
def scrape_businesses_from_google(niche, location, num_results=3, api_key=None):
    params = {
        "q": f"{niche} in {location}",
        "api_key": api_key,
        "num": num_results
    }
    try:
        if DEBUG:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
            # Use dictionary unpacking for compatibility with Python <3.9
            log_params = {**params, "api_key": masked_key}
            logging.info(f"Sending SerpAPI request with params: {log_params}")
            print(f"Sending SerpAPI request with params: {log_params}")
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if DEBUG:
            logging.info(f"SerpAPI raw response: {results}")
            print(f"SerpAPI raw response: {results}")
        
        if "error" in results:
            logging.error(f"SerpAPI error: {results['error']}")
            return []
        
        organic_results = results.get("organic_results", [])
        if not organic_results:
            logging.warning(f"No organic results found for {niche} in {location}")
            return []
        
        links = [result.get("link") for result in organic_results if result.get("link")]
        unique_links = list(set(links))[:num_results]
        if DEBUG:
            logging.info(f"Scraped {len(unique_links)} websites for {niche} in {location}: {unique_links}")
            print(f"Scraped {len(unique_links)} websites for {niche} in {location}: {unique_links}")
        return unique_links
    except Exception as e:
        logging.error(f"Failed to scrape via SerpAPI for {niche} in {location}: {str(e)}")
        print(f"Failed to scrape via SerpAPI for {niche} in {location}: {str(e)}")
        return []

# --- Analyze Website Design ---
def fetch_website(url):
    return requests.get(url, timeout=10, allow_redirects=True)

def analyze_website(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        if not is_scraping_allowed(url):
            return {
                "Website": url,
                "Design Issues": "Scraping not allowed by robots.txt",
                "Load Time (s)": None,
                "Performance Score": None
            }
        logging.info(f"Analyzing website: {url}")
        
        start_time = time.time()
        r = fetch_website(url)
        r.raise_for_status()
        load_time = time.time() - start_time
        
        soup = BeautifulSoup(r.text, "html.parser")
        html = soup.prettify().lower()

        issues = []
        if not soup.find("meta", attrs={"name": "viewport"}):
            issues.append("Not mobile-friendly")
        if not r.url.startswith("https://"):
            issues.append("Lacks HTTPS")
        current_year = time.strftime("%Y")
        old_years = [str(year) for year in range(2000, int(current_year) - 3)]
        if any(year in html for year in old_years):
            issues.append("Old copyright year detected")
        if any(x in html for x in ["wordpress", "joomla", "drupal", "template by"]):
            issues.append("Uses outdated CMS or template")
        modern_indicators = ["react", "vue", "angular", "bootstrap", "tailwind"]
        if not any(indicator in html for indicator in modern_indicators):
            issues.append("No modern frameworks detected")
        if load_time > 5:
            issues.append("Slow load time (>5s)")
        links = soup.find_all("a", href=True)
        broken_links = 0
        for link in links[:10]:
            href = link["href"]
            if href.startswith(("http", "https")):
                try:
                    link_r = requests.head(href, timeout=5, allow_redirects=True)
                    if link_r.status_code >= 400:
                        broken_links += 1
                except:
                    broken_links += 1
        if broken_links > 0:
            issues.append(f"Detected {broken_links} broken links")

        result = {
            "Website": url,
            "Design Issues": ", ".join(issues) if issues else "Appears modern",
            "Load Time (s)": round(load_time, 2),
            "Performance Score": None
        }
        if DEBUG:
            logging.info(f"Analysis result for {url}: {result}")
        return result
    except Exception as e:
        logging.error(f"Error analyzing {url}: {str(e)}")
        return {
            "Website": url,
            "Design Issues": f"Error: {str(e)}",
            "Load Time (s)": None,
            "Performance Score": None
        }

# --- Take Screenshot of Website ---
def screenshot_website(url, file_name="screenshot.png", folder="screenshots"):
    try:
        os.makedirs(folder, exist_ok=True)
        safe_name = re.sub(r'[^\w\-_\.]', '_', file_name)
        path = os.path.join(folder, safe_name)
        
        with start_driver() as driver:
            driver.set_window_size(1920, 1080)
            driver.get(url)
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.save_screenshot(path)
            logging.info(f"Screenshot saved: {path}")
            return path
    except Exception as e:
        logging.error(f"Screenshot failed for {url}: {str(e)}")
        return f"Screenshot Failed: {str(e)}"

# --- GUI Application ---
class WebCrabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebCrab")
        self.root.geometry("1200x800")
        
        # Set crab logo as window icon (base64-encoded PNG)
        crab_icon = """
        iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAACAklEQVRYw+2UsUtCURjHfy+7
        kGJrK7RaKy2CpGArjWCrQgh2tS4EQQS1DgpBydX1B7iIgoIuPoAuPoBuXHzg4goKgguCCxcu4u7e3QdCYQ6Teb/3nO/7fuc5
        z0wmBwcH8H3f8DqdwDAMc3NzsLOzA9M0wWAQJElCkiSQSqVoNBqUSqVotVoAII/Ho1KpBIfDQSKRYDab4fV6wTRN8Xg8yOfz
        wGaz4ff7AQCqqqKzswPbt29H13V0d3eju7sbDodBkiS4XC7UajVarRYsy8K2bQAAV1dXXC4XOp0OpmmC2WzG6XQCAABFUZTL
        ZYQQAlVVAYCmaYxGIwDA5/Ph8XgAALquK5VKIRwOA4BpmhAEAQBVVY/H44WmaYqmaZqmaQAAVVVRVZXJZDLQNA0A4Pf7oSgK
        AABVVVEURVEEQRAQQgghhBBCCCGEEEIIu7u7cLlc6PV6oSgKAAAej0e5XC6EEOByuZDJZMA0TQCArutKpVKhUqlQKBQKhUKh
        UCgUCoVCoVAoFAqFQuFyuRAOh4NpmiYIAoIoCjRNwzRNwzRN0zRN0zRN0zRN0zRN0zQhhBBCCCGEEEIIu7u7cLlc6PV6oSgK
        AAAej0e5XC6EEOByuZDJZMA0TQCArutKpVKhUqlQKBQKhUKhUCgUCoVCoVAoFAqFQuFyuRAOh4NpmiYIAoIoCjRNwzRNwzRN
        0zRN0zRN0zRN0zRN0zQhhBBCCCGEEEIIu7u7cLlc6PV6oSgKAAAej0e5XC6EEOByuZDJZMA0TQCArutKpVKhUqlQKBQKhUKh
        UCgUCoVCoVAoFAqFQuFyuRAOh4NpmiYIAoIoCjRNwzRNwzRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN0zRN
        0zRN0zRN0z
        """
        try:
            self.root.iconphoto(True, tk.PhotoImage(data=crab_icon))
            logging.info("Crab logo icon set successfully")
        except Exception as e:
            logging.warning(f"Failed to set crab logo icon: {str(e)}")
        
        # Hardcode SerpAPI key
        self.api_key = "30c368dcbfb921060b7eb411debc5b08e22e3b78d78c63dbbe76591de2c6b4d1"
        
        if DEBUG:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
            logging.info(f"Initialized with API key: {masked_key}")
            print(f"Initialized with API key: {masked_key}")
        
        self.categories = ["dentists", "law firms", "retail stores", "startups", "restaurants"]
        self.countries = ["USA", "Canada", "UK", "Australia", "Germany", "Japan", "France"]
        
        self.selected_country = tk.StringVar(value="USA")  # Set default value
        self.area = tk.StringVar()
        self.num_results = tk.StringVar(value="3")
        self.search_all_categories = tk.BooleanVar(value=False)
        self.filter_text = tk.StringVar()
        
        self.results = []
        self.filtered_results = []
        
        self.create_widgets()
        
    def create_widgets(self):
        loc_frame = ttk.LabelFrame(self.root, text="Location", padding=10)
        loc_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(loc_frame, text="Country:").grid(row=0, column=0, sticky="w", padx=5)
        country_combo = ttk.Combobox(loc_frame, textvariable=self.selected_country, values=self.countries, state="readonly")
        country_combo.grid(row=0, column=1, sticky="ew", padx=5)
        country_combo.set("USA")  # Set default selection
        
        ttk.Label(loc_frame, text="Area (optional):").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(loc_frame, textvariable=self.area).grid(row=1, column=1, sticky="ew", padx=5)
        
        cat_frame = ttk.LabelFrame(self.root, text="Business Categories", padding=10)
        cat_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(cat_frame, text="Search All Categories", variable=self.search_all_categories, command=self.toggle_category_selection).pack(anchor="w")
        
        self.category_listbox = tk.Listbox(cat_frame, selectmode="multiple", height=5, exportselection=False)
        for cat in self.categories:
            self.category_listbox.insert(tk.END, cat)
        self.category_listbox.pack(fill="x", pady=5)
        
        ttk.Label(cat_frame, text="Add Custom Category:").pack(anchor="w")
        self.custom_category = tk.StringVar()
        custom_entry = ttk.Entry(cat_frame, textvariable=self.custom_category)
        custom_entry.pack(fill="x", pady=2)
        ttk.Button(cat_frame, text="Add Category", command=self.add_category).pack(anchor="w")
        
        param_frame = ttk.LabelFrame(self.root, text="Search Parameters", padding=10)
        param_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(param_frame, text="Results per Search:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(param_frame, textvariable=self.num_results, width=10).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Button(self.root, text="Start Search", command=self.start_search).pack(pady=5)
        ttk.Button(self.root, text="Run Test Query", command=self.run_test_query).pack(pady=5)
        
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(anchor="w")
        
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        
        result_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        filter_frame = ttk.Frame(result_frame)
        filter_frame.pack(fill="x", pady=5)
        ttk.Label(filter_frame, text="Filter Results:").pack(side="left", padx=5)
        ttk.Entry(filter_frame, textvariable=self.filter_text).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Clear Filter", command=self.clear_filter).pack(side="left", padx=5)
        
        self.tree = ttk.Treeview(result_frame, columns=("Website", "Design Issues", "Load Time", "Performance", "Screenshot", "Niche", "Location"), show="headings")
        self.tree.heading("Website", text="Website")
        self.tree.heading("Design Issues", text="Design Issues")
        self.tree.heading("Load Time", text="Load Time (s)")
        self.tree.heading("Performance", text="Performance Score")
        self.tree.heading("Screenshot", text="Screenshot")
        self.tree.heading("Niche", text="Niche")
        self.tree.heading("Location", text="Location")
        self.tree.column("Website", width=200)
        self.tree.column("Design Issues", width=300)
        self.tree.column("Load Time", width=100)
        self.tree.column("Performance", width=100)
        self.tree.column("Screenshot", width=200)
        self.tree.column("Niche", width=100)
        self.tree.column("Location", width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.view_screenshot)
        
        save_frame = ttk.Frame(self.root)
        save_frame.pack(pady=10)
        ttk.Button(save_frame, text="Save to CSV", command=lambda: self.save_results("csv")).pack(side="left", padx=5)
        ttk.Button(save_frame, text="Save to Excel", command=lambda: self.save_results("excel")).pack(side="left", padx=5)
        
        ttk.Button(self.root, text="Test Table", command=self.test_table).pack(pady=5)
        ttk.Button(self.root, text="Refresh Table", command=lambda: self.update_table(self.filtered_results)).pack(pady=5)
        
    def log_message(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)
        logging.info(message)
        if DEBUG:
            print(message)
    
    def test_table(self):
        self.tree.insert("", "end", values=("Test", "Test Issue", "1.0", "", "test.png", "Test Niche", "Test Location"))
        self.log_message("Inserted test row")
        self.root.update()
    
    def toggle_category_selection(self):
        state = "disabled" if self.search_all_categories.get() else "normal"
        self.category_listbox.configure(state=state)
    
    def add_category(self):
        category = self.custom_category.get().strip()
        if category and category not in self.categories:
            self.categories.append(category)
            self.category_listbox.insert(tk.END, category)
            self.custom_category.set("")
            self.log_message(f"Added category: {category}")
    
    def view_screenshot(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            screenshot_path = item["values"][4]
            if os.path.exists(screenshot_path):
                webbrowser.open(f"file://{os.path.abspath(screenshot_path)}")
            else:
                messagebox.showerror("Error", f"Screenshot not found: {screenshot_path}")
    
    def apply_filter(self):
        filter_text = self.filter_text.get().lower()
        self.filtered_results = [
            result for result in self.results
            if (filter_text in result["Website"].lower() or
                filter_text in result["Design Issues"].lower() or
                filter_text in result["Niche"].lower() or
                filter_text in result["Location"].lower())
        ]
        self.update_table(self.filtered_results)
        self.log_message(f"Applied filter: {filter_text}, showing {len(self.filtered_results)} results")
    
    def clear_filter(self):
        self.filter_text.set("")
        self.filtered_results = self.results
        self.update_table(self.results)
        self.log_message(f"Cleared filter, showing {len(self.results)} results")
    
    def update_table(self, results):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for result in results:
            self.tree.insert("", "end", values=(
                result["Website"],
                result["Design Issues"],
                result.get("Load Time (s)", ""),
                result.get("Performance Score", ""),
                result["Screenshot"],
                result["Niche"],
                result["Location"]
            ))
        self.root.update()
    
    def run_test_query(self):
        self.results.clear()
        self.filtered_results.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.log_message("Running test query: dentists in USA, num=3")
        self.status_label.configure(text="Running test query...")
        
        self.run_test_query_thread()
    
    def run_test_query_thread(self):
        try:
            websites = scrape_businesses_from_google("dentists", "USA", 3, self.api_key)
            
            if not websites:
                self.log_message("No websites found for test query")
                messagebox.showwarning("Warning", "No results for test query. Check log for details.")
                self.status_label.configure(text="Ready")
                return
            
            for j, site in enumerate(websites, 1):
                self.log_message(f"[{j}] Analyzing: {site}")
                analysis = analyze_website(site)
                screenshot_path = screenshot_website(site, file_name=f"screenshot_test_{j}.png")
                analysis["Screenshot"] = screenshot_path
                analysis["Niche"] = "dentists"
                analysis["Location"] = "USA"
                analysis["Timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.results.append(analysis)
                self.filtered_results.append(analysis)
                
                self.tree.insert("", "end", values=(
                    analysis["Website"],
                    analysis["Design Issues"],
                    analysis.get("Load Time (s)", ""),
                    analysis.get("Performance Score", ""),
                    analysis["Screenshot"],
                    analysis["Niche"],
                    analysis["Location"]
                ))
                self.log_message(f"Added to table: {analysis['Website']} - {analysis['Design Issues']}")
                self.root.update()
            
            self.log_message(f"Test query completed. Found {len(self.results)} results.")
            messagebox.showinfo("Success", f"Test query completed. Found {len(self.results)} results.")
        except Exception as e:
            self.log_message(f"Test query failed: {str(e)}")
            messagebox.showerror("Error", f"Test query failed: {str(e)}")
        finally:
            self.status_label.configure(text="Ready")
    
    def start_search(self):
        # Log the selected country for debugging
        selected_country = self.selected_country.get()
        self.log_message(f"Selected country: '{selected_country}'")
        
        # Check if a country is selected
        if not selected_country or selected_country not in self.countries:
            messagebox.showerror("Error", "Please select a valid country.")
            return
        
        try:
            num_results = int(self.num_results.get())
            if num_results <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of results.")
            return
        
        if self.search_all_categories.get():
            categories = self.categories
        else:
            selected_indices = self.category_listbox.curselection()
            categories = [self.category_listbox.get(i) for i in selected_indices]
            if not categories:
                messagebox.showerror("Error", "Please select at least one category or check 'Search All Categories'.")
                return
        
        location = selected_country
        area = self.area.get().strip()
        if area:
            location = f"{area}, {location}"
        
        self.results.clear()
        self.filtered_results.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.log_message(f"Starting search for {categories} in {location} with {num_results} results per category")
        self.status_label.configure(text="Searching... (please wait)")
        
        self.run_search(categories, location, num_results)
    
    def run_search(self, categories, location, num_results):
        try:
            total_searches = len(categories)
            self.progress["maximum"] = total_searches
            self.progress["value"] = 0
            
            for i, niche in enumerate(categories, 1):
                self.status_label.configure(text=f"Searching {niche} in {location} ({i}/{total_searches})")
                self.log_message(f"Searching for {niche} in {location}")
                
                websites = scrape_businesses_from_google(niche, location, num_results, self.api_key)
                
                if not websites:
                    self.log_message(f"No websites found for {niche} in {location}. Try a more specific query or check API key.")
                    self.progress["value"] = i
                    self.root.update_idletasks()
                    continue
                
                for j, site in enumerate(websites, 1):
                    self.log_message(f"[{j}] Analyzing: {site}")
                    analysis = analyze_website(site)
                    screenshot_path = screenshot_website(site, file_name=f"screenshot_{niche}_{location.replace(', ', '_')}_{j}.png")
                    analysis["Screenshot"] = screenshot_path
                    analysis["Niche"] = niche
                    analysis["Location"] = location
                    analysis["Timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self.results.append(analysis)
                    self.filtered_results.append(analysis)
                    
                    self.tree.insert("", "end", values=(
                        analysis["Website"],
                        analysis["Design Issues"],
                        analysis.get("Load Time (s)", ""),
                        analysis.get("Performance Score", ""),
                        analysis["Screenshot"],
                        analysis["Niche"],
                        analysis["Location"]
                    ))
                    self.log_message(f"Added to table: {analysis['Website']} - {analysis['Design Issues']}")
                    self.root.update()
                
                self.progress["value"] = i
                self.root.update_idletasks()
                time.sleep(10)  # Rate limiting
            
            if not self.results:
                self.log_message("No results found for the given search criteria.")
                messagebox.showwarning("Warning", "No results found. Check the log for details or try different search criteria.")
            else:
                self.log_message(f"Search completed. Found {len(self.results)} results.")
                messagebox.showinfo("Success", f"Search completed. Found {len(self.results)} results.")
        except Exception as e:
            self.log_message(f"Search failed: {str(e)}")
            messagebox.showerror("Error", f"Search failed: {str(e)}")
        finally:
            self.status_label.configure(text="Ready")
    
    def save_results(self, format_type):
        if not self.results:
            messagebox.showerror("Error", "No results to save.")
            return
        
        try:
            df = pd.DataFrame(self.results)
            if format_type == "csv":
                df.to_csv("webcrab_analysis.csv", index=False)
                self.log_message("Results saved to webcrab_analysis.csv")
                messagebox.showinfo("Success", "Results saved to webcrab_analysis.csv")
            elif format_type == "excel":
                df.to_excel("webcrab_analysis.xlsx", index=False, engine="openpyxl")
                self.log_message("Results saved to webcrab_analysis.xlsx")
                messagebox.showinfo("Success", "Results saved to webcrab_analysis.xlsx")
        except Exception as e:
            self.log_message(f"Failed to save results: {str(e)}")
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

# --- Run Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = WebCrabApp(root)
    root.mainloop()