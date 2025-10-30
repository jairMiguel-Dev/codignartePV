#!/bin/bash
echo "🚀 Iniciando build no Render..."
pip install -r requirements.txt
python init_db.py
python populate_exercises.py
echo "✅ Build concluído!"