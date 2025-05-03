WebCrab
WebCrab is a Python-based GUI application that scrapes small business websites using SerpAPI, analyzes their design quality, and captures screenshots. It allows users to search for businesses by category (e.g., dentists, restaurants) and location, then generates reports on website performance, mobile-friendliness, and modern design practices. Results are displayed in a Tkinter-based interface and can be saved as CSV or Excel files.
Features

Search for businesses by category and location using SerpAPI.
Analyze website design (mobile-friendliness, HTTPS, load time, modern frameworks).
Capture screenshots of websites using Selenium.
Filter and display results in a table with double-click support to view screenshots.
Save results to CSV or Excel files.
Debug logging to webcrab.log for troubleshooting.

Prerequisites

Python: Version 3.8 or higher.
Tkinter: Included with standard Python installations. Ensure it's available (see Troubleshooting).
Google Chrome: Required for Selenium to take screenshots.
SerpAPI Key: A valid API key for SerpAPI (a hardcoded key is included for testing but should be replaced for production use).
Operating System: Windows, macOS, or Linux.

Installation

Clone the Repository:
git clone https://github.com/your-username/webcrab.git
cd webcrab


Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:Install all required Python libraries using pip:
pip install pandas requests beautifulsoup4 selenium webdriver-manager google-search-results openpyxl


Verify Prerequisites:

Ensure Python 3.8+ is installed:python --version


Check Tkinter availability:python -c "import tkinter"

If this fails, install Tkinter (see Troubleshooting).
Ensure Google Chrome is installed (required for screenshots).



Usage

Run the Application:
python webcrab.py


Using the GUI:

Location: Select a country (e.g., USA) and optionally enter an area (e.g., New York).
Business Categories: Choose categories (e.g., dentists, restaurants) or select "Search All Categories".
Search Parameters: Specify the number of results per category (default: 3).
Start Search: Click "Start Search" to scrape and analyze websites.
Run Test Query: Click "Run Test Query" to test with a sample query (dentists in USA).
View Results: Results appear in a table. Double-click a row to view the screenshot.
Save Results: Click "Save to CSV" or "Save to Excel" to export results.
Filter Results: Use the filter box to search within results.


Output Files:

Logs: Saved to webcrab.log.
Results: Saved as webcrab_analysis.csv or webcrab_analysis.xlsx.
Screenshots: Saved in the screenshots/ directory.



SerpAPI Key

The application includes a hardcoded SerpAPI key for testing. For production use, replace it with your own key:
Sign up at SerpAPI to get a key.
Update the self.api_key value in webcrab.py:self.api_key = "your-serpapi-key-here"





Troubleshooting

Tkinter ImportError:
On Ubuntu/Debian:sudo apt-get install python3-tk


On macOS (if using Homebrew):brew install python-tk




Selenium ChromeDriver Issues:
Ensure Google Chrome is installed.
Run webdriver-manager to update ChromeDriver:pip install --upgrade webdriver-manager




SerpAPI Errors:
Check webcrab.log for errors like "Invalid API key".
Verify your SerpAPI key and internet connection.


No Results:
Try a more specific query (e.g., "restaurants in New York, USA").
Check webcrab.log for detailed errors.



Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.

Please include tests and update documentation as needed.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact
For issues or questions, open an issue on GitHub .
