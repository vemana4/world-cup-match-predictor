# ⚽ FIFA 26 Data Scraper

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org) [![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)

A Streamlit-based web dashboard to collect, process, and export comprehensive statistics for all 48 teams participating in the FIFA 2026 World Cup. Aggregates data from FIFA World Rankings, Wikipedia, and Transfermarkt.

## 🚀 Key Technologies
- **Web Scraping**: BeautifulSoup4, Requests, Trafilatura
- **Data Processing**: Pandas, OpenPyXL (Excel integration), Numpy
- **Caching Layer**: Streamlit @cache_data engine

## 📦 Getting Started & Installation
```bash
# Install dependencies
uv sync

# Run the dashboard
uv run streamlit run app.py
```

## 📜 License
This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
