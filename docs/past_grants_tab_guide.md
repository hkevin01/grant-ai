# Past Grants Tab - User Guide

## Overview
The new **Past Grants** tab provides a comprehensive interface for tracking and analyzing CODA's historical grant funding. This feature helps organizations maintain a complete record of their funding history and identify patterns for future applications.

## Features

### 1. Summary Statistics Dashboard
- **Total Funding**: Displays total amount received across all grants
- **Grant Count**: Shows number of grants in the database
- **Average Grant Size**: Calculates mean funding amount
- **Color-coded cards** for easy visual scanning

### 2. Advanced Filtering
- **Year Filter**: Filter grants by specific years (2010-present)
- **Funding Type Filter**: 
  - Federal Grant
  - State Grant  
  - Foundation Grant
  - Corporate Sponsorship
  - Private Donation
  - Other
- **Status Filter**:
  - Received
  - In Progress
  - Completed
  - Pending

### 3. Grants History Table
**Columns:**
- **Funder**: Organization providing the grant
- **Amount**: Funding amount with currency formatting
- **Year**: Year grant was received/awarded
- **Type**: Category of funding source
- **Purpose**: Brief description of grant purpose
- **Status**: Current status with color coding
- **Notes**: Additional details and outcomes

**Features:**
- Sortable columns
- Color-coded status indicators
- Alternating row colors for readability
- Responsive column widths

### 4. Add New Grants
- **Add New Past Grant** button for easy data entry
- **Form fields**:
  - Funder name (required)
  - Amount with currency spinner
  - Year selection
  - Type dropdown
  - Purpose description (required)
  - Status selection
  - Notes text area
- **Validation** ensures required fields are completed
- **Success confirmation** after saving

## Sample Data Included

The tab comes pre-loaded with realistic CODA grant history:

1. **WV Department of Education** - $25,000 (2024)
   - State Grant for after-school STEM programs
   - Status: Completed

2. **Appalachian Regional Commission** - $50,000 (2023)
   - Federal Grant for rural arts education initiative
   - Status: Completed

3. **Claude Worthington Benedum Foundation** - $15,000 (2023)
   - Foundation Grant for music education equipment
   - Status: Completed

4. **United Way of Central West Virginia** - $8,000 (2022)
   - Foundation Grant for summer camp scholarships
   - Status: Completed

5. **Local Business Coalition** - $5,000 (2024)
   - Corporate Sponsorship for robotics competition team
   - Status: In Progress

## How to Use

1. **Launch the GUI**: Run `./run.sh gui`
2. **Navigate to Past Grants tab**: Click the "Past Grants" tab
3. **View funding history**: Browse the grants table
4. **Apply filters**: Use dropdowns to focus on specific years, types, or status
5. **Add new grants**: Click "Add New Past Grant" to record new funding
6. **Analyze trends**: Review summary statistics to understand funding patterns

## Benefits

- **Historical Tracking**: Complete record of all received funding
- **Trend Analysis**: Identify successful funding sources and patterns
- **Application Support**: Reference past successes in new applications
- **Reporting**: Generate funding reports for stakeholders
- **Accountability**: Track grant outcomes and completion status

## Future Enhancements

Planned improvements include:
- Export to Excel/PDF functionality
- Advanced analytics and charts
- Integration with application tracking
- Automated grant deadline reminders
- Funder relationship management

## Technical Notes

- Data is currently stored in memory (sample data)
- Production version would connect to database
- Filters update statistics in real-time
- All monetary amounts formatted with currency symbols
- Color coding improves visual scanning efficiency

The Past Grants tab provides CODA with a professional tool for managing their funding history and supporting future grant applications with historical data and success stories.
