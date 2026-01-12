# fusarium_genetoprot_mapping# Gene ID Mapping Scripts

Two mapping scripts for *Fusarium* species gene IDs to STRING protein IDs:

1. **mapping.py** - Direct species mapping (non-orthology)
2. **01.2_orthology_mapping_fpg2fg.py** - Orthology-based mapping

## Overview

### mapping.py (Direct Mapping)

Maps gene IDs directly from Excel files to STRING protein IDs for *F. graminearum* and *F. oxysporum* by matching gene ID prefixes.

### 01.2_orthology_mapping_fpg2fg.py (Orthology Mapping)

Maps *F. pseudograminearum* (FPse) gene IDs to STRING protein IDs using orthology inference through *F. graminearum* (FGSG) genes.

## Directory Structure

Before running either script, ensure the following directory structure exists:

```
c:\Users\Tuna\Desktop\test\
├── mapping.py                              # Direct mapping script
├── 01.2_orthology_mapping_fpg2fg.py       # Orthology mapping script
├── input_data/                             # Input Excel files
│   ├── 1_Downregulated_Genes.xlsx
│   ├── 1_Upregulated_Genes.xlsx
│   ├── 2_Downregulated_Genes.xlsx
│   ├── 2_Upregulated_Genes.xlsx
│   ├── 3_Downregulated_Genes.xlsx
│   ├── 4_Downregulated_Genes.xlsx
│   ├── 5_Downregulated_Genes.xlsx
│   ├── 6_Downregulated_Genes.xlsx         # For orthology mapping
│   ├── 6_Upregulated_Genes.xlsx           # For orthology mapping
│   ├── 7_Downregulated_Genes.xlsx
│   ├── 7_Upregulated_Genes.xlsx
│   ├── 8_Downregulated_Genes.xlsx
│   └── 8_Upregulated_Genes.xlsx
├── string_data/                            # STRING alias files
│   ├── 229533.protein.aliases.v12.0.txt   # F. graminearum
│   └── 426428.protein.aliases.v12.0.txt   # F. oxysporum
└── mapped_data/                            # Output directory (created automatically)
    ├── mapped_1_Downregulated_Genes.tsv
    ├── mapped_1_Upregulated_Genes.tsv
    ├── mapped_ortholog_6_Downregulated_Genes.tsv
    └── ... (output files)
```

## Input Files

### Excel Files (input_data/)

- **Format**: Excel workbooks (.xlsx)
- **Required column**: "gene" (case-insensitive, will be automatically trimmed)
- **File naming convention**:
  - **mapping.py**:
    - Files starting with **1 or 2** → *F. graminearum*
    - Files starting with **3, 4, 5, 7, or 8** → *F. oxysporum*
  - **01.2_orthology_mapping_fpg2fg.py**:
    - Files starting with **6** → *F. pseudograminearum* to *F. graminearum* orthology mapping

### STRING Alias Files (string_data/)

- **Format**: Tab-separated text files (.txt)
- **Columns**: 
  - Column 0: STRING Protein ID
  - Column 1: Alias (gene ID)
