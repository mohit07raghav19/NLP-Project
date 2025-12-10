# CVE Analyzer - Advanced Dashboard

A modern, feature-rich web interface for analyzing CVE (Common Vulnerabilities and Exposures) data.

## Features Implemented

### 1. Advanced Filtering & Sorting ✅
- **Multi-select severity filter** - Select multiple severity levels at once
- **CVSS range filter** - Filter by min/max CVSS scores
- **Date range picker** - Filter CVEs by publication date
- **Sort options** - Sort by date, CVSS score, or CVE ID (ascending/descending)
- **Active filters display** - See all active filters at a glance with easy removal
- **Per-page selection** - Choose 10, 20, 50, or 100 results per page

### 2. Data Visualizations ✅
- **Severity Distribution Chart** - Doughnut chart showing CVE breakdown by severity
- **CVSS Score Distribution** - Bar chart showing score ranges
- **Top 10 Affected Vendors** - Horizontal bar chart of most affected vendors
- **Theme-aware charts** - Charts automatically adapt to light/dark mode

### 3. Enhanced Search ✅
- **Debounced search** - Search triggers after 500ms of inactivity
- **Search term highlighting** - Results highlight matching terms with `<mark>` tags
- **Minimum 3 characters** - Validation for search queries
- **Search in active filters** - Search results can be further filtered

### 4. Export Functionality ✅
- **Export to CSV** - Download CVE data in CSV format
- **Export to JSON** - Download CVE data in JSON format
- **Export filtered results** - Export only what you see
- **Export single CVE** - Export individual CVEs from detail view
- **Toast notifications** - Confirmation messages for exports

### 5. Dark Mode ✅
- **Toggle button** - Easy theme switching in header
- **Persistent preference** - Theme saved to localStorage
- **Smooth transitions** - 300ms ease animations
- **Complete color scheme** - All UI elements support both themes
- **Chart theme adaptation** - Charts redraw when theme changes

### 6. Performance Optimizations ✅
- **API response caching** - 5-minute TTL for faster navigation
- **Debounced search** - Prevents excessive API calls
- **Client-side filtering** - Fast filtering without API calls
- **Lazy chart rendering** - Charts only render when Analytics tab is active
- **Optimized animations** - Respects `prefers-reduced-motion`

### 7. Enhanced CVE Cards ✅
- **Vendor tags** - Display up to 3 affected vendors on cards
- **Copy CVE ID button** - Quick copy to clipboard
- **Color-coded severity** - Left border indicates severity level
- **Quick actions** - Copy and export buttons
- **Smooth hover effects** - Subtle animations on interaction

### 8. Additional Data Displays ✅
- **Three-tab interface** - Dashboard, CVE List, Analytics
- **Statistics dashboard** - Overview cards with tooltips
- **Quick actions** - Jump to different sections easily
- **Detailed modal view** - Full CVE information in modal
- **Affected vendors/products** - Complete lists in detail view

### 9. Accessibility & Mobile ✅
- **Responsive design** - Works on all screen sizes
- **Keyboard shortcuts** - ESC to close modal, Enter to search
- **ARIA-compliant** - Semantic HTML and proper labeling
- **Tooltips** - Hover hints on stat cards
- **Touch-friendly** - Larger click targets on mobile
- **Reduced motion support** - Respects user preferences
- **Print-friendly** - Clean print styles

### 10. Real-time Features ✅
- **Auto-refresh** - Data refreshes every 60 seconds
- **Health status indicator** - Real-time connection status
- **Toast notifications** - Non-intrusive success/error messages
- **Manual refresh button** - Force refresh with animated icon
- **Loading states** - Clear feedback during data fetching

## Technologies Used

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS variables
- **Vanilla JavaScript** - No framework dependencies
- **Chart.js 4.4.0** - Data visualizations
- **LocalStorage** - Theme and preference persistence

## How to Run

### Option 1: Simple HTTP Server
```bash
cd frontend
python -m http.server 3000
```
Then open `http://localhost:3000`

### Option 2: Direct File Open
Simply open `index.html` in your browser (some features may be limited)

### Prerequisites
- Backend API running on `http://localhost:8000`
- Modern browser with ES6 support

## Project Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling (light + dark mode)
├── app.js          # All JavaScript functionality
└── README.md       # This file
```

## Key Features Breakdown

### Dashboard Tab
- 6 statistics cards (Total, Critical, High, Medium, Low, Avg CVSS)
- Quick action buttons
- Responsive grid layout

### CVE List Tab
- Advanced search bar
- Multi-filter interface
- Active filters display
- CVE cards with vendor tags
- Pagination controls

### Analytics Tab
- Severity distribution (doughnut chart)
- CVSS score distribution (bar chart)
- Top 10 vendors (horizontal bar chart)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Performance

- Initial load: < 1 second
- Search debounce: 500ms
- Cache TTL: 5 minutes
- Auto-refresh: 60 seconds

## Keyboard Shortcuts

- `ESC` - Close modal
- `Enter` - Submit search
- `Tab` - Navigate through interface

## Future Enhancements (Not Implemented)

- Infinite scroll
- Virtual scrolling for large lists
- Advanced search operators (AND, OR, NOT)
- PDF export
- Bookmark/favorite CVEs
- WebSocket for real-time updates
- Voice search

## License

MIT License - Feel free to use and modify!

## Author

Created with Claude Code
