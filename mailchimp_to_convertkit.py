#!/usr/bin/env python3
"""
MailChimp to ConvertKit CSV Converter

A tool to clean and prepare MailChimp subscriber exports for importing into ConvertKit.
Handles duplicate detection, tag cleaning, and column mapping.
"""

import csv
import re
import argparse
import sys
from pathlib import Path
from collections import Counter


class MailChimpToConvertKit:
    """Converter class for processing MailChimp exports to ConvertKit format."""
    
    def __init__(self, input_file, output_file=None, verbose=False):
        """Initialize the converter.
        
        Args:
            input_file: Path to the MailChimp export CSV
            output_file: Path for the cleaned output CSV (optional)
            verbose: Enable verbose output
        """
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        if output_file:
            self.output_file = Path(output_file)
        else:
            # Generate output filename based on input
            stem = self.input_file.stem
            self.output_file = self.input_file.parent / f"{stem}_convertkit_ready.csv"
            
        self.verbose = verbose
        self.stats = {
            'total_rows': 0,
            'processed': 0,
            'skipped': 0,
            'duplicates': 0,
            'invalid_emails': 0,
            'tags_cleaned': 0
        }
        
    def clean_tags(self, tag_string):
        """Clean and format tags for ConvertKit import.
        
        Args:
            tag_string: Raw tag string from MailChimp export
            
        Returns:
            Cleaned tag string suitable for ConvertKit
        """
        if not tag_string:
            return ''
        
        # Remove leading/trailing whitespace
        tag_string = tag_string.strip()
        
        # Remove various quote styles that MailChimp might use
        # This handles single quotes, double quotes, and smart quotes
        quotes_to_remove = ['"', "'", '"', '"', ''', ''']
        for quote in quotes_to_remove:
            tag_string = tag_string.replace(quote, '')
        
        # Split by various delimiters (comma, semicolon, pipe)
        tags = re.split('[,;|]', tag_string)
        
        # Clean each tag individually
        cleaned_tags = []
        for tag in tags:
            # Remove extra whitespace and normalize
            cleaned_tag = ' '.join(tag.split())
            # Only add non-empty tags
            if cleaned_tag:
                cleaned_tags.append(cleaned_tag)
        
        if cleaned_tags:
            self.stats['tags_cleaned'] += 1
            
        # Join with ConvertKit's expected format (comma + space)
        return ', '.join(cleaned_tags)
    
    def clean_name(self, name):
        """Clean name fields while preserving legitimate special characters.
        
        Args:
            name: Raw name string
            
        Returns:
            Cleaned name string
        """
        if not name:
            return ''
        
        # Remove excessive whitespace but keep the name as-is otherwise
        return ' '.join(name.split())
    
    def validate_email(self, email):
        """Basic email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            Boolean indicating if email is valid
        """
        if not email:
            return False
            
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    def analyze_input(self):
        """Analyze the input file and return statistics."""
        print("\n" + "="*60)
        print("ANALYZING MAILCHIMP EXPORT")
        print("="*60)
        
        emails_seen = []
        tags_counter = Counter()
        
        with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            
            print(f"\n📊 Found {len(headers)} columns:")
            if self.verbose:
                for i, header in enumerate(headers, 1):
                    print(f"   {i:2}. {header}")
            else:
                # Show first 5 columns
                for i, header in enumerate(headers[:5], 1):
                    print(f"   {i:2}. {header}")
                if len(headers) > 5:
                    print(f"   ... and {len(headers) - 5} more columns")
            
            # Analyze data
            for row in reader:
                self.stats['total_rows'] += 1
                email = row.get('Email Address', '').strip().lower()
                
                if email and self.validate_email(email):
                    emails_seen.append(email)
                    
                    # Count tags
                    tags = row.get('TAGS', '').strip()
                    if tags:
                        cleaned = self.clean_tags(tags)
                        for tag in cleaned.split(', '):
                            if tag:
                                tags_counter[tag] += 1
                elif email:
                    self.stats['invalid_emails'] += 1
        
        # Check for duplicates
        email_counts = Counter(emails_seen)
        duplicates = {email: count for email, count in email_counts.items() if count > 1}
        self.stats['duplicates'] = len(duplicates)
        
        print(f"\n📈 Statistics:")
        print(f"   Total rows: {self.stats['total_rows']}")
        print(f"   Valid emails: {len(emails_seen)}")
        print(f"   Invalid emails: {self.stats['invalid_emails']}")
        print(f"   Unique emails: {len(email_counts)}")
        print(f"   Duplicate emails: {self.stats['duplicates']}")
        
        if tags_counter:
            print(f"\n🏷️  Tags found ({len(tags_counter)} unique):")
            for tag, count in tags_counter.most_common(5):
                print(f"   - '{tag}': {count} contacts")
            if len(tags_counter) > 5:
                print(f"   ... and {len(tags_counter) - 5} more tags")
        
        return self.stats
    
    def convert(self, remove_duplicates=True):
        """Convert the MailChimp export to ConvertKit format.
        
        Args:
            remove_duplicates: If True, skip duplicate email addresses
            
        Returns:
            Path to the output file
        """
        print("\n" + "="*60)
        print("CONVERTING TO CONVERTKIT FORMAT")
        print("="*60)
        
        emails_processed = set()
        
        with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as infile:
            reader = csv.DictReader(infile)
            
            # Check which columns are available
            available_columns = reader.fieldnames
            
            # Map MailChimp columns to ConvertKit columns
            column_mapping = {
                'Email': 'Email Address',
                'First Name': 'First Name',
                'Last Name': 'Last Name',
                'Tags': 'TAGS'
            }
            
            # Check for alternative column names
            if 'Email' in available_columns:
                column_mapping['Email'] = 'Email'
            if 'Tags' in available_columns:
                column_mapping['Tags'] = 'Tags'
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                # ConvertKit expected columns
                fieldnames = ['Email', 'First Name', 'Last Name', 'Tags']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    email = row.get(column_mapping['Email'], '').strip()
                    
                    # Skip invalid emails
                    if not email or not self.validate_email(email):
                        self.stats['skipped'] += 1
                        continue
                    
                    # Handle duplicates
                    email_lower = email.lower()
                    if remove_duplicates and email_lower in emails_processed:
                        self.stats['skipped'] += 1
                        continue
                    
                    emails_processed.add(email_lower)
                    
                    # Create cleaned row
                    clean_row = {
                        'Email': email,
                        'First Name': self.clean_name(row.get(column_mapping['First Name'], '')),
                        'Last Name': self.clean_name(row.get(column_mapping['Last Name'], '')),
                        'Tags': self.clean_tags(row.get(column_mapping['Tags'], ''))
                    }
                    
                    writer.writerow(clean_row)
                    self.stats['processed'] += 1
        
        print(f"\n✅ Conversion Complete!")
        print(f"   Output file: {self.output_file}")
        print(f"   Contacts processed: {self.stats['processed']}")
        print(f"   Contacts skipped: {self.stats['skipped']}")
        print(f"   Tags cleaned: {self.stats['tags_cleaned']}")
        
        return self.output_file


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert MailChimp subscriber exports to ConvertKit format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s subscribers.csv
  %(prog)s subscribers.csv -o cleaned.csv
  %(prog)s subscribers.csv --keep-duplicates --verbose
  %(prog)s subscribers.csv --analyze-only
        """
    )
    
    parser.add_argument('input_file', 
                       help='Path to MailChimp export CSV file')
    parser.add_argument('-o', '--output', 
                       help='Output file path (default: input_convertkit_ready.csv)')
    parser.add_argument('--keep-duplicates', 
                       action='store_true',
                       help='Keep duplicate email addresses')
    parser.add_argument('--analyze-only', 
                       action='store_true',
                       help='Only analyze the input file without converting')
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        converter = MailChimpToConvertKit(
            args.input_file,
            args.output,
            args.verbose
        )
        
        # Always analyze first
        converter.analyze_input()
        
        # Convert unless analyze-only mode
        if not args.analyze_only:
            output_file = converter.convert(
                remove_duplicates=not args.keep_duplicates
            )
            
            print("\n📝 Import Instructions for ConvertKit:")
            print("   1. Log into ConvertKit")
            print("   2. Go to Subscribers → Import Subscribers")
            print(f"   3. Upload: {output_file.name}")
            print("   4. Map columns (should auto-detect)")
            print("   5. Choose to update existing subscribers if desired")
            print("   6. Review and confirm import")
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()