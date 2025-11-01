from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Usuario, Exercicio, Progresso, Transacao, ModuloConcluido
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import stripe
import os
import random
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///codignarte.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY não configurada")
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

STRIPE_PRICE_IDS = {
    'assinatura': os.environ.get('STRIPE_PRICE_ASSINATURA'),
    'vida_1': os.environ.get('STRIPE_PRICE_VIDA_1'),
    'vida_3': os.environ.get('STRIPE_PRICE_VIDA_3'),
    'vida_5': os.environ.get('STRIPE_PRICE_VIDA_5'),
}

print("=" * 60)
print("🔍 VERIFICAÇÃO DAS VARIÁVEIS DE AMBIENTE")
print("=" * 60)
print(f"✅ SECRET_KEY: {'Configurado' if os.environ.get('SECRET_KEY') else '❌ NÃO CONFIGURADO'}")
print(f"✅ DATABASE_URL: {'Configurado' if os.environ.get('DATABASE_URL') else '❌ NÃO CONFIGURADO'}")
print(f"✅ STRIPE_SECRET_KEY: {'***' + stripe.api_key[-8:] if stripe.api_key else '❌ NÃO CONFIGURADO'}")
print(f"✅ STRIPE_PUBLIC_KEY: {'***' + STRIPE_PUBLIC_KEY[-8:] if STRIPE_PUBLIC_KEY else '❌ NÃO CONFIGURADO'}")
print(f"✅ STRIPE_WEBHOOK_SECRET: {'***' + STRIPE_WEBHOOK_SECRET[-8:] if STRIPE_WEBHOOK_SECRET else '❌ NÃO CONFIGURADO'}")

print("\n🔍 PRICE IDs CONFIGURADOS:")
for price_type, price_id in STRIPE_PRICE_IDS.items():
    status = '✅' if price_id and price_id.startswith('price_') else '❌'
    print(f"   {status} {price_type}: {price_id or 'NÃO CONFIGURADO'}")

print("=" * 60)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

MODULOS = {
    'iniciante': [
        {
            'id': 'variaveis_operadores',
            'nome': 'Variáveis e Operadores',
            'descricao': 'Aprenda o básico da programação com variáveis e operações matemáticas',
            'icone': 'fa-calculator',
            'total_exercicios': 5
        },
        {
            'id': 'estruturas_controle',
            'nome': 'Estruturas de Controle',
            'descricao': 'Controle o fluxo do seu código com condições e loops',
            'icone': 'fa-sitemap',
            'total_exercicios': 5
        }
    ],
    'intermediario': [
        {
            'id': 'funcoes',
            'nome': 'Funções',
            'descricao': 'Aprenda a criar e usar funções para organizar seu código',
            'icone': 'fa-cogs',
            'total_exercicios': 5
        },
        {
            'id': 'arrays_objetos',
            'nome': 'Arrays e Objetos',
            'descricao': 'Trabalhe com listas e objetos para armazenar dados',
            'icone': 'fa-layer-group',
            'total_exercicios': 5
        }
    ],
    'avancado': [
        {
            'id': 'programacao_assincrona',
            'nome': 'Programação Assíncrona',
            'descricao': 'Domine callbacks, promises e async/await',
            'icone': 'fa-bolt',
            'total_exercicios': 5
        },
        {
            'id': 'dom_manipulation',
            'nome': 'Manipulação do DOM',
            'descricao': 'Interaja com páginas web dinamicamente',
            'icone': 'fa-window-restore',
            'total_exercicios': 5
        }
    ]
}

