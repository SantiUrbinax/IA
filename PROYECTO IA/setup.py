from cx_Freeze import setup, Executable
import sys

# Archivos extras que necesitas incluir
include_files = [
    "tomato_maturity_model.h5",
    "tomato_quality_model.h5",
    "tomate_triste.png",
    "TOMACOIA.COM.png"
]

# Paquetes que usa tu proyecto
packages = ["tkinter", "tensorflow", "PIL", "numpy"]

# Opciones de build
build_exe_options = {
    "packages": packages,
    "include_files": include_files,
}

# Base para que no muestre consola (solo para Windows GUI)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="ClasificadorTomates",
    version="1.0",
    description="Aplicación para clasificar tomates usando IA",
    options={"build_exe": build_exe_options},
    executables=[Executable("INTERFAZGRAFICA.py", base=base)]
)
