from cx_Freeze import setup, Executable

setup(
    name = "مخازن الورشة الرئيسيةللخدمات الطبية",
    version = "1.0",
    options = {"build_exe": {"packages":["tkinter"], "include_files": ["Kobry_el_kobba_hospital_logo.png"]}},
    executables = [Executable("main.py", base = "Win32GUI")]
)