def criar_dados_iniciais():
    try:
        if not Exercicio.query.first():
            exercicios = [
                Exercicio(
                    pergunta="Qual é o resultado de 5 + 3? É tipo somar 5 reais com 3 reais na carteira!",
                    codigo_exemplo="console.log(5 + 3);",
                    resposta_correta="8",
                    nivel="iniciante",
                    teoria="O operador '+' é usado para adição em JavaScript, igual quando você soma dinheiro! Pense: se você tem 5 reais e ganha mais 3, fica com 8 reais!",
                    modulo='variaveis_operadores',
                    ordem_no_modulo=1,
                    dica="Pense em quanto dinheiro você teria se juntasse 5 reais com 3 reais!"
                ),
                Exercicio(
                    pergunta="Como declarar uma variável chamada 'nome' em JavaScript? Tipo quando você guarda o nome de alguém na memória!",
                    codigo_exemplo="// Declare a variável 'nome'\n___ nome;",
                    resposta_correta="let",
                    nivel="iniciante",
                    teoria="Use 'let' para declarar variáveis que podem mudar, igual sua idade que muda todo ano! É como uma caixinha onde você guarda informações.",
                    modulo='variaveis_operadores',
                    ordem_no_modulo=2,
                    dica="Lembre-se: 'let' é como 'deixe' eu guardar este valor na memória!"
                ),
                Exercicio(
                    pergunta="Qual é o resultado de 10 % 3? É tipo dividir 10 balas entre 3 amigos e ver quantas sobram!",
                    codigo_exemplo="console.log(10 % 3);",
                    resposta_correta="1",
                    nivel="iniciante",
                    teoria="O operador '%' retorna o resto da divisão. 10 dividido por 3 dá 3 e sobra 1! É muito útil para saber se um número é par ou ímpar.",
                    modulo='variaveis_operadores',
                    ordem_no_modulo=3,
                    dica="Pense: se você tem 10 balas e 3 amigos, cada um fica com 3 balas e sobra 1!"
                ),
                Exercicio(
                    pergunta="Complete o código para declarar uma constante 'PI' com o valor 3.14",
                    codigo_exemplo="___ PI = 3.14;",
                    resposta_correta="const",
                    nivel="iniciante",
                    teoria="Use 'const' para coisas que não mudam, igual seu nome ou a data do seu aniversário! É uma constante - sempre o mesmo valor.",
                    modulo='variaveis_operadores',
                    ordem_no_modulo=4,
                    dica="'const' é para constantes - coisas que são constantes, que não mudam!"
                ),
                Exercicio(
                    pergunta="DESAFIO FINAL: Crie uma variável 'idade' com valor 20 e depois some 5. Imprima o resultado!",
                    codigo_exemplo="// Crie a variável idade\n___ idade = 20;\n// Some 5\nidade = idade ___ 5;\n// Imprima a idade\nconsole.log(idade);",
                    resposta_correta="let+",
                    nivel="iniciante",
                    teoria="Hora de juntar tudo que aprendemos! Variáveis e operadores trabalhando juntos! Primeiro criamos a variável, depois modificamos, depois mostramos o resultado.",
                    modulo='variaveis_operadores',
                    ordem_no_modulo=5,
                    eh_desafio_final=True,
                    dica="Primeiro declare a variável, depois some, depois imprima! Use 'let' e '+'"
                ),
                Exercicio(
                    pergunta="Complete o código para verificar se a idade é maior ou igual a 18, tipo para ver se pode dirigir!",
                    codigo_exemplo="let idade = 20;\nif (idade ___ 18) {\n  console.log('Pode dirigir!');\n}",
                    resposta_correta=">=",
                    nivel="iniciante",
                    teoria="O operador '>=' verifica se o valor é maior OU igual, igual quando você precisa ter 18 anos ou mais para algo! É como dizer 'pelo menos 18 anos'.",
                    modulo='estruturas_controle',
                    ordem_no_modulo=1,
                    dica="Maior OU igual - pense em 'pelo menos 18 anos'!"
                ),
                Exercicio(
                    pergunta="Complete o código para criar um loop que conta de 1 a 3",
                    codigo_exemplo="for (let i = 1; i ___ 3; i++) {\n  console.log(i);\n}",
                    resposta_correta="<=",
                    nivel="iniciante",
                    teoria="O loop 'for' repete código várias vezes. Aqui queremos contar de 1 ATÉ 3, então usamos '<=' que significa 'menor ou igual'.",
                    modulo='estruturas_controle',
                    ordem_no_modulo=2,
                    dica="Queremos incluir o 3 também, então precisa ser 'menor ou igual'"
                ),
                Exercicio(
                    pergunta="🔥 PREMIUM: Crie uma função que calcula o IMC (Índice de Massa Corporal)",
                    codigo_exemplo="function calcularIMC(peso, altura) {\n  // Sua código aqui\n  return ___;\n}",
                    resposta_correta="peso/(altura*altura)",
                    nivel="avancado",
                    teoria="Fórmula do IMC: peso dividido pela altura ao quadrado! Em JavaScript, usamos '/' para divisão e '*' para multiplicação.",
                    premium=True,
                    modulo='funcoes_avancadas',
                    ordem_no_modulo=1,
                    dica="Lembre-se: altura ao quadrado é altura × altura! Use os operadores matemáticos corretos."
                ),
                Exercicio(
                    pergunta="🔥 PREMIUM: Crie uma arrow function que dobra um número",
                    codigo_exemplo="const dobrar = (numero) => ___;\nconsole.log(dobrar(5));",
                    resposta_correta="numero*2",
                    nivel="avancado",
                    teoria="Arrow functions são uma forma moderna de escrever funções em JavaScript. Elas são mais curtas e legíveis!",
                    premium=True,
                    modulo='funcoes_avancadas',
                    ordem_no_modulo=2,
                    dica="Para dobrar um número, multiplique por 2! Use o operador de multiplicação."
                ),
            ]
            
            for exercicio in exercicios:
                db.session.add(exercicio)
            
            db.session.commit()
            print("✅ Dados iniciais criados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {str(e)}")
        db.session.rollback()

def init_database():
    """Inicializa o banco de dados"""
    try:
        with app.app_context():
            db.create_all()
            criar_dados_iniciais()
            print("✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {str(e)}")

@app.before_request
def verificar_premium():
    if current_user.is_authenticated:
        current_user.verificar_premium_expirado()
        db.session.commit()

