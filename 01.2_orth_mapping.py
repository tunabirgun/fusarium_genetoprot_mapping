#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
import re

# Set the base directory with appropriate subfolder structure
BASE_DIR = Path(".")
INPUT_DIR = BASE_DIR / "input_data"       # Where input XLSX files are located
STRING_DIR = BASE_DIR / "string_data"     # Where STRING database files are located
OUTPUT_DIR = BASE_DIR / "mapped_data"     # Where output files will be saved

# Set specific organisms to map and version of the STRING database
ORTHOLOG_CONFIG = {
    "F_pseudograminearum_to_F_graminearum": {
        "file_pattern": "^6_",          # Files starting with "6_" (Study 6)
        "source_prefix": "FPSE",        # The genes in your Excel file (e.g., FPSE_12345)
        "target_prefix": "FGSG",        # The genes in STRING (e.g., FGSG_12345)
        "target_taxid": "229533",       # Taxonomy ID of the TARGET (F. graminearum)
    }
}
STRING_VERSION = "12.0"

# Define the necessary functions
## Load STRING allias
def load_target_aliases(alias_file, target_prefix):
    target_map = {}
    print(f"Loading target aliases from: {alias_file.name}...")

    pattern = re.compile(f"^{target_prefix}_\\d+$", re.IGNORECASE)

    with open(alias_file, 'r') as f:
        next(f)                           # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                string_id = parts[0]
                alias = parts[1].upper()
                if pattern.match(alias):
                    target_map[alias] = string_id

    print(f"  Found {len(target_map)} valid {target_prefix} genes in STRING database.")
    return target_map

## Create the orthology mapping from source to target genes
def create_ortholog_map(target_map, source_prefix, target_prefix):
    ortholog_map = {}

    # Build regex pattern to extract numeric part
    target_pattern = re.compile(f"^{target_prefix}_(\\d+)$", re.IGNORECASE)
    count = 0
    for target_gene, string_id in target_map.items():
        match = target_pattern.match(target_gene)
        if match:
            number_part = match.group(1)
            
            # Construct the corresponding source gene name
            source_gene = f"{source_prefix}_{number_part}"
            
            # Add to map: FPSE_00001 -> STRING_ID_OF_FGSG_00001
            ortholog_map[source_gene] = string_id
            count += 1

    print(f"  Created ortholog map with {count} entries from {source_prefix} to {target_prefix}.")
    return ortholog_map

## Read input XLSX files and apply the orthology mapping
def process_file(file_path, ortholog_map):
    print(f"Processing: {file_path.name}")
    
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.lower().str.strip()
        
        if 'gene' not in df.columns:
            print(f"  Skipping: No 'gene' column found in {file_path.name}")
            return None

        df['gene'] = df['gene'].astype(str).str.upper().str.strip()

        # Map the genes using orthology strategy
        df['string_id'] = df['gene'].map(ortholog_map)
        
        # Calculate stats
        mapped = df['string_id'].notna().sum()
        total = len(df)
        percentage = (mapped/total*100) if total > 0 else 0
        print(f"  Mapped {mapped} out of {total} genes ({percentage:.1f}%)")
        
        # Save result
        output_file = OUTPUT_DIR / f"mapped_ortholog_{file_path.stem}.tsv"
        df.to_csv(output_file, sep='\t', index=False)
        print(f"  Saved to: {output_file}")
        
        return {'file': file_path.name, 'mapped': mapped, 'total': total}
        
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return None


# Execute the mapping process by looping through species and files
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"INPUT_DIR exists: {INPUT_DIR.exists()}")
    print(f"STRING_DIR exists: {STRING_DIR.exists()}")
    print(f"OUTPUT_DIR exists: {OUTPUT_DIR.exists()}\n")
    
    ortholog_stats = {}  # Track stats per ortholog mapping
    
    for name, config in ORTHOLOG_CONFIG.items():
        print(f"--- Starting Ortholog Mapping: {name} ---")
        
        # 1. Load the TARGET alias file (e.g., F. graminearum / 229533)
        alias_path = STRING_DIR / f"{config['target_taxid']}.protein.aliases.v{STRING_VERSION}.txt"
        
        if not alias_path.exists():
            print(f"Error: Target alias file not found ({alias_path})")
            continue
            
        # 2. Load valid target genes (FGSG_...)
        target_map = load_target_aliases(alias_path, config['target_prefix'])
        
        if not target_map:
            print(f"  Error: No genes loaded from alias file. Skipping this mapping.")
            continue
        
        # 3. Create the inferred map (FPSE_... -> STRING ID)
        final_map = create_ortholog_map(target_map, config['source_prefix'], config['target_prefix'])
        
        if not final_map:
            print(f"  Error: Ortholog map is empty. Skipping this mapping.")
            continue
        
        ortholog_stats[name] = []  # Initialize list for this ortholog mapping
        
        # 4. Process matching files
        found_files = False
        for file_path in INPUT_DIR.glob("*.xlsx"):
            if re.search(config['file_pattern'], file_path.name):
                result = process_file(file_path, final_map)
                if result:
                    ortholog_stats[name].append(result)
                    found_files = True
                
        if not found_files:
            print(f"  Warning: No files found matching pattern '{config['file_pattern']}'")
        print()

    # Print summary by ortholog mapping and total
    if ortholog_stats:
        print("=" * 70)
        print("SUMMARY BY STUDY")
        print("=" * 70)
        
        grand_total_mapped = 0
        grand_total_genes = 0
        
        for name, stats in ortholog_stats.items():
            if stats:
                mapping_mapped = sum(s['mapped'] for s in stats)
                mapping_total = sum(s['total'] for s in stats)
                mapping_percent = (mapping_mapped/mapping_total*100) if mapping_total > 0 else 0
                print(f"\n{name}:")
                print(f"  Files processed: {len(stats)}")
                print(f"  Genes mapped: {mapping_mapped} out of {mapping_total} ({mapping_percent:.1f}%)")
                grand_total_mapped += mapping_mapped
                grand_total_genes += mapping_total
        
        print(f"\n{'-' * 70}")
        print("TOTAL:")
        grand_percent = (grand_total_mapped/grand_total_genes*100) if grand_total_genes > 0 else 0
        print(f"  Files processed: {sum(len(s) for s in ortholog_stats.values())}")
        print(f"  Genes mapped: {grand_total_mapped} out of {grand_total_genes} ({grand_percent:.1f}%)")
        print("=" * 70)
    
    print(f"\nDone! Ortholog mapped files are in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