- **Download location**: [STRING Database](https://string-db.org/cgi/download)
- **Required files**:
  - `229533.protein.aliases.v12.0.txt` → *F. graminearum*
  - `426428.protein.aliases.v12.0.txt` → *F. oxysporum*

## Script 1: mapping.py (Direct Mapping)

### Configuration

```python
SPECIES_CONFIG = {
    "F_graminearum": {
        "taxid": "229533",
        "prefix": "FGSG",
        "file_pattern": "^[12]_"
    },
    "F_oxysporum": {
        "taxid": "426428",
        "prefix": "FOXG",
        "file_pattern": "^[34578]_"
    }
}
```

| Species       | Taxid  | Gene Prefix | File Pattern | Files                   |
| ------------- | ------ | ----------- | ------------ | ----------------------- |
| F_graminearum | 229533 | FGSG        | ^[12]_       | 1_*, 2_*                |
| F_oxysporum   | 426428 | FOXG        | ^[34578]_    | 3_*, 4_*, 5_*, 7_*, 8_* |

### How It Works

1. **Load STRING aliases** for the species
2. **Filter aliases** by gene ID prefix (e.g., FGSG_00001)
3. **Map gene IDs** from input files to STRING protein IDs
4. **Generate output** with new `string_id` column
5. **Report statistics** by species and total

### Usage

```bash
python mapping.py
```

### Example Output

```
--- Starting the mapping for F_graminearum ---
Loading aliases from: 229533.protein.aliases.v12.0.txt...
  Filtered to 3450 gene IDs with prefix 'FGSG'
Processing: 1_Downregulated_Genes.xlsx
  Mapped 245 out of 300 genes (81.7%)
  Saved to: mapped_data/mapped_1_Downregulated_Genes.tsv
Processing: 2_Upregulated_Genes.xlsx
  Mapped 198 out of 250 genes (79.2%)
  Saved to: mapped_data/mapped_2_Upregulated_Genes.tsv

======================================================================
SUMMARY BY STUDY
======================================================================

F_graminearum:
  Files processed: 2
  Genes mapped: 443 out of 550 (80.5%)

F_oxysporum:
  Files processed: 4
  Genes mapped: 795 out of 1000 (79.5%)

----------------------------------------------------------------------
TOTAL:
  Files processed: 6
  Genes mapped: 1238 out of 1550 (79.9%)
======================================================================
```

---

## Script 2: 01.2_orthology_mapping_fpg2fg.py (Orthology Mapping)

### Configuration

```python
ORTHOLOG_CONFIG = {
    "F_pseudograminearum_to_F_graminearum": {
        "file_pattern": "^6_",
        "source_prefix": "FPSE",            # Genes in your input files
        "target_prefix": "FGSG",            # Reference genes in STRING
        "target_taxid": "229533",           # F. graminearum
    }
}
```

| Source Species       | Target Species | Source Prefix | Target Prefix | File Pattern |
| -------------------- | -------------- | ------------- | ------------- | ------------ |
| F. pseudograminearum | F. graminearum | FPSE          | FGSG          | ^6_          |

### How It Works

1. **Load target aliases** (F. graminearum FGSG genes) from STRING
2. **Extract numeric parts** from FGSG genes (e.g., 00001 from FGSG_00001)
3. **Infer orthology** by creating FPSE_00001 → STRING_ID mapping
4. **Map genes** from input files using inferred orthology
5. **Generate output** with new `string_id` column
6. **Report statistics** by study and total

### Usage

```bash
python 01.2_orthology_mapping_fpg2fg.py
```

### Example Output

```
--- Starting Ortholog Mapping: F_pseudograminearum_to_F_graminearum ---
Loading target aliases from: 229533.protein.aliases.v12.0.txt...
  Processed 10500 lines from alias file
  Found 3450 valid FGSG genes in STRING database.
  Created ortholog map with 3450 entries from FPSE to FGSG.
Processing: 6_Downregulated_Genes.xlsx
  Mapped 267 out of 350 genes (76.3%)
  Saved to: mapped_data/mapped_ortholog_6_Downregulated_Genes.tsv
Processing: 6_Upregulated_Genes.xlsx
  Mapped 289 out of 380 genes (76.1%)
  Saved to: mapped_data/mapped_ortholog_6_Upregulated_Genes.tsv

======================================================================
SUMMARY BY STUDY
======================================================================

F_pseudograminearum_to_F_graminearum:
  Files processed: 2
  Genes mapped: 556 out of 730 (76.2%)

----------------------------------------------------------------------
TOTAL:
  Files processed: 2
  Genes mapped: 556 out of 730 (76.2%)
======================================================================
```

---

## Output Files

### Output Location

All mapped files are saved to `mapped_data/` directory

### Direct Mapping (mapping.py)

- Naming pattern: `mapped_{original_filename}.tsv`
- Example: `mapped_1_Downregulated_Genes.tsv`

### Orthology Mapping (01.2_orthology_mapping_fpg2fg.py)

- Naming pattern: `mapped_ortholog_{original_filename}.tsv`
- Example: `mapped_ortholog_6_Downregulated_Genes.tsv`

### File Format

- **Type**: Tab-separated values (.tsv)
- **Columns**: All original columns + new `string_id` column
- **string_id values**: STRING protein ID (or empty if unmapped)

---

## Requirements

- Python 3.6+
- pandas
- openpyxl (for Excel reading)

### Installation

```bash
pip install pandas openpyxl
```

---

## Troubleshooting

### No output files created

- Verify `string_data/` contains the required alias files with correct filenames
- Check that `input_data/` has .xlsx files matching the expected naming patterns
- Run the script and check console output for error messages

### Low mapping percentage

- Verify gene ID format matches the STRING database (e.g., FGSG_00001)
- Confirm the correct gene prefix is configured for each species/organism
- Some genes may not exist in the STRING database version being used
- For orthology mapping, check that numeric parts match between source and target

### "Alias file not found" error

- Ensure STRING alias files are in the `string_data/` directory
- Verify filenames exactly match format: `{taxid}.protein.aliases.v{version}.txt`
- Check that the taxid and version in the filename match the configuration

### File processing errors

- Ensure the "gene" column exists in your Excel files (case-insensitive)
- Check that Excel files are not corrupted or locked
- Verify gene IDs don't contain special characters that might cause mapping issues

---

## Key Differences

| Feature                  | mapping.py                   | orthology_mapping.py                  |
| ------------------------ | ---------------------------- | ------------------------------------- |
| **Use Case**             | Direct STRING mapping        | Cross-species orthology inference     |
| **Supported Species**    | F. graminearum, F. oxysporum | F. pseudograminearum → F. graminearum |
| **Mapping Method**       | Direct prefix matching       | Numeric ortholog inference            |
| **Typical Success Rate** | 75-85%                       | 70-80%                                |
| **Output Prefix**        | `mapped_`                    | `mapped_ortholog_`                    |

---

## Some Notes

- Gene IDs are automatically converted to uppercase during processing
- Empty or null values in the gene column are left unmapped
- All original data is preserved; only `string_id` column is added
- Summary statistics are printed by species/study and as a grand total
- Both scripts validate directories exist before processing
- Error handling with informative messages for missing or malformed files
