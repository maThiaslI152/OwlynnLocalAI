import os
import sys
from pathlib import Path

# Add the Backend directory to the Python path
backend_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_dir) 