@app.route('/')
def index():
    tem_progresso = False
    if current_user.is_authenticated:
        progresso = Progresso.query.filter_by(usuario_id=current_user.id).first()
        tem_progresso = progresso is not None
    
    return render_template('index.html', tem_progresso=tem_progresso)

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_premium_active:
        current_user.regenerar_vidas()
    
    tempo_restante = current_user.tempo_para_proxima_vida()
    db.session.commit()
    
    progresso = Progresso.query.filter_by(usuario_id=current_user.id).all()
    exercicios_completos = len(progresso)
    novo_usuario = exercicios_completos == 0
    
    transacoes = Transacao.query.filter_by(usuario_id=current_user.id).order_by(Transacao.data_transacao.desc()).all()
    
    return render_template('dashboard.html', 
                         exercicios_completos=exercicios_completos,
                         vidas=current_user.vidas,
                         novo_usuario=novo_usuario,
                         tempo_restante=tempo_restante,
                         premium=current_user.is_premium_active,
                         transacoes=transacoes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            if not usuario.is_premium_active:
                usuario.regenerar_vidas()
            db.session.commit()
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciais inválidas.')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        senha = request.form.get('senha')
        aceitar_termos = request.form.get('aceitar_termos')
        
        if not aceitar_termos:
            return render_template('cadastro.html', error='Você deve aceitar os termos de uso e política de privacidade.')
        
        usuario_existente = Usuario.query.filter(
            (Usuario.email == email) | (Usuario.username == username)
        ).first()
        
        if usuario_existente:
            return render_template('cadastro.html', error='Usuário ou email já cadastrados.')
        
        novo_usuario = Usuario(
            username=username,
            email=email,
            senha=generate_password_hash(senha, method='pbkdf2:sha256')
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        login_user(novo_usuario)
        return redirect(url_for('dashboard'))
    
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/modulos')
@login_required
def modulos():
    # Calcular progresso para cada módulo
    modulos_com_progresso = {}
    
    for nivel, lista_modulos in MODULOS.items():
        modulos_com_progresso[nivel] = []
        for modulo in lista_modulos:
            # Buscar exercícios deste módulo
            exercicios_modulo = Exercicio.query.filter_by(modulo=modulo['id']).all()
            
            # Verificar progresso do usuário
            exercicios_completos = 0
            modulo_concluido = False
            
            for exercicio in exercicios_modulo:
                progresso = Progresso.query.filter_by(
                    usuario_id=current_user.id, 
                    exercicio_id=exercicio.id
                ).first()
                if progresso:
                    exercicios_completos += 1
            
            # Verificar se o módulo está completo (desafio final concluído)
            desafio_final = Exercicio.query.filter_by(
                modulo=modulo['id'], 
                eh_desafio_final=True
            ).first()
            
            if desafio_final:
                progresso_desafio = Progresso.query.filter_by(
                    usuario_id=current_user.id,
                    exercicio_id=desafio_final.id
                ).first()
                modulo_concluido = progresso_desafio is not None
            
            modulos_com_progresso[nivel].append({
                **modulo,
                'exercicios_completos': exercicios_completos,
                'concluido': modulo_concluido,
                'progresso_percent': int((exercicios_completos / len(exercicios_modulo)) * 100) if exercicios_modulo else 0
            })
    
    return render_template('modulos.html', 
                         modulos=modulos_com_progresso,
                         premium=current_user.is_premium_active)

@app.route('/modulo/<string:modulo_id>')
@login_required
def ver_modulo(modulo_id):
    # Buscar exercícios do módulo em ordem
    exercicios = Exercicio.query.filter_by(modulo=modulo_id).order_by(Exercicio.ordem_no_modulo).all()
    
    # Verificar progresso
    progresso_usuario = []
    for exercicio in exercicios:
        progresso = Progresso.query.filter_by(
            usuario_id=current_user.id,
            exercicio_id=exercicio.id
        ).first()
        progresso_usuario.append({
            'exercicio': exercicio,
            'concluido': progresso is not None,
            'tentativas': progresso.tentativas if progresso else 0
        })
    
    # Encontrar informações do módulo
    modulo_info = None
    for nivel, modulos in MODULOS.items():
        for mod in modulos:
            if mod['id'] == modulo_id:
                modulo_info = mod
                break
    
    return render_template('modulo_detalhes.html',
                         modulo=modulo_info,
                         progresso=progresso_usuario,
                         premium=current_user.is_premium_active)

@app.route('/exercicios')
@login_required
def lista_exercicios():
    if not current_user.is_premium_active:
        current_user.regenerar_vidas()
    
    tempo_restante = current_user.tempo_para_proxima_vida()
    db.session.commit()
    
    if current_user.vidas <= 0 and not current_user.is_premium_active:
        return render_template('sem_vidas.html', tempo_restante=tempo_restante)
    
    if current_user.is_premium_active:
        exercicios = Exercicio.query.all()
    else:
        exercicios = Exercicio.query.filter_by(premium=False).all()
    
    progresso = Progresso.query.filter_by(usuario_id=current_user.id).all()
    exercicios_completos_ids = [p.exercicio_id for p in progresso]
    
    return render_template('lista_exercicios.html', 
                         exercicios=exercicios,
                         exercicios_completos_ids=exercicios_completos_ids,
                         vidas=current_user.vidas,
                         tempo_restante=tempo_restante,
                         premium=current_user.is_premium_active)

@app.route('/exercicio/<int:exercicio_id>')
@login_required
def exercicio(exercicio_id):
    if not current_user.is_premium_active:
        current_user.regenerar_vidas()
    
    tempo_restante = current_user.tempo_para_proxima_vida()
    db.session.commit()
    
    if current_user.vidas <= 0 and not current_user.is_premium_active:
        return render_template('sem_vidas.html', tempo_restante=tempo_restante)
    
    exercicio = Exercicio.query.get_or_404(exercicio_id)
    
    if exercicio.premium and not current_user.is_premium_active:
        return render_template('conteudo_premium.html')
    
    return render_template('exercicios.html', 
                         exercicio=exercicio, 
                         tempo_restante=tempo_restante, 
                         premium=current_user.is_premium_active)

@app.route('/verificar_resposta', methods=['POST'])
@login_required
def verificar_resposta():
    if not current_user.is_premium_active:
        current_user.regenerar_vidas()
        db.session.commit()
    
    data = request.get_json()
    exercicio_id = data.get('exercicio_id')
    resposta_usuario = data.get('resposta')
    
    exercicio = Exercicio.query.get(exercicio_id)
    usuario = Usuario.query.get(current_user.id)
    
    if not exercicio:
        return jsonify({'success': False, 'error': 'Exercício não encontrado'})
    
    # Simular output do terminal
    terminal_output = simular_terminal(exercicio, resposta_usuario)
    
    progresso_existente = Progresso.query.filter_by(
        usuario_id=usuario.id, 
        exercicio_id=exercicio_id
    ).first()
    
    if exercicio.resposta_correta.lower() == resposta_usuario.strip().lower():
        # Resposta correta
        if not progresso_existente:
            progresso = Progresso(usuario_id=usuario.id, exercicio_id=exercicio_id)
            db.session.add(progresso)
        else:
            progresso_existente.tentativas += 1
        
        # Verificar se é desafio final e marcar módulo como concluído
        if exercicio.eh_desafio_final:
            modulo_concluido = ModuloConcluido.query.filter_by(
                usuario_id=usuario.id,
                modulo=exercicio.modulo
            ).first()
            
            if not modulo_concluido:
                modulo_concluido = ModuloConcluido(
                    usuario_id=usuario.id,
                    modulo=exercicio.modulo
                )
                db.session.add(modulo_concluido)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'correto': True, 
            'feedback': '🎉 Parabéns! Resposta correta!',
            'vidas_restantes': usuario.vidas,
            'terminal_output': terminal_output,
            'eh_desafio_final': exercicio.eh_desafio_final,
            'modulo_concluido': exercicio.eh_desafio_final
        })
    else:
        # Resposta incorreta
        if progresso_existente:
            progresso_existente.tentativas += 1
        else:
            # Usar vida
            if usuario.vidas_compradas > usuario.vidas_utilizadas_compradas:
                usuario.usar_vida_comprada()
            else:
                if not usuario.is_premium_active:
                    usuario.vidas -= 1
        
        db.session.commit()
        
        if usuario.vidas <= 0 and not usuario.is_premium_active and usuario.get_vidas_compradas_nao_utilizadas() <= 0:
            return jsonify({
                'success': True,
                'correto': False, 
                'sem_vidas': True, 
                'feedback': '💔 Suas vidas acabaram! Aguarde para regenerar.',
                'vidas_restantes': 0,
                'terminal_output': terminal_output
            })
        else:
            feedback = '❌ Resposta incorreta. Tente novamente!'
            if not usuario.is_premium_active:
                feedback += f' Vidas restantes: {usuario.vidas}'
            else:
                feedback += ' (Premium: vidas infinitas!)'
                
            return jsonify({
                'success': True,
                'correto': False, 
                'vidas_restantes': usuario.vidas,
                'feedback': feedback,
                'terminal_output': terminal_output,
                'dica': exercicio.dica if exercicio.dica else None
            })

