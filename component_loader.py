"""Generic component loader for dynamic class loading."""

import importlib.util
import inspect
import logging
import os
from typing import Dict, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ComponentLoader:
    """Dynamically loads components that implement a specified interface."""

    @staticmethod
    def load_components(
        directory: str,
        base_class: Type[T],
    ) -> Dict[str, Type[T]]:
        """Load components from a directory that implement an interface.

        Args:
            directory: Directory containing component modules
            base_class: Base class/interface that components must implement

        Returns:
            Dictionary mapping class names to component classes

        Raises:
            ValueError: If directory does not exist

        Example:
            >>> from my_interface import MyInterface
            >>> loader = ComponentLoader()
            >>> components = loader.load_components('components', MyInterface)
        """
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")

        # Get all Python files in directory
        module_files = [
            f[:-3]
            for f in os.listdir(directory)
            if f.endswith('.py') and not f.startswith('__')
        ]

        # Get required methods from base_class
        required_methods = {
            name for name, member in inspect.getmembers(base_class)
            if (inspect.isfunction(member) and
                getattr(member, '__isabstractmethod__', False))
        }

        # Load all matching classes
        component_classes = {}
        for module_name in module_files:
            try:
                # Load module from file path
                module_path = os.path.join(directory, f"{module_name}.py")
                spec = importlib.util.spec_from_file_location(
                    module_name, module_path)
                if spec is None or spec.loader is None:
                    msg = ("Failed to load module %s: Invalid module "
                           "specification")
                    logger.warning(msg, module_name)
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find classes that implement required methods
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj == base_class:
                        continue

                    # Check if class has all required methods
                    class_methods = {
                        name for name, _ in inspect.getmembers(
                            obj, predicate=inspect.isfunction)
                    }
                    if required_methods.issubset(class_methods):
                        component_classes[name] = obj
            except (ImportError, SyntaxError, TypeError) as e:
                msg = "Failed to load module %s: %s"
                logger.warning(msg, module_name, str(e))

        return component_classes
