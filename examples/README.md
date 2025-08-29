# Example Files

This directory contains sample CSV files for testing the MailChimp to ConvertKit converter.

## Files

### `sample_mailchimp_export.csv`
A sample MailChimp export file that demonstrates various data scenarios:
- Normal contacts with all fields filled
- Contacts with missing first names
- Contacts with special characters in names (O'Connor, Mary Jane, Sarah & Mike)
- Various tag formats (quoted, multiple tags)
- Invalid email addresses
- Empty tag fields

## Testing the Tool

Use the sample file to test the converter:

```bash
# From the main directory
python3 mailchimp_to_convertkit.py examples/sample_mailchimp_export.csv --verbose

# Or analyze only
python3 mailchimp_to_convertkit.py examples/sample_mailchimp_export.csv --analyze-only
```

## Expected Results

When processing the sample file, you should see:
- 10 total rows processed
- 1 invalid email detected (`invalid.email.com`)
- Various tag cleaning operations
- Output file with clean ConvertKit format

This helps verify the tool is working correctly before processing your actual subscriber data.