def simular_terminal(exercicio, resposta):
    """Simula a execução do código no terminal"""
    try:
        if exercicio.tipo == 'output':
            # Simular output baseado no código
            codigo_completo = exercicio.codigo_exemplo.replace('___', resposta)
            
            # Simulações comuns
            if 'console.log(5 + 3)' in codigo_completo:
                return "8"
            elif 'console.log(10 % 3)' in codigo_completo:
                return "1"
            elif 'idade' in codigo_completo and '+' in resposta:
                return "25"
            else:
                return "Resultado executado com sucesso!"
                
        elif exercicio.tipo == 'completion':
            # Mostrar código completado
            codigo_completado = exercicio.codigo_exemplo.replace('___', f'[{resposta}]')
            return f"Código executado:\n{codigo_completado}\n✅ Executado sem erros!"
            
    except Exception as e:
        return f"Erro na simulação: {str(e)}"
    
    return "Execução concluída com sucesso!"

@app.route('/proximo_exercicio/<int:exercicio_atual_id>')
@login_required
def proximo_exercicio(exercicio_atual_id):
    exercicio_atual = Exercicio.query.get(exercicio_atual_id)
    
    if not exercicio_atual:
        return redirect(url_for('modulos'))
    
    # Buscar próximo exercício no mesmo módulo
    proximo = Exercicio.query.filter(
        Exercicio.modulo == exercicio_atual.modulo,
        Exercicio.ordem_no_modulo > exercicio_atual.ordem_no_modulo
    ).order_by(Exercicio.ordem_no_modulo).first()
    
    if proximo:
        if proximo.premium and not current_user.is_premium_active:
            return render_template('conteudo_premium.html')
        return redirect(url_for('exercicio', exercicio_id=proximo.id))
    else:
        # Se não há próximo exercício, verificar se o módulo existe antes de redirecionar
        if exercicio_atual.modulo:
            try:
                return redirect(url_for('ver_modulo', modulo_id=exercicio_atual.modulo))
            except:
                # Se houver erro ao construir a URL, redirecionar para módulos
                return redirect(url_for('modulos'))
        else:
            # Se não há módulo definido, redirecionar para módulos
            return redirect(url_for('modulos'))

@app.route('/atualizar_tempo_restante')
@login_required
def atualizar_tempo_restante():
    try:
        if not current_user.is_premium_active:
            current_user.regenerar_vidas()
            tempo_restante = current_user.tempo_para_proxima_vida()
        else:
            tempo_restante = 0
        
        db.session.commit()
        
        return jsonify({
            'vidas': current_user.vidas,
            'tempo_restante': tempo_restante,
            'tempo_formatado': formatar_tempo(tempo_restante) if tempo_restante > 0 else "Pronta!",
            'premium': current_user.is_premium_active
        })
    except Exception as e:
        print(f"❌ Erro em atualizar_tempo_restante: {str(e)}")
        # Retorna valores padrão em caso de erro
        return jsonify({
            'vidas': current_user.vidas,
            'tempo_restante': 0,
            'tempo_formatado': "Erro",
            'premium': current_user.is_premium_active
        })

