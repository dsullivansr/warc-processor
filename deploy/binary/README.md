# Binary Distribution

This directory contains configuration and scripts for creating standalone binary distributions of the WARC Processor.

## Files
- `create_release.sh` - Script to create binary releases
- `warc-processor.spec` - PyInstaller specification file

## Creating a Release

```bash
./create_release.sh
```

This will create `dist/warc-processor-<version>-linux-x86_64.tar.gz` containing:
- Standalone executable
- Configuration files
- Documentation

## Customizing the Build

### PyInstaller Spec File
The `warc-processor.spec` file controls how PyInstaller builds the binary. Common customizations:

```python
# Add additional data files
a = Analysis(
    ['warc_processor_main.py'],
    datas=[
        ('config.yaml', '.'),
        ('additional_file.txt', 'subdir'),
    ],
    ...
)

# Add hidden imports if PyInstaller misses dependencies
a = Analysis(
    ['warc_processor_main.py'],
    hiddenimports=['yaml', 'other_module'],
    ...
)

# Enable debug mode
exe = EXE(
    ...,
    debug=True,
    ...
)
```

### Build Options

Modify `create_release.sh` for different build options:

```bash
# Create debug build
pyinstaller --debug ...

# Disable UPX compression
pyinstaller --noupx ...

# Include additional files
pyinstaller --add-data "extra_file.txt:." ...
```

## Troubleshooting

1. **Missing Dependencies**
   - Check `build/warc-processor/warn-warc-processor.txt` for import errors
   - Add missing imports to `hiddenimports` in spec file

2. **File Not Found Errors**
   - Ensure all required files are listed in `datas`
   - Check paths are relative to spec file

3. **Binary Size Issues**
   - Enable UPX compression
   - Use `--exclude-module` to remove unused packages

## Platform Support

Current build is for Linux x86_64. For other platforms:

1. **Windows**
   ```bash
   # Add to spec file
   exe = EXE(
       ...,
       console=True,  # Command line
       # or
       console=False, # GUI
   )
   ```

2. **macOS**
   ```bash
   # Add to spec file
   exe = EXE(
       ...,
       target_arch='universal2',  # For M1 and Intel
   )
   ```
