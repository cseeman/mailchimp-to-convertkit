# MailChimp to ConvertKit CSV Converter

A Python tool to clean and prepare MailChimp subscriber exports for importing into ConvertKit. This tool handles duplicate detection, tag cleaning, column mapping, and data validation to ensure a smooth migration between email marketing platforms.

## Features

- 🔍 **Analyzes MailChimp exports** - Shows statistics about your subscriber data
- 🧹 **Cleans and formats data** - Removes unnecessary columns and formats tags properly
- 🔄 **Handles duplicates** - Detects and optionally removes duplicate email addresses
- 🏷️ **Smart tag processing** - Cleans quoted tags and handles multiple tag formats
- ✅ **Email validation** - Validates email addresses before processing
- 📊 **Detailed reporting** - Provides statistics on processed and skipped contacts

## Installation

### Prerequisites

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

### Quick Setup

1. Clone this repository:
```bash
git clone https://github.com/cseeman/mailchimp-to-convertkit
cd mailchimp-to-convertkit
```

2. Make the script executable (optional but probably needed):
```bash
chmod +x mailchimp_to_convertkit.py
```

## Usage

### Basic Usage

Convert a MailChimp export to ConvertKit format:

```bash
python3 mailchimp_to_convertkit.py your_mailchimp_export.csv
```

This will create a file named `your_mailchimp_export_convertkit_ready.csv` in the same directory.

### Advanced Options

```bash
# Specify custom output file
python3 mailchimp_to_convertkit.py input.csv -o output.csv

# Keep duplicate emails (by default, duplicates are removed)
python3 mailchimp_to_convertkit.py input.csv --keep-duplicates

# Only analyze without converting
python3 mailchimp_to_convertkit.py input.csv --analyze-only

# Enable verbose output
python3 mailchimp_to_convertkit.py input.csv --verbose
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `input_file` | Path to your MailChimp export CSV file (required) |
| `-o, --output` | Custom output file path |
| `--keep-duplicates` | Don't remove duplicate email addresses |
| `--analyze-only` | Only analyze the file without converting |
| `-v, --verbose` | Show detailed output including all columns |
| `-h, --help` | Show help message |

## What This Tool Does

### 1. Column Mapping

The tool maps MailChimp's export columns to ConvertKit's expected format:

**MailChimp Columns** → **ConvertKit Columns**
- `Email Address` → `Email`
- `First Name` → `First Name`
- `Last Name` → `Last Name`
- `TAGS` → `Tags`

All other MailChimp-specific columns (like MEMBER_RATING, LEID, EUID, etc.) are removed.

### 2. Tag Cleaning

MailChimp often exports tags with quotes and various formatting issues. This tool:
- Removes quotes (single, double, and smart quotes)
- Handles multiple delimiters (commas, semicolons, pipes)
- Normalizes whitespace
- Ensures proper comma-separated format for ConvertKit

**Example:**
- MailChimp: `"Newsletter Subscribers"; "VIP Customers"`
- ConvertKit: `Newsletter Subscribers, VIP Customers`

### 3. Data Validation

- Validates email addresses using regex pattern
- Removes rows with invalid or missing emails
- Preserves special characters in names (like "O'Brien" or "José")
- Handles empty first/last names gracefully

## Example Output

Running the tool will show:

```
============================================================
ANALYZING MAILCHIMP EXPORT
============================================================

📊 Found 25 columns:
   1. First Name
   2. Last Name
   3. Email Address
   4. TAGS
   5. MEMBER_RATING
   ... and 20 more columns

📈 Statistics:
   Total rows: 500
   Valid emails: 495
   Invalid emails: 2
   Unique emails: 490
   Duplicate emails: 5

🏷️ Tags found (8 unique):
   - 'Newsletter': 234 contacts
   - 'Customer': 156 contacts
   - 'VIP': 45 contacts
   ... and 5 more tags

============================================================
CONVERTING TO CONVERTKIT FORMAT
============================================================

✅ Conversion Complete!
   Output file: subscribers_convertkit_ready.csv
   Contacts processed: 490
   Contacts skipped: 10
   Tags cleaned: 389

📝 Import Instructions for ConvertKit:
   1. Log into ConvertKit
   2. Go to Subscribers → Import Subscribers
   3. Upload: subscribers_convertkit_ready.csv
   4. Map columns (should auto-detect)
   5. Choose to update existing subscribers if desired
   6. Review and confirm import
```

## Importing to ConvertKit

1. **Log into ConvertKit** and navigate to the Subscribers section
2. **Click "Import Subscribers"** button
3. **Upload the converted CSV file** created by this tool
4. **Map the columns** - ConvertKit should auto-detect them:
   - Email → Email
   - First Name → First Name
   - Last Name → Last Name
   - Tags → Tags
5. **Choose import options**:
   - Update existing subscribers (recommended)
   - Create tags if they don't exist (automatic)
6. **Review and confirm** the import

## Troubleshooting

### Common Issues

**"Input file not found" error**
- Check that the file path is correct
- Ensure you have read permissions for the file

**Tags not importing correctly**
- Verify tags are comma-separated in the output file
- Check ConvertKit's tag naming restrictions

**Missing subscribers after import**
- Check the skipped count in the tool output
- Review invalid email addresses in verbose mode
- ConvertKit may reject certain email domains

### Getting Help

If you encounter issues:
1. Run with `--verbose` flag for detailed output
2. Check the output CSV manually to verify formatting
3. Ensure your MailChimp export includes standard column names

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development

```bash
# Run the script in development
python3 mailchimp_to_convertkit.py examples/sample_export.csv --verbose

# Run with Python debugger
python3 -m pdb mailchimp_to_convertkit.py examples/sample_export.csv
```

## License

MIT License - see LICENSE file for details

## Author

Created with the goal of making email platform migrations easier for marketers and developers.

## Acknowledgments

- Thanks to the MailChimp and ConvertKit communities
- Inspired by the need for a simple, reliable migration tool
