#!/bin/bash

echo "Checking Python setup..."
echo ""
echo "Which python:"
which python
echo ""
echo "Python version:"
python --version
echo ""
echo "Python path:"
python -c "import sys; print(sys.executable)"
echo ""
echo "Python path list:"
python -c "import sys; print('\n'.join(sys.path))"
echo ""
echo "Checking if fastapi is importable:"
python -c "import fastapi; print('FastAPI found:', fastapi.__version__)" 2>&1
echo ""
echo "Venv Python:"
ls -la venv/bin/python*
