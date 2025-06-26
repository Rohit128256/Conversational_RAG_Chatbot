import os
from pathlib import Path


list_of_files = [
    ".github/workflows/.gitkeep",
    f"src/__init__.py",
    f"src/session.py",
    f"src/add_info.py",
    f"src/runnables.py",
    f"src/components/__init__.py",
    f"src/components/retrievers.py",
    f"src/components/prompts.py",
    f"src/components/chains.py",
    f"src/components/models.py",
    f"src/components/vector_store.py",
    "app.py",
    "requirements.txt",
    "notebooks/testing.ipynb"
    ".env"
]


for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir,exist_ok=True)

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath,'w') as f:
            pass