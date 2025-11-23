#!/usr/bin/env python3
"""
JSON Streaming Data Quality Validator
Analyzes all JSON batch files for missing/NaN values
"""

import json
import glob
import pandas as pd
from pathlib import Path
import math

# Configuration
STREAMING_DATA_DIR = "/Users/thomasv/Repositories/JADS/01 Data Engineering/DE25-DataJobs-group5/Data/streaming"
CRITICAL_FIELDS = ['watch_duration_minutes', 'progress_percentage']  # Fields critical for analysis

def is_missing(value):
    """Check if a value is missing (None, NaN, empty string)"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    # Check for string "NaN" (common in JSON exports)
    if isinstance(value, str) and value.strip().lower() == "nan":
        return True
    return False

def load_all_json_files(directory):
    """Load all JSON files from directory"""
    json_files = sorted(glob.glob(f"{directory}/*.json"))
    print(f"Found {len(json_files)} JSON files")
    
    all_records = []
    file_stats = {}
    
    for json_file in json_files:
        filename = Path(json_file).name
        try:
            with open(json_file, 'r') as f:
                records = [json.loads(line.strip()) for line in f if line.strip()]
                all_records.extend(records)
                file_stats[filename] = len(records)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return all_records, file_stats

def analyze_missing_values(records):
    """Analyze missing values across all fields"""
    if not records:
        print("No records found!")
        return
    
    total_records = len(records)
    all_fields = records[0].keys()
    
    field_stats = {}
    
    for field in all_fields:
        missing_count = sum(1 for record in records if is_missing(record.get(field)))
        field_stats[field] = {
            'missing_count': missing_count,
            'missing_pct': (missing_count / total_records) * 100,
            'present_count': total_records - missing_count
        }
    
    return field_stats, total_records

def find_problematic_records(records, num_samples=10):
    """Find sample records with missing critical fields"""
    problematic = []
    
    for record in records:
        issues = []
        for field in CRITICAL_FIELDS:
            if is_missing(record.get(field)):
                issues.append(field)
        
        if issues:
            problematic.append({
                'session_id': record.get('session_id', 'unknown'),
                'timestamp': record.get('timestamp', 'unknown'),
                'missing_fields': ', '.join(issues),
                'record': record
            })
            
            if len(problematic) >= num_samples:
                break
    
    return problematic

def main():
    print("=" * 80)
    print("JSON STREAMING DATA QUALITY ANALYSIS")
    print("=" * 80)
    print(f"Source directory: {STREAMING_DATA_DIR}\n")
    
    # Load all JSON files
    print("Loading JSON files...")
    records, file_stats = load_all_json_files(STREAMING_DATA_DIR)
    
    print(f"\n📊 FILE SUMMARY:")
    print(f"  Total files: {len(file_stats)}")
    print(f"  Total records: {len(records):,}")
    print(f"  Avg records per file: {len(records) / len(file_stats):.1f}")
    
    # Analyze missing values
    print("\n" + "=" * 80)
    print("MISSING VALUE ANALYSIS")
    print("=" * 80)
    
    field_stats, total_records = analyze_missing_values(records)
    
    # Sort by missing percentage (highest first)
    sorted_fields = sorted(field_stats.items(), key=lambda x: x[1]['missing_pct'], reverse=True)
    
    print(f"\n{'Field':<30} {'Missing':<12} {'Present':<12} {'Missing %':<12}")
    print("-" * 80)
    
    for field, stats in sorted_fields:
        missing_pct_str = f"{stats['missing_pct']:.2f}%"
        print(f"{field:<30} {stats['missing_count']:<12} {stats['present_count']:<12} {missing_pct_str:<12}")
    
    # Critical fields analysis
    print("\n" + "=" * 80)
    print("🚨 CRITICAL FIELDS ANALYSIS")
    print("=" * 80)
    
    for field in CRITICAL_FIELDS:
        stats = field_stats[field]
        status = "❌ HIGH RISK" if stats['missing_pct'] > 10 else "⚠️  MODERATE" if stats['missing_pct'] > 1 else "✅ HEALTHY"
        print(f"\n{field}:")
        print(f"  Status: {status}")
        print(f"  Missing: {stats['missing_count']:,} ({stats['missing_pct']:.2f}%)")
        print(f"  Present: {stats['present_count']:,} ({100-stats['missing_pct']:.2f}%)")
    
    # Find problematic records
    print("\n" + "=" * 80)
    print("SAMPLE PROBLEMATIC RECORDS")
    print("=" * 80)
    
    problematic = find_problematic_records(records, num_samples=10)
    
    if problematic:
        print(f"\nFound {len(problematic)} sample records with missing critical fields:\n")
        for i, issue in enumerate(problematic[:5], 1):
            print(f"{i}. Session: {issue['session_id']}")
            print(f"   Timestamp: {issue['timestamp']}")
            print(f"   Missing: {issue['missing_fields']}")
            print(f"   Watch duration: {issue['record'].get('watch_duration_minutes')}")
            print(f"   Progress %: {issue['record'].get('progress_percentage')}")
            print()
    else:
        print("\n✅ No problematic records found!")
    
    # Impact assessment
    print("=" * 80)
    print("IMPACT ASSESSMENT")
    print("=" * 80)
    
    records_with_any_issue = sum(
        1 for record in records 
        if any(is_missing(record.get(field)) for field in CRITICAL_FIELDS)
    )
    
    impact_pct = (records_with_any_issue / total_records) * 100
    
    print(f"\n📊 Records with at least one critical field missing:")
    print(f"   Count: {records_with_any_issue:,}")
    print(f"   Percentage: {impact_pct:.2f}%")
    print(f"   Clean records: {total_records - records_with_any_issue:,} ({100-impact_pct:.2f}%)")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    if impact_pct > 10:
        print("\n❌ HIGH IMPACT - Immediate action required:")
        print("  1. Fix JSON generation script to prevent NaN values")
        print("  2. Update Spark pipeline to handle NaN explicitly (use isnan() function)")
        print("  3. Consider regenerating JSON batches with cleaned data")
    elif impact_pct > 1:
        print("\n⚠️  MODERATE IMPACT - Action recommended:")
        print("  1. Update Spark pipeline to handle NaN explicitly")
        print("  2. Monitor data quality in future batches")
    else:
        print("\n✅ LOW IMPACT - Data quality is good:")
        print("  1. Minor pipeline updates may still be beneficial")
        print("  2. Continue monitoring data quality")
    
    print("\n" + "=" * 80)
    print(f"Analysis complete! Checked {total_records:,} records across {len(file_stats)} files.")
    print("=" * 80)

if __name__ == "__main__":
    main()