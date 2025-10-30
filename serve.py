from waitress import serve
from wsgi import application
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Servidor iniciando na porta {port}...")
    serve(application, host='0.0.0.0', port=port)