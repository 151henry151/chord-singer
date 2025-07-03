"""
Monkey patch for madmom to fix NumPy compatibility issues.
This patches the deprecated np.float usage in madmom.
"""

import numpy as np
import sys
from types import ModuleType

def patch_madmom():
    """Apply patches to fix madmom NumPy compatibility issues."""
    
    # Patch np.float to np.float64 for compatibility
    if not hasattr(np, 'float'):
        np.float = np.float64
    # Patch np.int to int for compatibility
    if not hasattr(np, 'int'):
        np.int = int
    
    # If madmom is already imported, we need to patch the specific module
    if 'madmom' in sys.modules:
        madmom = sys.modules['madmom']
        if hasattr(madmom, 'io') and hasattr(madmom.io, '__init__'):
            # Patch the SEGMENT_DTYPE in madmom.io.__init__
            try:
                import madmom.io
                if hasattr(madmom.io, 'SEGMENT_DTYPE'):
                    # Replace np.float with np.float64 in the dtype
                    dtype_list = list(madmom.io.SEGMENT_DTYPE)
                    for i, (name, dtype) in enumerate(dtype_list):
                        if dtype == np.float64:  # This was originally np.float
                            dtype_list[i] = (name, np.float64)
                    madmom.io.SEGMENT_DTYPE = np.dtype(dtype_list)
            except Exception as e:
                print(f"Warning: Could not patch madmom.io: {e}")

def apply_patch():
    """Apply the patch before importing madmom."""
    patch_madmom()

# Apply patch when this module is imported
apply_patch() 