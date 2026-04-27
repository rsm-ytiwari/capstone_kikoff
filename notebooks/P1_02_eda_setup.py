"""
Setup script for EDA notebook - ensures correct paths are configured
Run this at the top of the notebook for proper file loading
"""
import os
from pathlib import Path

def setup_notebook_paths():
    """Configure notebook working directory to find data files"""
    
    # Check current location
    current = Path.cwd()
    
    # Find the project root (contains 'data' directory)
    if not (current / 'data').exists():
        # If data not in current dir, try parent
        parent = current.parent
        if (parent / 'data').exists():
            os.chdir(parent)
            print(f"Changed working directory to: {parent}")
        else:
            # Try to find capstone_team directory
            for ancestor in current.parents:
                if 'capstone_team' in ancestor.name and (ancestor / 'data').exists():
                    os.chdir(ancestor)
                    print(f"Changed working directory to: {ancestor}")
                    break
    
    # Verify data directory
    data_dir = Path.cwd() / 'data'
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found at {data_dir}")
    
    # List available files
    csv_files = list(data_dir.glob('*.csv'))
    print(f"\nData directory: {data_dir}")
    print(f"CSV files found: {len(csv_files)}")
    for f in csv_files:
        print(f"  - {f.name}")
    
    return data_dir

if __name__ == '__main__':
    setup_notebook_paths()
