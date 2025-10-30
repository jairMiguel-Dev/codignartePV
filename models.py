from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import json
import secrets
import string

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    vidas = db.Column(db.Integer, default=3)
    ultima_regeneracao = db.Column(db.DateTime, server_default=func.now())
    data_criacao = db.Column(db.DateTime, server_default=func.now())
    premium = db.Column(db.Boolean, default=False)
    data_inicio_premium = db.Column(db.DateTime)
    data_expiracao_premium = db.Column(db.DateTime)
    premium_cancelado = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(255))
    
    # Novos campos para controle de uso
    vidas_compradas = db.Column(db.Integer, default=0)
    vidas_utilizadas_compradas = db.Column(db.Integer, default=0)
    nivel_atual = db.Column(db.String(50), default='iniciante')
    modulo_atual = db.Column(db.String(100), default='variaveis_operadores')
    
    @property
    def is_premium_active(self):
        """Verifica se o usuário tem premium ativo (não cancelado e não expirado)"""
        if not self.premium:
            return False
        if self.premium_cancelado:
            return False
        if self.data_expiracao_premium and datetime.utcnow() > self.data_expiracao_premium:
            return False
        return True
    
    def tempo_para_proxima_vida(self):
        if self.is_premium_active:
            return 0
            
        if self.vidas >= 3:
            return 0
            
        agora = datetime.utcnow()
        
        if not self.ultima_regeneracao:
            return 1800
        
        if self.ultima_regeneracao.tzinfo is not None:
            ultima_regeneracao_naive = self.ultima_regeneracao.replace(tzinfo=None)
        else:
            ultima_regeneracao_naive = self.ultima_regeneracao
            
        tempo_decorrido = agora - ultima_regeneracao_naive
        segundos_passados = tempo_decorrido.total_seconds()
        
        tempo_restante = 1800 - segundos_passados
        
        if tempo_restante < 0:
            return 0
        return int(tempo_restante)
    
    def regenerar_vidas(self):
        if self.is_premium_active:
            return
            
        if self.vidas >= 3:
            return
            
        agora = datetime.utcnow()
        
        if not self.ultima_regeneracao:
            self.ultima_regeneracao = agora
            return
        
        if self.ultima_regeneracao.tzinfo is not None:
            ultima_regeneracao_naive = self.ultima_regeneracao.replace(tzinfo=None)
        else:
            ultima_regeneracao_naive = self.ultima_regeneracao
            
        tempo_decorrido = agora - ultima_regeneracao_naive
        
        if tempo_decorrido.total_seconds() >= 1800:
            vidas_regeneradas = int(tempo_decorrido.total_seconds() // 1800)
            self.vidas = min(3, self.vidas + vidas_regeneradas)
            self.ultima_regeneracao = agora

    def verificar_premium_expirado(self):
        """Verifica se o premium expirou e atualiza o status"""
        if self.premium and self.data_expiracao_premium:
            if datetime.utcnow() > self.data_expiracao_premium:
                self.premium = False
                self.premium_cancelado = False
                self.data_inicio_premium = None
                self.data_expiracao_premium = None
                return True
        return False

    def pode_reembolso_assinatura(self):
        """Verifica se a assinatura pode ser reembolsada (dentro de 7 dias)"""
        if not self.data_inicio_premium:
            return False
        
        dias_decorridos = (datetime.utcnow() - self.data_inicio_premium).days
        return dias_decorridos <= 7

    def get_vidas_compradas_nao_utilizadas(self):
        """Retorna quantas vidas compradas ainda não foram utilizadas"""
        return max(0, self.vidas_compradas - self.vidas_utilizadas_compradas)

    def usar_vida_comprada(self):
        """Registra o uso de uma vida comprada"""
        if self.vidas_utilizadas_compradas < self.vidas_compradas:
            self.vidas_utilizadas_compradas += 1
            return True
        return False

    def adicionar_vidas_compradas(self, quantidade):
        """Adiciona vidas compradas ao total"""
        self.vidas_compradas += quantidade

    def get_status_reembolso(self):
        """Retorna o status atual do reembolso se aplicável"""
        if not self.premium_cancelado:
            return None
            
        transacao = Transacao.query.filter_by(
            usuario_id=self.id, 
            tipo='assinatura'
        ).order_by(Transacao.data_transacao.desc()).first()
        
        if transacao and transacao.status_reembolso:
            return transacao.status_reembolso
        return None

class Exercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pergunta = db.Column(db.Text, nullable=False)
    codigo_exemplo = db.Column(db.Text)
    resposta_correta = db.Column(db.String(500), nullable=False)
    nivel = db.Column(db.String(50), nullable=False)
    teoria = db.Column(db.Text)
    premium = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.String(20), default='completion')
    opcoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, server_default=func.now())
    
    # Novos campos para módulos
    modulo = db.Column(db.String(100))
    ordem_no_modulo = db.Column(db.Integer, default=0)
    eh_desafio_final = db.Column(db.Boolean, default=False)
    dica = db.Column(db.Text)
    
    def get_opcoes(self):
        if self.opcoes:
            return json.loads(self.opcoes)
        return []

