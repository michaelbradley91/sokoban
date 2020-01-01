import sys

import cx_Freeze

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",         # Shortcut
     "DesktopFolder",           # Directory_
     "Sokoban",                 # Name
     "TARGETDIR",               # Component_
     "[TARGETDIR]Sokoban.exe",  # Target
     None,                      # Arguments
     None,                      # Description
     None,                      # Hot-key
     None,                      # Icon
     None,                      # IconIndex
     None,                      # ShowCmd
     'TARGETDIR'                # WkDir
     ),
    ]
msi_data = {"Shortcut": shortcut_table}

executables = [cx_Freeze.Executable(
    "app.py",
    targetName="Sokoban.exe",
    icon="resources/Sokoban.ico",
    base=base,
    shortcutDir="DesktopFolder",
    shortcutName="Sokoban")
]

cx_Freeze.setup(
    name="Sokoban",
    version="0.10.0",
    description="Let's play Sokoban!",
    options={
        "build_exe": {
            "packages": ["pygame", "OpenGL"],
            "include_files": ["resources/"],
            "excludes": ["tkinter", "OpenGL.GL.SGIX.async", "numpy"]
        },
        "bdist_msi": {
            'upgrade_code': '{94a3e49d-c84d-4f08-bbc4-aa0b18cef955}',
            'add_to_path': False,
            'initial_target_dir': "[ProgramFilesFolder]\\Sokoban\\",
            'data': msi_data
        }
    },
    executables=executables
)
