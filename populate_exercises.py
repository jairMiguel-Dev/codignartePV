import json
from app import app, db
from models import Exercicio
from datetime import datetime
import random

class ExerciseGenerator:
    """Gerador sofisticado de exercícios com IA simulada"""
    
    THEMES = {
        'brasil': ['carnaval', 'futebol', 'samba', 'café', 'açaí', 'capoeira', 'feijoada'],
        'tech': ['startup', 'hackathon', 'blockchain', 'machine learning', 'IoT'],
        'games': ['minecraft', 'roblox', 'fortnite', 'valorant', 'league of legends'],
        'vida_real': ['uber', 'ifood', 'nubank', 'whatsapp', 'instagram']
    }
    
    @staticmethod
    def generate_contextual_hint(pergunta, resposta):
        """Gera dicas contextuais inteligentes baseadas no conteúdo"""
        hints = {
            'parseInt': '🤔 Pense em "parse" como analisar e "Int" como inteiro!',
            'push': '📦 Imagine empurrando um item para o final da fila!',
            'function': '🔧 Funções são como ferramentas que executam tarefas!',
            'return': '↩️ É como devolver um resultado para quem pediu!',
            'let': '🎯 "Let" em inglês significa "deixe" - deixe esta variável existir!',
            'const': '🏛️ Constante é como um monumento - não muda!',
            'await': '⏳ "Aguarde" até a promessa ser cumprida!',
            'async': '⚡ Assíncrono = não precisa esperar na fila!'
        }
        return hints.get(resposta, '💡 Tente pensar no conceito por trás da operação!')
    
    @staticmethod
    def generate_real_world_analogy(teoria):
        """Adiciona analogias do mundo real para melhor aprendizado"""
        analogies = [
            "É como pedir um Uber - você chama e espera ele chegar!",
            "Pense nisso como enviar uma mensagem no WhatsApp!",
            "Imagine que é como fazer um pedido no iFood!",
            "É tipo jogar um game - cada ação tem uma consequência!",
            "Pense como organizar sua playlist do Spotify!"
        ]
        return teoria + " " + random.choice(analogies)