class Progresso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicio.id'), nullable=False)
    data_conclusao = db.Column(db.DateTime, server_default=func.now())
    tentativas = db.Column(db.Integer, default=1)
    
    usuario = db.relationship('Usuario', backref=db.backref('progresso', lazy=True))
    exercicio = db.relationship('Exercicio', backref=db.backref('completado_por', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('usuario_id', 'exercicio_id', name='unique_progresso'),)

class ModuloConcluido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    modulo = db.Column(db.String(100), nullable=False)
    data_conclusao = db.Column(db.DateTime, server_default=func.now())
    
    usuario = db.relationship('Usuario', backref=db.backref('modulos_concluidos', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('usuario_id', 'modulo', name='unique_modulo_concluido'),)

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # assinatura, vidas_1, vidas_3, vidas_5
    valor = db.Column(db.Float, nullable=False)
    detalhes = db.Column(db.String(500))
    data_transacao = db.Column(db.DateTime, server_default=func.now())
    status = db.Column(db.String(20), default='pendente')
    stripe_session_id = db.Column(db.String(255))
    stripe_payment_intent = db.Column(db.String(255))
    stripe_refund_id = db.Column(db.String(255))
    id_publico = db.Column(db.String(20), unique=True)
    
    # Campos para controle de uso do produto
    produto_utilizado = db.Column(db.Boolean, default=False)
    quantidade_produto = db.Column(db.Integer, default=0)  # Para vidas: quantidade comprada
    quantidade_utilizada = db.Column(db.Integer, default=0)  # Quantidade já utilizada
    
    # Campos para rastreamento de reembolso
    status_reembolso = db.Column(db.String(20), default='nao_solicitado')
    data_solicitacao_reembolso = db.Column(db.DateTime)
    data_processamento_reembolso = db.Column(db.DateTime)
    motivo_reembolso = db.Column(db.String(500))
    valor_reembolsado = db.Column(db.Float, default=0.0)
    tracking_reembolso = db.Column(db.Text)
    
    usuario = db.relationship('Usuario', backref=db.backref('transacoes', lazy=True))
    
    def gerar_id_publico(self):
        caracteres = string.ascii_uppercase + string.digits
        return 'CDG' + ''.join(secrets.choice(caracteres) for _ in range(7))
    
    def adicionar_tracking_reembolso(self, status, mensagem, dados=None):
        """Adiciona uma entrada no histórico de tracking do reembolso"""
        try:
            tracking = self.tracking_reembolso or '[]'
            historico = json.loads(tracking)
            
            entrada = {
                'timestamp': datetime.utcnow().isoformat(),
                'status': status,
                'mensagem': mensagem,
                'dados': dados or {}
            }
            
            historico.append(entrada)
            self.tracking_reembolso = json.dumps(historico, ensure_ascii=False)
            
        except Exception as e:
            print(f"Erro ao adicionar tracking: {str(e)}")
    
    def get_tracking_reembolso(self):
        """Retorna o histórico de tracking do reembolso"""
        try:
            if self.tracking_reembolso:
                return json.loads(self.tracking_reembolso)
        except:
            pass
        return []
    
    def pode_reembolsar(self):
        """Verifica se a transação pode ser reembolsada baseada no uso do produto"""
        if self.tipo == 'assinatura':
            # Para assinatura: reembolso total apenas dentro de 7 dias
            dias_decorridos = (datetime.utcnow() - self.data_transacao).days
            return dias_decorridos <= 7 and not self.produto_utilizado
        
        elif self.tipo.startswith('vidas_'):
            # Para vidas: reembolso proporcional baseado no uso dentro de 7 dias
            dias_decorridos = (datetime.utcnow() - self.data_transacao).days
            if dias_decorridos > 7:
                return False
            
            vidas_nao_utilizadas = self.quantidade_produto - self.quantidade_utilizada
            return vidas_nao_utilizadas > 0
        
        return False
    
    def calcular_valor_reembolso(self):
        """Calcula o valor do reembolso baseado no uso do produto"""
        if self.tipo == 'assinatura':
            # Assinatura: reembolso total se dentro de 7 dias e não utilizou benefícios premium
            if self.pode_reembolsar():
                return self.valor
            return 0.0
        
        elif self.tipo.startswith('vidas_'):
            # Vidas: reembolso proporcional às vidas não utilizadas
            if not self.pode_reembolsar():
                return 0.0
            
            vidas_nao_utilizadas = self.quantidade_produto - self.quantidade_utilizada
            if vidas_nao_utilizadas <= 0:
                return 0.0
            
            # Calcular valor proporcional (descontando taxas stripe não reembolsáveis)
            valor_por_vida = self.valor / self.quantidade_produto
            valor_reembolso = valor_por_vida * vidas_nao_utilizadas
            
            # Aplicar desconto das taxas stripe (aproximadamente 3.2%)
            valor_reembolso = valor_reembolso * 0.968
            
            return round(valor_reembolso, 2)
        
        return 0.0
    
    def solicitar_reembolso(self, motivo=None):
        """Marca a transação para reembolso"""
        self.status_reembolso = 'solicitado'
        self.data_solicitacao_reembolso = datetime.utcnow()
        self.motivo_reembolso = motivo
        self.valor_reembolsado = self.calcular_valor_reembolso()
        
        self.adicionar_tracking_reembolso(
            'solicitado',
            'Reembolso solicitado pelo usuário',
            {
                'motivo': motivo,
                'valor_reembolsado': self.valor_reembolsado,
                'valor_original': self.valor
            }
        )
    
    def processar_reembolso(self, refund_id):
        """Marca o reembolso como em processamento"""
        self.status_reembolso = 'processando'
        self.stripe_refund_id = refund_id
        
        self.adicionar_tracking_reembolso(
            'processando',
            'Reembolso sendo processado pela Stripe',
            {'refund_id': refund_id}
        )
    
    def completar_reembolso(self, dados_reembolso):
        """Marca o reembolso como completado"""
        self.status_reembolso = 'completado'
        self.data_processamento_reembolso = datetime.utcnow()
        self.status = 'reembolsada'
        
        self.adicionar_tracking_reembolso(
            'completado',
            'Reembolso processado com sucesso',
            {'dados_reembolso': dados_reembolso}
        )
    
    def falhar_reembolso(self, erro):
        """Marca o reembolso como falhou"""
        self.status_reembolso = 'falhou'
        
        self.adicionar_tracking_reembolso(
            'falhou',
            'Falha no processamento do reembolso',
            {'erro': str(erro)}
        )
    
    def marcar_como_utilizado(self):
        """Marca que o produto foi utilizado"""
        self.produto_utilizado = True
    
    def registrar_uso_vida(self):
        """Registra o uso de uma vida comprada"""
        if self.quantidade_utilizada < self.quantidade_produto:
            self.quantidade_utilizada += 1
            return True
        return False