def formatar_tempo(segundos):
    minutos = segundos // 60
    segundos_rest = segundos % 60
    return f"{minutos:02d}:{segundos_rest:02d}"

@app.route('/loja')
@login_required
def loja():
    status_reembolso = current_user.get_status_reembolso() if current_user.premium_cancelado else None
    
    return render_template('loja.html', 
                         premium=current_user.is_premium_active,
                         pode_reembolso=current_user.pode_reembolso_assinatura() if current_user.premium else False,
                         status_reembolso=status_reembolso,
                         stripe_public_key=STRIPE_PUBLIC_KEY)

@app.route('/criar-sessao-assinatura', methods=['POST'])
@login_required
def criar_sessao_assinatura():
    if current_user.is_premium_active:
        return jsonify({'error': 'Você já é usuário premium!'}), 400
    
    try:
        price_id = STRIPE_PRICE_IDS['assinatura']
        
        if not price_id:
            print("❌ STRIPE_PRICE_ASSINATURA não configurado")
            return jsonify({'error': 'Configuração de preço não encontrada'}), 500
        
        print(f"🔄 Criando sessão de assinatura com price_id: {price_id}")
        
        try:
            price = stripe.Price.retrieve(price_id)
            print(f"✅ Preço encontrado: {price.id} - {price.unit_amount} {price.currency}")
        except Exception as price_error:
            print(f"❌ Erro ao verificar preço: {str(price_error)}")
            return jsonify({'error': 'Preço não encontrado no Stripe'}), 500
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('pagamento_sucesso', _external=True) + '?session_id={CHECKOUT_SESSION_ID}&tipo=assinatura',
            cancel_url=url_for('loja', _external=True),
            customer_email=current_user.email,
            metadata={
                'user_id': current_user.id,
                'tipo': 'assinatura'
            }
        )
        
        transacao = Transacao(
            usuario_id=current_user.id,
            tipo='assinatura',
            valor=13.49,
            detalhes='Assinatura Premium - Aguardando confirmação do pagamento',
            status='pendente',
            stripe_session_id=checkout_session.id,
            id_publico=Transacao().gerar_id_publico(),
            quantidade_produto=1  # Uma assinatura
        )
        db.session.add(transacao)
        db.session.commit()
        
        print(f"✅ Sessão de assinatura criada: {checkout_session.url}")
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        print(f"❌ Erro ao criar sessão de assinatura: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao processar pagamento. Tente novamente.'}), 500

@app.route('/criar-sessao-vidas/<int:quantidade>', methods=['POST'])
@login_required
def criar_sessao_vidas(quantidade):
    print(f"🔍 Iniciando criação de sessão para {quantidade} vidas")
    
    if current_user.is_premium_active:
        print("❌ Usuário já é premium, não pode comprar vidas")
        return jsonify({'error': 'Usuários premium não precisam comprar vidas!'}), 400
    
    if quantidade not in [1, 3, 5]:
        print(f"❌ Quantidade inválida: {quantidade}")
        return jsonify({'error': 'Pacote inválido'}), 400
    
    try:
        price_id = STRIPE_PRICE_IDS[f'vida_{quantidade}']
        
        if not price_id:
            print(f"❌ STRIPE_PRICE_VIDA_{quantidade} não configurado")
            return jsonify({'error': 'Configuração de preço não encontrada'}), 500
        
        print(f"🔄 Criando sessão de vidas com price_id: {price_id}, quantidade: {quantidade}")
        
        try:
            price = stripe.Price.retrieve(price_id)
            print(f"✅ Preço encontrado: {price.id} - {price.unit_amount} {price.currency}")
        except Exception as price_error:
            print(f"❌ Erro ao verificar preço: {str(price_error)}")
            return jsonify({'error': 'Preço não encontrado no Stripe'}), 500
        
        success_url = url_for('pagamento_sucesso', _external=True) + f'?session_id={{CHECKOUT_SESSION_ID}}&tipo=vidas&quantidade={quantidade}'
        cancel_url = url_for('loja', _external=True)
        
        print(f"🔗 URLs: success={success_url}, cancel={cancel_url}")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=current_user.email,
            metadata={
                'user_id': current_user.id,
                'tipo': 'vidas',
                'quantidade': quantidade
            }
        )
        
        valores = {1: 0.99, 3: 3.00, 5: 4.75}
        valor = valores[quantidade]
        
        transacao = Transacao(
            usuario_id=current_user.id,
            tipo=f'vidas_{quantidade}',
            valor=valor,
            detalhes=f'Pacote de {quantidade} vidas - Aguardando confirmação do pagamento',
            status='pendente',
            stripe_session_id=checkout_session.id,
            id_publico=Transacao().gerar_id_publico(),
            quantidade_produto=quantidade
        )
        db.session.add(transacao)
        db.session.commit()
        
        print(f"✅ Sessão de vidas criada com sucesso: {checkout_session.url}")
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        print(f"❌ Erro ao criar sessão de vidas: {str(e)}")
        import traceback
        print(f"📝 Traceback completo:")
        print(traceback.format_exc())
        return jsonify({'error': 'Erro ao processar pagamento. Tente novamente.'}), 500

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    if not STRIPE_WEBHOOK_SECRET:
        return 'Webhook secret não configurado', 400
        
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"❌ Erro no payload do webhook: {e}")
        return 'Payload inválido', 400
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Erro na assinatura do webhook: {e}")
        return 'Assinatura inválida', 400

    print(f"✅ Webhook recebido: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        processar_pagamento_sucesso(session)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        processar_cancelamento_assinatura(subscription)
        
    elif event['type'] == 'charge.refunded':
        refund = event['data']['object']
        processar_reembolso_stripe(refund)

    return jsonify({'status': 'success'})

def processar_pagamento_sucesso(session):
    try:
        user_id = session['metadata']['user_id']
        tipo = session['metadata']['tipo']
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            print(f"❌ Usuário não encontrado: {user_id}")
            return
        
        print(f"✅ Processando pagamento para usuário: {usuario.username}, tipo: {tipo}")
        
        transacao = Transacao.query.filter_by(stripe_session_id=session.id).first()
        if transacao:
            transacao.status = 'confirmada'
            transacao.stripe_payment_intent = session.payment_intent
            transacao.detalhes = transacao.detalhes.replace('Aguardando confirmação do pagamento', 'Pagamento confirmado')
            print(f"✅ Transação atualizada: {transacao.id}")
        
        if tipo == 'assinatura':
            data_inicio = datetime.utcnow()
            data_expiracao = data_inicio + timedelta(days=30)
            usuario.premium = True
            usuario.premium_cancelado = False
            usuario.data_inicio_premium = data_inicio
            usuario.data_expiracao_premium = data_expiracao
            
            print(f"✅ Premium ativado para usuário: {usuario.username}")
            
        elif tipo == 'vidas':
            quantidade = int(session['metadata']['quantidade'])
            usuario.vidas += quantidade
            usuario.adicionar_vidas_compradas(quantidade)
            print(f"✅ {quantidade} vidas adicionadas para usuário: {usuario.username}")
        
        db.session.commit()
        print(f"✅ Pagamento processado com sucesso para {usuario.username}")
        
    except Exception as e:
        print(f"❌ Erro ao processar pagamento: {str(e)}")
        db.session.rollback()

def processar_cancelamento_assinatura(subscription):
    print(f"📝 Assinatura cancelada: {subscription.id}")

def processar_reembolso_stripe(refund):
    """Processa webhooks de reembolso da Stripe"""
    try:
        payment_intent = refund.payment_intent
        
        # Encontrar transação pelo payment_intent
        transacao = Transacao.query.filter_by(stripe_payment_intent=payment_intent).first()
        
        if not transacao:
            print(f"❌ Transação não encontrada para payment_intent: {payment_intent}")
            return
        
        if refund.status == 'succeeded':
            # Reembolso bem-sucedido
            transacao.completar_reembolso({
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'currency': refund.currency,
                'status': refund.status,
                'reason': refund.reason
            })
            
            print(f"✅ Reembolso processado com sucesso: {refund.id}")
            
        elif refund.status == 'failed':
            # Reembolso falhou
            transacao.falhar_reembolso(f"Reembolso falhou na Stripe: {refund.failure_reason}")
            
            print(f"❌ Reembolso falhou: {refund.id} - {refund.failure_reason}")
        
        db.session.commit()
        
    except Exception as e:
        print(f"❌ Erro ao processar reembolso: {str(e)}")
        db.session.rollback()

@app.route('/pagamento-sucesso')
@login_required
def pagamento_sucesso():
    session_id = request.args.get('session_id')
    tipo = request.args.get('tipo')
    quantidade = request.args.get('quantidade')
    
    transacao = Transacao.query.filter_by(stripe_session_id=session_id, status='confirmada').first()
    
    if transacao:
        mensagem = ""
        if tipo == 'assinatura':
            mensagem = "Sua assinatura premium foi ativada com sucesso! Agora você tem vidas infinitas e acesso a conteúdos exclusivos."
        elif tipo == 'vidas':
            mensagem = f"Pacote de {quantidade} vidas comprado com sucesso! Suas vidas foram adicionadas à sua conta."
        
        return render_template('pagamento_sucesso.html', 
                             mensagem=mensagem,
                             tipo=tipo,
                             quantidade=quantidade,
                             transacao=transacao)
    else:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                processar_pagamento_sucesso(session)
                return redirect(url_for('pagamento_sucesso', session_id=session_id, tipo=tipo, quantidade=quantidade))
        except Exception as e:
            print(f"Erro ao verificar sessão: {str(e)}")
        
        return render_template('pagamento_processando.html')

@app.route('/conteudo_premium')
@login_required
def conteudo_premium():
    if not current_user.is_premium_active:
        return render_template('conteudo_premium.html')
    
    exercicios_premium = Exercicio.query.filter_by(premium=True).all()
    progresso = Progresso.query.filter_by(usuario_id=current_user.id).all()
    exercicios_completos_ids = [p.exercicio_id for p in progresso]
    
    return render_template('conteudo_premium_exclusivo.html', 
                         exercicios=exercicios_premium,
                         exercicios_completos_ids=exercicios_completos_ids)

@app.route('/cancelar_assinatura', methods=['POST'])
@login_required
def cancelar_assinatura():
    if not current_user.premium:
        return jsonify({'success': False, 'error': 'Você não tem uma assinatura premium ativa.'})
    
    if current_user.premium_cancelado:
        return jsonify({'success': False, 'error': 'Sua assinatura já foi cancelada.'})
    
    transacao = Transacao.query.filter_by(
        usuario_id=current_user.id, 
        tipo='assinatura'
    ).order_by(Transacao.data_transacao.desc()).first()
    
    if not transacao:
        return jsonify({'success': False, 'error': 'Transação de assinatura não encontrada.'})
    
    pode_reembolso = transacao.pode_reembolsar()
    motivo = request.json.get('motivo', 'Arrependimento do usuário')
    
    try:
        if pode_reembolso:
            # CANCELAMENTO IMEDIATO COM REEMBOLSO - CDC Artigo 49
            transacao.solicitar_reembolso(motivo)
            
            try:
                reembolso = stripe.Refund.create(
                    payment_intent=transacao.stripe_payment_intent,
                    metadata={
                        'user_id': current_user.id,
                        'transacao_id': transacao.id_publico,
                        'motivo': motivo
                    }
                )
                
                transacao.processar_reembolso(reembolso.id)
                
                # REMOÇÃO IMEDIATA DO STATUS PREMIUM - CONFORME CDC
                current_user.premium = False
                current_user.premium_cancelado = True
                current_user.data_inicio_premium = None
                current_user.data_expiracao_premium = None
                
                mensagem = f'Assinatura cancelada com sucesso! Reembolso integral de R$ {transacao.valor_reembolsado:.2f} solicitado. ID do Reembolso: {reembolso.id}'
                
            except Exception as stripe_error:
                transacao.falhar_reembolso(str(stripe_error))
                # MESMO COM ERRO NO REEMBOLSO, REMOVEMOS O PREMIUM IMEDIATAMENTE
                current_user.premium = False
                current_user.premium_cancelado = True
                current_user.data_inicio_premium = None
                current_user.data_expiracao_premium = None
                mensagem = f'Assinatura cancelada, mas houve um erro ao processar o reembolso: {str(stripe_error)}. O status premium foi removido conforme CDC.'
                
        else:
            # CANCELAMENTO FORA DO PRAZO DE REEMBOLSO
            transacao.solicitar_reembolso('Fora do prazo de reembolso de 7 dias')
            current_user.premium_cancelado = True
            mensagem = f'Assinatura cancelada com sucesso! Você continuará com os benefícios premium até {current_user.data_expiracao_premium.strftime("%d/%m/%Y")}.'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reembolsado': pode_reembolso,
            'message': mensagem,
            'refund_id': transacao.stripe_refund_id if pode_reembolso else None,
            'transacao_id': transacao.id_publico if transacao else None,
            'status_reembolso': transacao.status_reembolso,
            'valor_reembolsado': transacao.valor_reembolsado if pode_reembolso else 0
        })
        
    except Exception as e:
        print(f"❌ Erro ao cancelar assinatura: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/solicitar-reembolso-vidas/<string:id_publico>', methods=['POST'])
@login_required
def solicitar_reembolso_vidas(id_publico):
    transacao = Transacao.query.filter_by(id_publico=id_publico, usuario_id=current_user.id).first_or_404()
    
    if not transacao.tipo.startswith('vidas_'):
        return jsonify({'success': False, 'error': 'Esta transação não é de pacote de vidas.'})
    
    if transacao.status_reembolso != 'nao_solicitado':
        return jsonify({'success': False, 'error': 'Reembolso já foi solicitado para esta transação.'})
    
    if not transacao.pode_reembolsar():
        vidas_nao_utilizadas = transacao.quantidade_produto - transacao.quantidade_utilizada
        if vidas_nao_utilizadas <= 0:
            return jsonify({'success': False, 'error': 'Não é possível reembolsar este pacote de vidas. Todas as vidas já foram utilizadas.'})
        else:
            return jsonify({'success': False, 'error': 'Não é possível reembolsar este pacote de vidas. Prazo de 7 dias expirado.'})
    
    motivo = request.json.get('motivo', 'Arrependimento do usuário')
    
    try:
        transacao.solicitar_reembolso(motivo)
        
        if transacao.stripe_payment_intent:
            # Para reembolsos parciais, precisamos calcular o valor
            valor_reembolso_centavos = int(transacao.valor_reembolsado * 100)
            
            reembolso = stripe.Refund.create(
                payment_intent=transacao.stripe_payment_intent,
                amount=valor_reembolso_centavos,
                metadata={
                    'user_id': current_user.id,
                    'transacao_id': transacao.id_publico,
                    'motivo': motivo,
                    'tipo': 'reembolso_parcial_vidas'
                }
            )
            
            transacao.processar_reembolso(reembolso.id)
            
            # Remover vidas não utilizadas da conta do usuário
            vidas_remover = transacao.quantidade_produto - transacao.quantidade_utilizada
            current_user.vidas = max(0, current_user.vidas - vidas_remover)
            current_user.vidas_compradas = max(0, current_user.vidas_compradas - vidas_remover)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Reembolso parcial de R$ {transacao.valor_reembolsado:.2f} solicitado com sucesso!',
                'refund_id': reembolso.id,
                'status_reembolso': transacao.status_reembolso,
                'valor_reembolsado': transacao.valor_reembolsado,
                'vidas_nao_utilizadas': vidas_remover
            })
        else:
            return jsonify({'success': False, 'error': 'Não foi possível processar o reembolso. Payment intent não encontrado.'})
            
    except Exception as e:
        transacao.falhar_reembolso(str(e))
        db.session.commit()
        return jsonify({'success': False, 'error': f'Erro ao solicitar reembolso: {str(e)}'})

