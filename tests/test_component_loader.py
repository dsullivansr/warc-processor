"""Tests for component loader."""

import os
import shutil
import tempfile
import unittest
from abc import ABC, abstractmethod

from component_loader import ComponentLoader


# Test interfaces and components
class AbstractTestInterface(ABC):
    """Abstract test interface for component loading."""

    @abstractmethod
    def process(self) -> str:
        """Process something."""


class ValidComponent(AbstractTestInterface):
    """Valid component that implements AbstractTestInterface."""

    def process(self) -> str:
        """Process something."""
        return "valid"


class AnotherValidComponent(AbstractTestInterface):
    """Another valid component that implements AbstractTestInterface."""

    def process(self) -> str:
        """Process something."""
        return "another"


class InvalidComponent:
    """Invalid component that doesn't implement AbstractTestInterface."""

    def something_else(self) -> None:
        """Do something else."""


class TestComponentLoader(unittest.TestCase):
    """Test component loader."""

    def setUp(self):
        """Set up test case."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup)

        # Create test component files
        self._create_component_file(
            "valid_component.py",
            """
class ValidComponent:
    def process(self) -> str:
        return "valid"
""".strip(),
        )

        self._create_component_file(
            "another_valid_component.py",
            """
class AnotherValidComponent:
    def process(self) -> str:
        return "another"
""".strip(),
        )

        self._create_component_file(
            "invalid_component.py",
            """
class InvalidComponent:
    def something_else(self) -> None:
        pass
""".strip(),
        )

        self._create_component_file(
            "syntax_error.py",
            """
this is not valid python
""".strip(),
        )

        # Create __init__.py to make it a package
        self._create_component_file("__init__.py", "")

    def _create_component_file(self, filename: str, content: str) -> None:
        """Create a component file in the test directory.

        Args:
            filename: Name of the file to create
            content: Content to write to the file
        """
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content + "\n")

    def _cleanup(self) -> None:
        """Clean up test files."""
        try:
            shutil.rmtree(self.test_dir)
        except OSError:
            pass  # Directory already removed

    def test_load_components(self):
        """Test loading components."""
        components = ComponentLoader.load_components(
            self.test_dir,
            AbstractTestInterface,
        )

        # Should find both valid components
        self.assertEqual(len(components), 2)
        self.assertIn("ValidComponent", components)
        self.assertIn("AnotherValidComponent", components)

        # Components should be properly instantiable
        valid = components["ValidComponent"]()
        another = components["AnotherValidComponent"]()
        self.assertEqual(valid.process(), "valid")
        self.assertEqual(another.process(), "another")

    def test_load_components_empty_directory(self):
        """Test loading from empty directory."""
        empty_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: os.rmdir(empty_dir))

        components = ComponentLoader.load_components(empty_dir, AbstractTestInterface)
        self.assertEqual(len(components), 0)

    def test_load_components_nonexistent_directory(self):
        """Test loading from nonexistent directory."""
        with self.assertRaises(ValueError):
            ComponentLoader.load_components("/nonexistent/dir", AbstractTestInterface)

    def test_load_components_with_errors(self):
        """Test loading components with some files containing errors."""
        components = ComponentLoader.load_components(
            self.test_dir,
            AbstractTestInterface,
        )

        # Should still find valid components despite errors in other files
        self.assertEqual(len(components), 2)
        self.assertIn("ValidComponent", components)
        self.assertIn("AnotherValidComponent", components)
