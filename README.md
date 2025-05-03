# WebCrab

WebCrab is a Python-based GUI application that scrapes small business websites using SerpAPI, analyzes their design quality, and captures screenshots. It allows users to search for businesses by category (e.g., dentists, restaurants) and location, then generates reports on website performance, mobile-friendliness, and modern design practices. Results are displayed in a Tkinter-based interface and can be saved as CSV or Excel files.

## Features

* Search for businesses by category and location using SerpAPI.
* Analyze website design (mobile-friendliness, HTTPS, load time, modern frameworks).
* Capture screenshots of websites using Selenium.
* Filter and display results in a table with double-click support to view screenshots.
* Save results to CSV or Excel files.
* Debug logging to `webcrab.log` for troubleshooting.

## Prerequisites

* **Python**: Version 3.8 or higher.
* **Tkinter**: Included with standard Python installations. Ensure it's available (see Troubleshooting).
* **Google Chrome**: Required for Selenium to take screenshots.
* **SerpAPI Key**: A valid API key for SerpAPI (a hardcoded key is included for testing but should be replaced for production use).
* **Operating System**: Windows, macOS, or Linux.

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/webcrab.git
cd webcrab
```

### Set Up a Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

> Create a `requirements.txt` with the following content:

```plaintext
pandas
requests
beautifulsoup4
selenium
webdriver-manager
google-search-results
openpyxl
```

### Verify Prerequisites

Ensure Python 3.8+ is installed:

```bash
python --version
```

Check Tkinter availability:

```bash
python -c "import tkinter"
```

If this fails, install Tkinter (see Troubleshooting).

Ensure Google Chrome is installed (required for screenshots).

## Usage

### Run the Application

```bash
python webcrab.py
```

### Using the GUI

* **Location**: Select a country (e.g., USA) and optionally enter an area (e.g., New York).
* **Business Categories**: Choose categories (e.g., dentists, restaurants) or select "Search All Categories".
* **Search Parameters**: Specify the number of results per category (default: 3).
* **Start Search**: Click "Start Search" to scrape and analyze websites.
* **Run Test Query**: Click "Run Test Query" to test with a sample query (dentists in USA).
* **View Results**: Results appear in a table. Double-click a row to view the screenshot.
* **Save Results**: Click "Save to CSV" or "Save to Excel" to export results.
* **Filter Results**: Use the filter box to search within results.

### Output Files

* **Logs**: Saved to `webcrab.log`.
* **Results**: Saved as `webcrab_analysis.csv` or `webcrab_analysis.xlsx`.
* **Screenshots**: Saved in the `screenshots/` directory.

## SerpAPI Key

The application includes a hardcoded SerpAPI key for testing. For production use, replace it with your own key:

1. Sign up at [SerpAPI](https://serpapi.com/) to get a key.
2. Update the following line in `webcrab.py`:

```python
self.api_key = "your-serpapi-key-here"
```

> For better security in public repos, use environment variables:

```python
import os
self.api_key = os.getenv("SERPAPI_KEY", "your-default-testing-key")
```

Then set the variable in your terminal:

```bash
export SERPAPI_KEY="your-serpapi-key"  # On Windows: set SERPAPI_KEY=your-serpapi-key
```

## Troubleshooting

### Tkinter ImportError

* **On Ubuntu/Debian**:

  ```bash
  sudo apt-get install python3-tk
  ```
* **On macOS (if using Homebrew)**:

  ```bash
  brew install python-tk
  ```

### Selenium ChromeDriver Issues

* Ensure Google Chrome is installed.
* Run webdriver-manager to update ChromeDriver:

  ```bash
  pip install --upgrade webdriver-manager
  ```

### SerpAPI Errors

* Check `webcrab.log` for errors like "Invalid API key".
* Verify your SerpAPI key and internet connection.

### No Results

* Try a more specific query (e.g., "restaurants in New York, USA").
* Check `webcrab.log` for detailed errors.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit changes:

   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:

   ```bash
   git push origin feature/your-feature
   ```
5. Open a Pull Request.

Please include tests and update documentation as needed.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

### LICENSE

```plaintext
MIT License

Copyright (c) 2025 [your-name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Contact

For issues or questions, open an issue on GitHub 


