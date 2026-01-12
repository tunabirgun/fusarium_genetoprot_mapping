#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
from collections import defaultdict
import re

# Set the base directory with appropriate subfolder structure
BASE_DIR = Path("/mnt/c/Users/Tuna/Desktop/test")  # Windows path
INPUT_DIR = BASE_DIR / "input_data"       # Where input XLSX files are located
STRING_DIR = BASE_DIR / "string_data"     # Where STRING database files are located
OUTPUT_DIR = BASE_DIR / "mapped_data"     # Where output files will be saved

# Set specific organisms to map and version of the STRING database
SPECIES_CONFIG = {
    "F_graminearum": {
        "taxid": "229533",                # STRING Taxonomy ID
        "prefix": "FGSG",                 # Gene ID prefix (e.g., FGSG_00001)
        "file_pattern": "^[12]_"          # Regex to match filenames for this species
    },
    "F_oxysporum": {
        "taxid": "426428",
        "prefix": "FOXG",
        "file_pattern": "^[34578]_"
    }
}
STRING_VERSION = "12.0"


# Define the necessary functions
## Load STRING allias
def load_string_aliases(alias_file):
    alias_map = {}
    print(f"Loading aliases from: {alias_file.name}...")
    
    with open(alias_file, 'r') as f:
        next(f)                           # Skip header
        for line in f:
            parts = line.strip().split('\t')
            # Map alias (col 1) to Protein ID (col 0)
            if len(parts) >= 2:
                alias_map[parts[1]] = parts[0]
                
    return alias_map

## Filter the complete allias data for specific gene ID prefixes
def filter_gene_map(full_alias_map, prefix):
    pattern = re.compile(f"^{prefix}_\\d+$", re.IGNORECASE)
    return {k.upper(): v for k, v in full_alias_map.items() if pattern.match(k)}

## Read input XLSX files and map gene IDs to STRING Protein IDs
def process_file(file_path, gene_map):
    print(f"Processing: {file_path.name}")
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.lower().str.strip()
        if 'gene' not in df.columns:
            print(f"  Skipping: No 'gene' column found in {file_path.name}")
            return None

        df['gene'] = df['gene'].astype(str).str.upper().str.strip()

        # Map the genes
        df['string_id'] = df['gene'].map(gene_map)
        
        # Calculate stats
        mapped = df['string_id'].notna().sum()
        total = len(df)
        percentage = (mapped/total*100) if total > 0 else 0
        print(f"  Mapped {mapped} out of {total} genes ({percentage:.1f}%)")
        
        # Save result
        output_file = OUTPUT_DIR / f"mapped_{file_path.stem}.tsv"
        df.to_csv(output_file, sep='\t', index=False)
        print(f"  Saved to: {output_file}")
        
        return {'file': file_path.name, 'mapped': mapped, 'total': total}
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return None


# Execute the mapping process by looping through species and files
def main():
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"INPUT_DIR: {INPUT_DIR} (exists: {INPUT_DIR.exists()})")
    print(f"STRING_DIR: {STRING_DIR} (exists: {STRING_DIR.exists()})")
    print(f"OUTPUT_DIR: {OUTPUT_DIR} (exists: {OUTPUT_DIR.exists()})\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    species_stats = {}  # Track stats per species
    
    for species, config in SPECIES_CONFIG.items():
        print(f"--- Starting the mapping for {species} ---")

        alias_path = STRING_DIR / f"{config['taxid']}.protein.aliases.v{STRING_VERSION}.txt"
        if not alias_path.exists():
            print(f"Error: Alias file not found for {species} ({alias_path})")
            continue

        full_aliases = load_string_aliases(alias_path)

        gene_map = filter_gene_map(full_aliases, config['prefix'])
        print(f"  Filtered to {len(gene_map)} gene IDs with prefix '{config['prefix']}'")

        species_stats[species] = []  # Initialize list for this species
        
        for file_path in INPUT_DIR.glob("*.xlsx"):
            if re.search(config['file_pattern'], file_path.name):
                result = process_file(file_path, gene_map)
                if result:
                    species_stats[species].append(result)
        print()
    
    # Print summary by species and total
    if species_stats:
        print("=" * 70)
        print("SUMMARY BY STUDY")
        print("=" * 70)
        
        grand_total_mapped = 0
        grand_total_genes = 0
        
        for species, stats in species_stats.items():
            if stats:
                species_mapped = sum(s['mapped'] for s in stats)
                species_total = sum(s['total'] for s in stats)
                species_percent = (species_mapped/species_total*100) if species_total > 0 else 0
                print(f"\n{species}:")
                print(f"  Files processed: {len(stats)}")
                print(f"  Genes mapped: {species_mapped} out of {species_total} ({species_percent:.1f}%)")
                grand_total_mapped += species_mapped
                grand_total_genes += species_total
        
        print(f"\n{'-' * 70}")
        print("TOTAL:")
        grand_percent = (grand_total_mapped/grand_total_genes*100) if grand_total_genes > 0 else 0
        print(f"  Files processed: {sum(len(s) for s in species_stats.values())}")
        print(f"  Genes mapped: {grand_total_mapped} out of {grand_total_genes} ({grand_percent:.1f}%)")
        print("=" * 70)
    
    print(f"\nDone! All mapped files are in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
