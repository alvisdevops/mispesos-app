# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal financial management system called "mispesos-app" designed to automate expense tracking through a Telegram bot with a web dashboard for visualization. The system is intended to run on an old PC at home with local data storage.

## System Architecture

The project consists of three main components:

1. **Telegram Bot** - Captures expenses and receipts through natural language and OCR
2. **Home Server** - Processes data, handles OCR, and serves APIs (using an old PC at home)
3. **Web Application** - Provides dashboard and detailed financial analysis

### Technology Stack (As Planned)

**Backend (Home Server):**
- Python 3.11+ with FastAPI
- SQLite database for local storage
- Tesseract OCR for receipt processing
- python-telegram-bot library
- Docker + Docker Compose for containerization

**Frontend (Web App):**
- React.js with Tailwind CSS
- REST API communication with Pi server
- Hosted on Namecheap shared hosting

## Database Schema

The system uses SQLite with the following key tables:

- `transactions` - Main financial transactions
- `receipts` - OCR processed receipts with metadata  
- `categories` - Expense categories with auto-classification
- `category_keywords` - Keywords for automatic categorization

## Key Features

### Telegram Bot Capabilities
- Natural language expense parsing (e.g., "50k almuerzo tarjeta")
- OCR processing of receipt photos
- Commands: `/resumen`, `/categorias`, `/balance`, `/corregir`, `/ayuda`
- Real-time transaction confirmation

### Web Dashboard
- Executive dashboard with KPIs and trend graphs
- Detailed transaction view (Excel-like interface)  
- Fiscal module for tax documentation
- Advanced filtering, search, and export capabilities

## Development Status

This appears to be a fresh repository with only specifications documented. The actual implementation has not yet begun - only the `financial_bot_specs.md` specification file exists.

## Development Approach

When implementing this system:

1. Start with Phase 1 MVP (basic bot + SQLite)
2. Add OCR processing and web dashboard (Phase 2)
3. Implement advanced categorization and reporting (Phase 3)
4. Deploy and optimize for home PC server (Phase 4)

## Security Considerations

- All financial data stays on local infrastructure (home PC + personal hosting)
- Telegram User ID authentication required
- Data encryption for sensitive information
- No third-party services for financial data processing

## Deployment Target

The system is designed to run on:
- Old PC at home as the main server
- Cloudflare tunnel for external access
- Local SQLite database (no cloud dependencies)
- Personal Namecheap hosting for web frontend