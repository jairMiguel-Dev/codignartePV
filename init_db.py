from app import app, db
from models import Usuario, Exercicio, Progresso, Transacao

def init_database():
    with app.app_context():
        print("🔄 Criando tabelas...")
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se já existem exercícios
        if not Exercicio.query.first():
            print("🔄 Criando dados iniciais...")
            from app import criar_dados_iniciais
            criar_dados_iniciais()
            print("✅ Dados iniciais criados!")
        
        print("🎉 Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_database()