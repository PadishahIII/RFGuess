import importlib
import os

directory = "."
directoryList = ["Components", "Component", "Configs", "Config"]

existedDirList = [d for d in os.listdir(directory) if d in directoryList]

for d in existedDirList:

    moduleFiles: str = [f for f in os.listdir(d) if f.endswith(".py")]
    for moduleFile in moduleFiles:
        if moduleFile.startswith("__init__"):
            continue
        moduleName = moduleFile[:-3]
        module = importlib.import_module(f"{d}.{moduleName}")
