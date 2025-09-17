#!/usr/bin/env python3
"""
Script to add age group dummy variables to the synthetic population data.
New variables:
- cAgeGroup30To44, cAgeGroup45To64, cAgeGroup65Plus based on cAge
- mAgeGroup30To44, mAgeGroup45To64, mAgeGroup65Plus based on mAge
"""

import pandas as pd
import os
import sys

def add_age_group_dummies(input_file, output_file):
    """
    Add age group dummy variables to the dataset.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    print(f"Reading data from {input_file}")
    # Read the data
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Original data shape: {df.shape}")
    
    # Create cAge group dummies
    print("Creating cAge group dummies...")
    df['cAgeGroup30To44'] = ((df['cAge'] >= 30) & (df['cAge'] < 45)).astype(int)
    df['cAgeGroup45To64'] = ((df['cAge'] >= 45) & (df['cAge'] < 65)).astype(int)
    df['cAgeGroup65Plus'] = (df['cAge'] >= 65).astype(int)
    
    # Create mAge group dummies
    print("Creating mAge group dummies...")
    df['mAgeGroup30To44'] = ((df['mAge'] >= 30) & (df['mAge'] < 45)).astype(int)
    df['mAgeGroup45To64'] = ((df['mAge'] >= 45) & (df['mAge'] < 65)).astype(int)
    df['mAgeGroup65Plus'] = (df['mAge'] >= 65).astype(int)
    
    # Save to new file
    print(f"Saving processed data to {output_file}")
    df.to_csv(output_file, index=False)
    
    print("Summary of newly added columns:")
    for col in ['cAgeGroup30To44', 'cAgeGroup45To64', 'cAgeGroup65Plus',
                'mAgeGroup30To44', 'mAgeGroup45To64', 'mAgeGroup65Plus']:
        print(f"{col}: {df[col].sum()} agents in this group")
    
    print(f"Final data shape: {df.shape}")
    print("Processing complete!")

if __name__ == "__main__":
    # Set file paths
    base_dir = "/home/shang/smoking/smokingABM/data"
    input_file = os.path.join(base_dir, "data_synth_network_testing.csv")
    output_file = os.path.join(base_dir, "data_synth_network_testing_with_agegroup.csv")
    
    # Run processing
    add_age_group_dummies(input_file, output_file) 