@app.route('/minhas-compras')
@login_required
def minhas_compras():
    transacoes = Transacao.query.filter_by(usuario_id=current_user.id).order_by(Transacao.data_transacao.desc()).all()
    return render_template('minhas_compras.html', transacoes=transacoes)

@app.route('/detalhes-transacao/<string:id_publico>')
@login_required
def detalhes_transacao(id_publico):
    transacao = Transacao.query.filter_by(id_publico=id_publico, usuario_id=current_user.id).first_or_404()
    
    # Buscar informações atualizadas do reembolso na Stripe se aplicável
    if transacao.stripe_refund_id and transacao.status_reembolso in ['processando', 'solicitado']:
        try:
            refund = stripe.Refund.retrieve(transacao.stripe_refund_id)
            
            if refund.status == 'succeeded' and transacao.status_reembolso != 'completado':
                transacao.completar_reembolso({
                    'refund_id': refund.id,
                    'amount': refund.amount / 100,
                    'currency': refund.currency,
                    'status': refund.status
                })
                db.session.commit()
                
            elif refund.status == 'failed' and transacao.status_reembolso != 'falhou':
                transacao.falhar_reembolso(f"Reembolso falhou na Stripe: {refund.failure_reason}")
                db.session.commit()
                
        except Exception as e:
            print(f"Erro ao buscar status do reembolso: {str(e)}")
    
    return render_template('detalhes_transacao.html', transacao=transacao)

