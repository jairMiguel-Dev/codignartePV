from app import app
import asyncio
import os

async def initialize_app():
    """Inicializa a aplicação de forma assíncrona"""
    try:
        # Importar e executar a inicialização do banco
        from app import init_database
        await init_database()
        print("✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")

# Criar e inicializar a aplicação
def create_application():
    """Factory function para criar a aplicação"""
    # Executar inicialização assíncrona
    asyncio.run(initialize_app())
    return app

# Aplicação para o Gunicorn/Waitress
application = create_application()

if __name__ == "__main__":
    # Para desenvolvimento local
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    application.run(host="0.0.0.0", port=port, debug=debug)