from pathlib import Path

spec_file = "canvas_grab.spec"

spec = Path(spec_file).read_text()
spec = spec.replace("excludes=[]", "excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter']")
spec = spec.replace("block_cipher = None", """
block_cipher = None
import sys
sys.modules['FixTk'] = None
""")
Path(spec_file).write_text(spec)
