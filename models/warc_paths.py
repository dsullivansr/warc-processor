"""Path handling for WARC files and related outputs.

This module provides path validation and handling specific to WARC processing,
ensuring proper file extensions and permissions.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WarcPath:
    """Represents a path to a WARC file.
    
    This class ensures that the path points to a valid WARC file
    with the correct extension.
    
    Attributes:
        path: The Path object representing the WARC file location.
    """
    path: Path
    
    @classmethod
    def from_str(cls, path_str: str) -> 'WarcPath':
        """Creates a WarcPath from a string path.
        
        Args:
            path_str: The path string to convert.
            
        Returns:
            A new WarcPath instance.
            
        Raises:
            ValueError: If the path doesn't have a .warc or .warc.gz extension.
        """
        path = Path(path_str)
        if not (path.suffix == '.warc' or 
                (path.suffix == '.gz' and path.stem.endswith('.warc'))):
            raise ValueError(
                f"Invalid WARC file extension: {path_str}. "
                "Must end in .warc or .warc.gz"
            )
        return cls(path)
    
    def __str__(self) -> str:
        return str(self.path)


@dataclass(frozen=True)
class OutputPath:
    """Represents a path where output will be written.
    
    This class ensures that the output directory exists and is writable.
    
    Attributes:
        path: The Path object representing the output location.
    """
    path: Path
    
    @classmethod
    def from_str(cls, path_str: str) -> 'OutputPath':
        """Creates an OutputPath from a string path.
        
        Args:
            path_str: The path string to convert.
            
        Returns:
            A new OutputPath instance.
            
        Raises:
            ValueError: If the parent directory doesn't exist or isn't writable.
        """
        path = Path(path_str)
        if not path.parent.exists():
            raise ValueError(f"Output directory doesn't exist: {path.parent}")
        if not os.access(path.parent, os.W_OK):
            raise ValueError(f"Output directory isn't writable: {path.parent}")
        return cls(path)
    
    def __str__(self) -> str:
        return str(self.path)