@app.route('/termos-uso')
def termos_uso():
    return render_template('termos_uso.html', data_atual=datetime.utcnow())

@app.route('/politica-privacidade')
def politica_privacidade():
    return render_template('politica_privacidade.html', data_atual=datetime.utcnow())

@app.route('/termo-arrependimento')
def termo_arrependimento():
    return render_template('termo_arrependimento.html', data_atual=datetime.utcnow())

@app.route('/comecar_agora')
@login_required
def comecar_agora():
    primeiro_exercicio = Exercicio.query.filter_by(premium=False).order_by(Exercicio.id).first()
    if primeiro_exercicio:
        return redirect(url_for('exercicio', exercicio_id=primeiro_exercicio.id))
    else:
        return redirect(url_for('modulos'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Inicialização síncrona do banco de dados
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tabelas do banco criadas/verificadas")
            
            # Criar dados iniciais de forma síncrona
            if not Exercicio.query.first():
                exercicios = [
                    Exercicio(
                        pergunta="Qual é o resultado de 5 + 3? É tipo somar 5 reais com 3 reais na carteira!",
                        codigo_exemplo="console.log(5 + 3);",
                        resposta_correta="8",
                        nivel="iniciante",
                        teoria="O operador '+' é usado para adição em JavaScript, igual quando você soma dinheiro!",
                        modulo='variaveis_operadores',
                        ordem_no_modulo=1,
                        dica="Pense em quanto dinheiro você teria se juntasse 5 reais com 3 reais!"
                    ),
                    Exercicio(
                        pergunta="Como declarar uma variável chamada 'nome' em JavaScript? Tipo quando você guarda o nome de alguém na memória!",
                        codigo_exemplo="// Declare a variável 'nome'\n___ nome;",
                        resposta_correta="let",
                        nivel="iniciante",
                        teoria="Use 'let' para declarar variáveis que podem mudar, igual sua idade que muda todo ano!",
                        modulo='variaveis_operadores',
                        ordem_no_modulo=2,
                        dica="Lembre-se: 'let' é como 'deixe' eu guardar este valor na memória!"
                    ),
                    Exercicio(
                        pergunta="Qual é o resultado de 10 % 3? É tipo dividir 10 balas entre 3 amigos e ver quantas sobram!",
                        codigo_exemplo="console.log(10 % 3);",
                        resposta_correta="1",
                        nivel="iniciante",
                        teoria="O operador '%' retorna o resto da divisão. 10 dividido por 3 dá 3 e sobra 1!",
                        modulo='variaveis_operadores',
                        ordem_no_modulo=3,
                        dica="Pense: se você tem 10 balas e 3 amigos, cada um fica com 3 balas e sobra 1!"
                    ),
                    Exercicio(
                        pergunta="Complete o código para declarar uma constante 'PI' com o valor 3.14",
                        codigo_exemplo="___ PI = 3.14;",
                        resposta_correta="const",
                        nivel="iniciante",
                        teoria="Use 'const' para coisas que não mudam, igual seu nome ou a data do seu aniversário!",
                        modulo='variaveis_operadores',
                        ordem_no_modulo=4,
                        dica="'const' é para constantes - coisas que são constantes, que não mudam!"
                    ),
                    Exercicio(
                        pergunta="DESAFIO FINAL: Crie uma variável 'idade' com valor 20 e depois some 5. Imprima o resultado!",
                        codigo_exemplo="// Crie a variável idade\n___ idade = 20;\n// Some 5\nidade = idade ___ 5;\n// Imprima a idade\nconsole.log(idade);",
                        resposta_correta="let+",
                        nivel="iniciante",
                        teoria="Hora de juntar tudo que aprendemos! Variáveis e operadores trabalhando juntos!",
                        modulo='variaveis_operadores',
                        ordem_no_modulo=5,
                        eh_desafio_final=True,
                        dica="Primeiro declare a variável, depois some, depois imprima! Use 'let' e '+'"
                    ),
                ]
                
                for exercicio in exercicios:
                    db.session.add(exercicio)
                
                db.session.commit()
                print("✅ Dados iniciais criados com sucesso!")
        except Exception as e:
            print(f"❌ Erro na inicialização do banco: {str(e)}")
            db.session.rollback()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)