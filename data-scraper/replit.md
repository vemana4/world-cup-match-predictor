# FIFA 26 World Cup Data Scraper

## Overview

This is a Streamlit-based web application designed to scrape and aggregate comprehensive data for all 48 teams participating in the FIFA 26 World Cup. The application collects 100+ features per team from multiple data sources including FIFA official rankings, Transfermarkt player valuations, and football statistics databases. The collected data can be exported to CSV and Excel formats with organized categorization for analysis and machine learning purposes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web UI
- **Design Pattern**: Single-page application with cached data loading
- **Key Features**:
  - Real-time progress tracking during data scraping
  - Session state management for scraping status
  - Sidebar controls for data collection triggers
  - Wide layout configuration for data visualization

### Backend Architecture
- **Core Components**:
  - `FIFA26DataCollector`: Orchestrates data collection from multiple scrapers
  - `ExportHandler`: Manages data export to CSV and Excel formats
  - Modular scraper system with three specialized scrapers

- **Scraper Architecture**:
  - `FIFAScraper`: Fetches FIFA world rankings and points with fallback mechanisms
  - `TransfermarktScraper`: Collects squad data (player ages, market values, league distributions)
  - `FootballDataScraper`: Gathers match statistics and tactical performance metrics

- **Data Model**: 48 teams with 100+ features organized into categories:
  - Team Performance & Results (15 features)
  - Match & Tactical Stats (35+ features)
  - Squad composition metrics
  - Continental confederation mapping

### Data Storage Solutions
- **File-based Storage**: No database used
- **Export Formats**:
  - CSV: Single file with all team data
  - Excel: Multi-sheet workbook with categorized data views
- **Cache Strategy**: CSV-based caching via Streamlit's `@st.cache_data` decorator
- **Directory Structure**: `exports/` folder for all generated files

### External Dependencies

**Web Scraping Libraries**:
- `requests`: HTTP client for API calls and web requests
- `BeautifulSoup4`: HTML parsing for FIFA and Transfermarkt websites

**Data Processing**:
- `pandas`: Primary data structure and manipulation library
- `numpy`: Numerical computations and data generation
- `openpyxl`: Excel file creation with styling support

**Web Framework**:
- `streamlit`: Complete UI framework and application server

**Third-Party Data Sources**:
- FIFA.com: Official world rankings and team points
- Transfermarkt.com: Player market values and squad statistics  
- Football statistics databases: Match performance and tactical data

**Key Integration Points**:
- Real-time web scraping with timeout protection (10s)
- User-Agent headers for web request compatibility
- Fallback data mechanisms when live scraping fails
- Progress callback system for UI updates during collection