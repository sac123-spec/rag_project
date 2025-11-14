import sys
import os

# Ensure the project root is in PYTHONPATH
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
