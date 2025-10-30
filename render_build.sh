#!/bin/bash
echo "🚀 Executando build para Render..."
python init_db.py
python populate_exercises.py
echo "✅ Build concluído!"