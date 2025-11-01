from app import app, db
from models import Exercicio
import os

def initialize_app():
    """Inicializa a aplicação de forma síncrona"""
    try:
        with app.app_context():
            print("🔄 Criando tabelas do banco...")
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se já existem exercícios
            if not Exercicio.query.first():
                print("🔄 Criando dados iniciais...")
                from app import criar_dados_iniciais
                criar_dados_iniciais()
                print("✅ Dados iniciais criados!")
            
            print("🎉 Aplicação inicializada com sucesso!")
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")

# Inicializar a aplicação
initialize_app()

# Aplicação para o Gunicorn/Waitress
application = app

if __name__ == "__main__":
    # Para desenvolvimento local
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    application.run(host="0.0.0.0", port=port, debug=debug)