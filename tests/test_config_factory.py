"""Test configuration factory."""

import os
import tempfile

import yaml


def create_component_config(config):
    """Create a component configuration file.

    Args:
        config: Configuration dictionary.

    Returns:
        Path to configuration file.
    """
    config_file = os.path.join(tempfile.gettempdir(), "test_config.yaml")
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    return config_file