def populate_exercises():
    """População sofisticada do banco com exercícios inovadores"""
    print("🚀 INICIANDO POPULAÇÃO AVANÇADA DE EXERCÍCIOS...")
    print("=" * 60)
    
    with app.app_context():
        # Limpar exercícios existentes para recriação completa
        try:
            deleted_count = Exercicio.query.delete()
            db.session.commit()
            print(f"🧹 {deleted_count} exercícios antigos removidos")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao limpar exercícios: {str(e)}")
            return

        generator = ExerciseGenerator()
        
        # EXERCÍCIOS PREMIUM INOVADORES - Conteúdo Exclusivo
        premium_exercises = [
            {
                'pergunta': '🔥 DOM: Crie um efeito de digitação como ChatGPT',
                'codigo_exemplo': 'async function typeWriter(elemento, texto) {\n  for (let i = 0; i < texto.length; i++) {\n    elemento.___ += texto[i];\n    await new Promise(resolve => setTimeout(resolve, 50));\n  }\n}',
                'resposta_correta': 'textContent',
                'nivel': 'avancado',
                'teoria': generator.generate_real_world_analogy('textContent é mais performático que innerHTML para texto puro. Imagine cada letra aparecendo como numa máquina de escrever digital!'),
                'premium': True,
                'modulo': 'dom_manipulation',
                'ordem_no_modulo': 1,
                'dica': generator.generate_contextual_hint('textContent', 'textContent'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🎮 Game Dev: Detecte colisão entre dois elementos',
                'codigo_exemplo': 'function detectarColisão(elemento1, elemento2) {\n  const rect1 = elemento1.___();\n  const rect2 = elemento2.getBoundingClientRect();\n  return !(rect1.right < rect2.left || rect1.left > rect2.right);\n}',
                'resposta_correta': 'getBoundingClientRect',
                'nivel': 'avancado',
                'teoria': generator.generate_real_world_analogy('getBoundingClientRect() retorna as coordenadas exatas de um elemento na tela. É como um GPS para elementos HTML!'),
                'premium': True,
                'modulo': 'dom_manipulation',
                'ordem_no_modulo': 2,
                'dica': generator.generate_contextual_hint('getBoundingClientRect', 'getBoundingClientRect'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🤖 IA: Crie um chatbot com respostas inteligentes',
                'codigo_exemplo': 'class Chatbot {\n  constructor() {\n    this.respostas = {\n      "ola": "Olá! Como posso ajudar?",\n      "nome": "Sou o BotCodignarte!"\n    };\n  }\n  responder(mensagem) {\n    return this.respostas[mensagem.___()] || "Não entendi!";\n  }\n}',
                'resposta_correta': 'toLowerCase',
                'nivel': 'avancado',
                'teoria': generator.generate_real_world_analogy('toLowerCase() garante que o input do usuário seja padronizado. É como um tradutor que entende tanto "OLA" quanto "ola"!'),
                'premium': True,
                'modulo': 'programacao_assincrona',
                'ordem_no_modulo': 1,
                'dica': generator.generate_contextual_hint('toLowerCase', 'toLowerCase'),
                'tipo': 'completion'
            },
            {
                'pergunta': '📊 Data Science: Analise sentimentos de texto',
                'codigo_exemplo': 'function analisarSentimento(texto) {\n  const positivas = ["amo", "incrível", "ótimo"];\n  const negativas = ["odeio", "horrível", "ruim"];\n  return positivas.___(palavra => texto.includes(palavra)) ? "positivo" : "negativo";\n}',
                'resposta_correta': 'some',
                'nivel': 'avancado',
                'teoria': generator.generate_real_world_analogy('some() verifica se pelo menos um elemento atende à condição. É como um detector de palavras-chave em reviews!'),
                'premium': True,
                'modulo': 'arrays_objetos',
                'ordem_no_modulo': 1,
                'dica': generator.generate_contextual_hint('some', 'some'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🎵 Spotify: Crie um player de música virtual',
                'codigo_exemplo': 'class MusicPlayer {\n  constructor() {\n    this.playlist = [];\n    this.currentIndex = 0;\n  }\n  adicionarMusica(musica) {\n    this.playlist.___(musica);\n  }\n}',
                'resposta_correta': 'push',
                'nivel': 'intermediario',
                'teoria': generator.generate_real_world_analogy('push() adiciona elementos ao final do array. É como adicionar músicas ao final da sua playlist!'),
                'premium': True,
                'modulo': 'arrays_objetos',
                'ordem_no_modulo': 2,
                'dica': generator.generate_contextual_hint('push', 'push'),
                'tipo': 'completion'
            }
        ]

        # EXERCÍCIOS FREEMIUM CRIATIVOS
        freemium_exercises = [
            {
                'pergunta': '🛍️ Ifood: Calcule o total do pedido',
                'codigo_exemplo': 'function calcularTotal(itens) {\n  let total = 0;\n  for (let item of itens) {\n    total += item.___;\n  }\n  return total;\n}',
                'resposta_correta': 'preco',
                'nivel': 'iniciante',
                'teoria': generator.generate_real_world_analogy('Acesse propriedades de objetos usando ponto. É como ver o preço de cada item no cardápio!'),
                'premium': False,
                'modulo': 'arrays_objetos',
                'ordem_no_modulo': 3,
                'dica': generator.generate_contextual_hint('preco', 'preco'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🚗 Uber: Calcule tempo de viagem',
                'codigo_exemplo': 'function calcularTempo(distancia, velocidade) {\n  return distancia / ___;\n}',
                'resposta_correta': 'velocidade',
                'nivel': 'iniciante',
                'teoria': generator.generate_real_world_analogy('Use variáveis nos cálculos. É como calcular quanto tempo leva uma corrida de Uber!'),
                'premium': False,
                'modulo': 'variaveis_operadores',
                'ordem_no_modulo': 1,
                'dica': generator.generate_contextual_hint('velocidade', 'velocidade'),
                'tipo': 'completion'
            },
            {
                'pergunta': '📱 Nubank: Verifique saldo suficiente',
                'codigo_exemplo': 'function podeComprar(saldo, preco) {\n  ___ saldo >= preco;\n}',
                'resposta_correta': 'return',
                'nivel': 'iniciante',
                'teoria': generator.generate_real_world_analogy('Funções retornam resultados. É como o Nubank verificando se você tem saldo para uma compra!'),
                'premium': False,
                'modulo': 'funcoes',
                'ordem_no_modulo': 1,
                'dica': generator.generate_contextual_hint('return', 'return'),
                'tipo': 'completion'
            },
            {
                'pergunta': '⚽ Futebol: Controle placar do jogo',
                'codigo_exemplo': 'let placar = { timeA: 0, timeB: 0 };\nfunction marcarGol(time) {\n  placar[time] ___;\n}',
                'resposta_correta': '++',
                'nivel': 'iniciante',
                'teoria': generator.generate_real_world_analogy('O operador ++ incrementa valores. É como marcar um gol e aumentar o placar!'),
                'premium': False,
                'modulo': 'variaveis_operadores',
                'ordem_no_modulo': 2,
                'dica': generator.generate_contextual_hint('++', '++'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🎯 Quiz: Verifique resposta correta',
                'codigo_exemplo': 'function verificarResposta(respostaUsuario, respostaCorreta) {\n  return respostaUsuario.___() === respostaCorreta.toLowerCase();\n}',
                'resposta_correta': 'toLowerCase',
                'nivel': 'intermediario',
                'teoria': generator.generate_real_world_analogy('toLowerCase() padroniza texto. É como um quiz que aceita "Verdadeiro" ou "verdadeiro"!'),
                'premium': False,
                'modulo': 'funcoes',
                'ordem_no_modulo': 2,
                'dica': generator.generate_contextual_hint('toLowerCase', 'toLowerCase'),
                'tipo': 'completion'
            },
            {
                'pergunta': '📈 Investimentos: Calcule rendimentos',
                'codigo_exemplo': 'function calcularRendimento(capital, taxa, tempo) {\n  return capital * Math.___(1 + taxa, tempo);\n}',
                'resposta_correta': 'pow',
                'nivel': 'intermediario',
                'teoria': generator.generate_real_world_analogy('Math.pow() calcula potências. É como calcular juros compostos nas suas economias!'),
                'premium': False,
                'modulo': 'variaveis_operadores',
                'ordem_no_modulo': 3,
                'dica': generator.generate_contextual_hint('pow', 'pow'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🎮 Game: Movimente personagem no canvas',
                'codigo_exemplo': 'function moverDireita(personagem) {\n  personagem.x += personagem.___;\n}',
                'resposta_correta': 'velocidade',
                'nivel': 'intermediario',
                'teoria': generator.generate_real_world_analogy('Propriedades de objetos controlam comportamento. É como mover um personagem em um jogo!'),
                'premium': False,
                'modulo': 'arrays_objetos',
                'ordem_no_modulo': 4,
                'dica': generator.generate_contextual_hint('velocidade', 'velocidade'),
                'tipo': 'completion'
            },
            {
                'pergunta': '🤖 Automação: Processe lista de tarefas',
                'codigo_exemplo': 'const tarefas = ["estudar", "trabalhar", "descansar"];\ntarefas.___(tarefa => console.log(`Fazendo: ${tarefa}`));',
                'resposta_correta': 'forEach',
                'nivel': 'intermediario',
                'teoria': generator.generate_real_world_analogy('forEach executa uma função para cada elemento. É como uma lista de tarefas sendo processada automaticamente!'),
                'premium': False,
                'modulo': 'arrays_objetos',
                'ordem_no_modulo': 5,
                'dica': generator.generate_contextual_hint('forEach', 'forEach'),
                'tipo': 'completion'
            }
        ]

        # EXERCÍCIOS DESAFIO FINAL POR MÓDULO
        challenge_exercises = [
            {
                'pergunta': '🏆 DESAFIO FINAL: Crie um sistema de carrinho de compras',
                'codigo_exemplo': 'class Carrinho {\n  constructor() {\n    this.itens = [];\n    this.total = 0;\n  }\n  adicionarItem(produto) {\n    this.itens.___(produto);\n    this.total += produto.preco;\n  }\n}',
                'resposta_correta': 'push',
                'nivel': 'intermediario',
                'teoria': generator.generate_real_world_analogy('Junte tudo que aprendeu: arrays, objetos, funções e métodos! É como criar um carrinho de compras completo.'),
                'premium': False,
                'modulo': 'arrays_objetos',
                'ordem_no_modulo': 6,
                'dica': 'Lembre-se: push adiciona ao array!',
                'tipo': 'completion',
                'eh_desafio_final': True
            },
            {
                'pergunta': '🏆 DESAFIO FINAL: Sistema de autenticação com async/await',
                'codigo_exemplo': 'async function login(email, senha) {\n  try {\n    const resposta = ___ fetch("/api/login", {\n      method: "POST",\n      body: JSON.stringify({ email, senha })\n    });\n    return await resposta.json();\n  } catch (erro) {\n    console.log("Erro:", erro);\n  }\n}',
                'resposta_correta': 'await',
                'nivel': 'avancado',
                'teoria': generator.generate_real_world_analogy('Async/await + fetch + tratamento de erros = sistema profissional! É como fazer login em qualquer app moderno.'),
                'premium': True,
                'modulo': 'programacao_assincrona',
                'ordem_no_modulo': 6,
                'dica': 'Não esqueça do await antes do fetch!',
                'tipo': 'completion',
                'eh_desafio_final': True
            }
        ]

        # COMBINAR TODOS OS EXERCÍCIOS
        all_exercises = freemium_exercises + premium_exercises + challenge_exercises

        try:
            print("🎨 CRIANDO EXERCÍCIOS INOVADORES...")
            created_count = 0
            
            for exercise_data in all_exercises:
                # Garantir valores padrão
                exercise_data.setdefault('tipo', 'completion')
                exercise_data.setdefault('opcoes', None)
                exercise_data.setdefault('eh_desafio_final', False)
                
                exercicio = Exercicio(**exercise_data)
                db.session.add(exercicio)
                created_count += 1
                
                # Feedback visual
                premium_icon = "🔥" if exercise_data['premium'] else "🎯"
                print(f"   {premium_icon} {exercise_data['pergunta'][:40]}...")
            
            db.session.commit()
            
            # ESTATÍSTICAS DETALHADAS
            print("\n" + "=" * 60)
            print("📊 RELATÓRIO DE POPULAÇÃO")
            print("=" * 60)
            
            total = Exercicio.query.count()
            freemium = Exercicio.query.filter_by(premium=False).count()
            premium = Exercicio.query.filter_by(premium=True).count()
            
            # Estatísticas por módulo
            modulos = ['variaveis_operadores', 'estruturas_controle', 'funcoes', 
                      'arrays_objetos', 'programacao_assincrona', 'dom_manipulation']
            
            print(f"\n🏗️  EXERCÍCIOS CRIADOS: {created_count}")
            print(f"💰 FREEMIUM: {freemium} exercícios")
            print(f"🔥 PREMIUM: {premium} exercícios")
            
            print("\n📁 DISTRIBUIÇÃO POR MÓDULO:")
            for modulo in modulos:
                count = Exercicio.query.filter_by(modulo=modulo).count()
                premium_count = Exercicio.query.filter_by(modulo=modulo, premium=True).count()
                freemium_count = count - premium_count
                print(f"   📂 {modulo}: {count} total ({freemium_count} 🎯 + {premium_count} 🔥)")
            
            # Estatísticas por nível
            print("\n🎯 DISTRIBUIÇÃO POR NÍVEL:")
            for nivel in ['iniciante', 'intermediario', 'avancado']:
                count = Exercicio.query.filter_by(nivel=nivel).count()
                print(f"   ⭐ {nivel}: {count} exercícios")
            
            print(f"\n✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🎉 SEU MVP AGORA TEM EXERCÍCIOS SOFISTICADOS E INOVADORES!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERRO CRÍTICO: {str(e)}")
            raise

if __name__ == '__main__':
    populate_exercises()