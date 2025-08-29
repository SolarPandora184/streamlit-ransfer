# Airshow POS System

## Overview

The Airshow Point of Sale System is a Streamlit-based web application designed for managing sales operations at airshow events. The system provides comprehensive functionality for inventory management, sales transactions, customer tracking, and data export capabilities. It uses Firebase Realtime Database as the backend data storage solution and features a multi-page interface for different operational needs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web-based user interface
- **Multi-page Structure**: Modular design with separate pages for different functions
- **Navigation**: Sidebar-based navigation system with page selection
- **Session Management**: Streamlit session state for cart management and authentication

### Backend Architecture
- **Database**: Firebase Realtime Database for real-time data synchronization
- **Data Structure**: NoSQL document-based storage with organized collections for inventory, sales, and tracking data
- **Authentication**: Simple password-based admin authentication for inventory management
- **Data Operations**: CRUD operations through Firebase SDK with error handling

### Core Components
- **Sales Interface**: Shopping cart functionality with real-time inventory checking
- **Inventory Management**: Admin-protected CRUD operations for product catalog
- **Turned Away Tracker**: Customer interaction logging for business intelligence
- **Export Manager**: Data export functionality with date filtering and Excel output

### Security Model
- Environment variable-based Firebase configuration
- Admin password protection for sensitive operations
- Input validation and sanitization utilities
- Error handling with user-friendly messages

### Data Flow
- Real-time inventory updates during sales transactions
- Centralized Firebase configuration with connection pooling
- Modular utility functions for data formatting and validation
- Session-based cart management with persistence

## External Dependencies

### Cloud Services
- **Firebase**: Google's Firebase Realtime Database for data storage and synchronization
- **Firebase Admin SDK**: Server-side Firebase integration for secure data operations

### Python Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis for export functionality
- **UUID**: Unique identifier generation for transactions and inventory items
- **JSON**: Configuration parsing for Firebase credentials

### Environment Variables
- **FIREBASE_SERVICE_ACCOUNT_KEY**: JSON credentials for Firebase authentication
- **FIREBASE_DATABASE_URL**: Firebase project database endpoint URL

### Data Export
- **Excel Integration**: Pandas-based Excel file generation for data exports
- **Date Range Filtering**: Time-based data filtering for export operations