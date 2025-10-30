import json
from app import app, db
from models import Exercicio
from datetime import datetime

def populate_exercises():
    print("🏗️ Iniciando população do banco de dados com exercícios...")
    
    # Verificar se já existem exercícios para não duplicar
    existing_count = Exercicio.query.count()
    if existing_count > 6:  # Já temos os exercícios iniciais
        print(f"✅ Banco já possui {existing_count} exercícios. Pulando população.")
        return
    
    exercicios = [
        # ========== EXERCÍCIOS FREEMIUM ==========
        {
            'pergunta': 'Qual método converte uma string em número inteiro?',
            'codigo_exemplo': 'let numero = ___("42");\nconsole.log(numero); // 42',
            'resposta_correta': 'parseInt',
            'nivel': 'iniciante',
            'teoria': 'O método parseInt() converte uma string em um número inteiro. Ele para a leitura quando encontra um caractere não numérico.',
            'teoria_audio': '/static/audio/parseint.mp3',
            'premium': False,
            'tipo': 'completion'
        },
        {
            'pergunta': 'Como acessar o primeiro elemento de um array chamado "frutas"?',
            'codigo_exemplo': 'let frutas = ["maçã", "banana", "laranja"];\nlet primeira = frutas[___];',
            'resposta_correta': '0',
            'nivel': 'iniciante',
            'teoria': 'Arrays em JavaScript são indexados começando em 0. O primeiro elemento está na posição 0, o segundo na 1, e assim por diante.',
            'teoria_audio': '/static/audio/arrays.mp3',
            'premium': False,
            'tipo': 'completion'
        },
        {
            'pergunta': 'Qual será o output do código: console.log("10" + 5)?',
            'codigo_exemplo': 'console.log("10" + 5);',
            'resposta_correta': '105',
            'nivel': 'iniciante',
            'teoria': 'O operador "+" com string e número realiza concatenação. O número é convertido para string e as duas são juntadas.',
            'teoria_audio': '/static/audio/concatenacao.mp3',
            'premium': False,
            'tipo': 'output'
        },
        {
            'pergunta': 'Como verificar se uma variável "idade" é maior ou igual a 18?',
            'codigo_exemplo': 'let idade = 20;\nif (idade ___ 18) {\n  console.log("Maior de idade");\n}',
            'resposta_correta': '>=',
            'nivel': 'iniciante',
            'teoria': 'O operador ">=" verifica se o valor da esquerda é maior ou igual ao valor da direita.',
            'teoria_audio': '/static/audio/maior_igual.mp3',
            'premium': False,
            'tipo': 'completion'
        },
        {
            'pergunta': 'Qual método adiciona um elemento ao final de um array?',
            'codigo_exemplo': 'let numeros = [1, 2, 3];\nnumeros.___(4);\n// numeros agora é [1, 2, 3, 4]',
            'resposta_correta': 'push',
            'nivel': 'iniciante',
            'teoria': 'O método push() adiciona um ou mais elementos ao final de um array e retorna o novo comprimento do array.',
            'teoria_audio': '/static/audio/push.mp3',
            'premium': False,
            'tipo': 'completion'
        },
        {
            'pergunta': 'Qual é a diferença entre == e === em JavaScript?',
            'codigo_exemplo': '',
            'resposta_correta': '== compara valor, === compara valor e tipo',
            'nivel': 'intermediario',
            'teoria': 'O operador "==" faz conversão de tipo antes da comparação (coerção), enquanto "===" não faz conversão e exige que valor E tipo sejam iguais.',
            'teoria_audio': '/static/audio/igualdade.mp3',
            'premium': False,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                '== compara valor, === compara valor e tipo',
                '== compara tipo, === compara valor',
                'Não há diferença',
                '== é mais rápido que ==='
            ])
        },
        {
            'pergunta': 'Como criar um objeto vazio em JavaScript?',
            'codigo_exemplo': '',
            'resposta_correta': 'let obj = {};',
            'nivel': 'iniciante',
            'teoria': 'Objetos em JavaScript podem ser criados usando chaves {}. Esta é a sintaxe de objeto literal, a forma mais comum de criar objetos.',
            'teoria_audio': '/static/audio/objetos.mp3',
            'premium': False,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'let obj = {};',
                'let obj = [];',
                'let obj = new Object;',
                'let obj = Object.create();'
            ])
        },
        {
            'pergunta': 'Qual método transforma um array em string?',
            'codigo_exemplo': 'let frutas = ["maçã", "banana"];\nlet resultado = frutas.___(",");\n// resultado: "maçã,banana"',
            'resposta_correta': 'join',
            'nivel': 'intermediario',
            'teoria': 'O método join() une todos os elementos de um array em uma string, usando um separador especificado.',
            'teoria_audio': '/static/audio/join.mp3',
            'premium': False,
            'tipo': 'completion'
        },

        # ========== EXERCÍCIOS PREMIUM (Conteúdo Exclusivo) ==========
        {
            'pergunta': 'Como funciona o Event Loop em JavaScript?',
            'codigo_exemplo': 'console.log("1");\nsetTimeout(() => console.log("2"), 0);\nconsole.log("3");\n// Qual a ordem de output?',
            'resposta_correta': '1, 3, 2',
            'nivel': 'avancado',
            'teoria': 'O Event Loop é o mecanismo que permite JavaScript ser assíncrono. Ele gerencia a call stack, task queue e microtask queue. Funções síncronas executam primeiro, depois microtasks (Promises), e finalmente macrotasks (setTimeout).',
            'teoria_audio': '/static/audio/event_loop.mp3',
            'premium': True,
            'tipo': 'output'
        },
        {
            'pergunta': 'O que é Closure em JavaScript e como funciona?',
            'codigo_exemplo': 'function criarContador() {\n  let count = 0;\n  return function() {\n    count++;\n    return count;\n  };\n}',
            'resposta_correta': 'Função que lembra do escopo onde foi criada',
            'nivel': 'avancado',
            'teoria': 'Closure é quando uma função tem acesso a variáveis de um escopo externo mesmo após esse escopo ter sido removido da call stack. Isso permite criar funções com "estado privado" e é fundamental para muitos padrões em JavaScript.',
            'teoria_audio': '/static/audio/closure.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Função que lembra do escopo onde foi criada',
                'Função que fecha outras funções',
                'Método para fechar janelas',
                'Tipo de loop infinito'
            ])
        },
        {
            'pergunta': 'Como funciona o Prototype Chain em JavaScript?',
            'codigo_exemplo': 'function Animal(nome) {\n  this.nome = nome;\n}\nAnimal.prototype.falar = function() {\n  console.log(this.nome + " faz um som");\n};',
            'resposta_correta': 'Mecanismo de herança baseado em protótipos',
            'nivel': 'avancado',
            'teoria': 'JavaScript usa herança prototipal. Cada objeto tem um protótipo interno que pode ter seu próprio protótipo, formando uma cadeia. Quando uma propriedade não é encontrada no objeto, a busca sobe pela cadeia de protótipos.',
            'teoria_audio': '/static/audio/prototype.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Mecanismo de herança baseado em protótipos',
                'Tipo de array especial',
                'Método para clonar objetos',
                'Sistema de versionamento'
            ])
        },
        {
            'pergunta': 'Qual a diferença entre call, apply e bind?',
            'codigo_exemplo': 'function saudacao(periodo, nome) {\n  console.log(`Boa ${periodo}, ${nome}!`);\n}',
            'resposta_correta': 'call e apply executam agora, bind retorna função',
            'nivel': 'avancado',
            'teoria': 'Todos três métodos permitem definir o valor de "this" em uma função. call() aceita argumentos separados, apply() aceita array de argumentos, e bind() retorna uma nova função com "this" definido, sem executar imediatamente.',
            'teoria_audio': '/static/audio/call_apply_bind.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'call e apply executam agora, bind retorna função',
                'Todos executam a função imediatamente',
                'bind é mais rápido que call e apply',
                'Não há diferença prática'
            ])
        },
        {
            'pergunta': 'Como funciona o Async/Await por baixo dos panos?',
            'codigo_exemplo': 'async function buscarDados() {\n  const resposta = await fetch(url);\n  const dados = await resposta.json();\n  return dados;\n}',
            'resposta_correta': 'Syntax sugar sobre Promises',
            'nivel': 'avancado',
            'teoria': 'Async/await é syntax sugar sobre Promises que torna o código assíncrono mais legível. Uma função async sempre retorna uma Promise, e await pausa a execução até que a Promise seja resolvida, sem bloquear o thread principal.',
            'teoria_audio': '/static/audio/async_await.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Syntax sugar sobre Promises',
                'Novo tipo de thread',
                'Método síncrono melhorado',
                'Substituto para callbacks'
            ])
        },
        {
            'pergunta': 'O que é Currying em JavaScript?',
            'codigo_exemplo': 'function soma(a) {\n  return function(b) {\n    return a + b;\n  };\n}',
            'resposta_correta': 'Técnica de transformar função multi-argumento em cadeia de funções de um argumento',
            'nivel': 'avancado',
            'teoria': 'Currying é uma técnica funcional onde uma função com múltiplos argumentos é transformada em uma sequência de funções, cada uma recebendo um único argumento. Isso permite composição de funções e aplicação parcial.',
            'teoria_audio': '/static/audio/currying.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Técnica de transformar função multi-argumento em cadeia de funções de um argumento',
                'Método para cozinhar dados',
                'Tipo de loop para arrays',
                'Padrão de design para objetos'
            ])
        },
        {
            'pergunta': 'Como funciona a Memoização para otimização de performance?',
            'codigo_exemplo': 'function memoize(fn) {\n  const cache = {};\n  return function(...args) {\n    const key = JSON.stringify(args);\n    if (cache[key]) return cache[key];\n    return cache[key] = fn.apply(this, args);\n  };\n}',
            'resposta_correta': 'Cache de resultados de funções pesadas',
            'nivel': 'avancado',
            'teoria': 'Memoização é uma técnica de otimização que armazena os resultados de chamadas de função caras e retorna o resultado em cache quando as mesmas entradas ocorrem novamente. É especialmente útil para funções recursivas ou com cálculos intensivos.',
            'teoria_audio': '/static/audio/memoization.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Cache de resultados de funções pesadas',
                'Técnica para memorizar código',
                'Método de compressão de dados',
                'Padrão para gerenciar memória'
            ])
        },
        {
            'pergunta': 'O que são Generators e como funcionam?',
            'codigo_exemplo': 'function* contadorInfinito() {\n  let i = 0;\n  while (true) {\n    yield i++;\n  }\n}',
            'resposta_correta': 'Funções que podem ser pausadas e retomadas',
            'nivel': 'avancado',
            'teoria': 'Generators são funções especiais que podem ser pausadas e retomadas. Eles usam a palavra-chave yield para retornar valores múltiplos ao longo do tempo. São úteis para lazy evaluation, iteradores customizados e controle assíncrono.',
            'teoria_audio': '/static/audio/generators.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Funções que podem ser pausadas e retomadas',
                'Funções que geram números aleatórios',
                'Método para criar arrays',
                'Tipo de loop para objetos'
            ])
        },
        {
            'pergunta': 'Como funciona o Web Workers API para multi-threading?',
            'codigo_exemplo': '// main.js\nconst worker = new Worker("worker.js");\nworker.postMessage("Hello");',
            'resposta_correta': 'Executa código JavaScript em thread separado',
            'nivel': 'avancado',
            'teoria': 'Web Workers permitem executar código JavaScript em threads em segundo plano, separados do thread principal da interface. Isso evita bloqueio da UI durante operações pesadas. Os workers se comunicam com o thread principal via mensagens.',
            'teoria_audio': '/static/audio/web_workers.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Executa código JavaScript em thread separado',
                'Trabalha com elementos da Web',
                'Método para criar servidores',
                'API para trabalhar com arquivos'
            ])
        },
        {
            'pergunta': 'O que é Tree Shaking e como otimiza bundles?',
            'codigo_exemplo': '// Webpack remove código não utilizado\nimport { func1, func2 } from "./module";\n// Se só func1 for usado, func2 é removido',
            'resposta_correta': 'Remoção de código não utilizado durante o build',
            'nivel': 'avancado',
            'teoria': 'Tree Shaking é uma técnica de otimização que remove código não utilizado (dead code) dos bundles finais. Funciona analisando o grafo de dependências e eliminando exportações que não são importadas em nenhum lugar da aplicação.',
            'teoria_audio': '/static/audio/tree_shaking.mp3',
            'premium': True,
            'tipo': 'multiple_choice',
            'opcoes': json.dumps([
                'Remoção de código não utilizado durante o build',
                'Técnica para organizar arquivos',
                'Método para cortar strings',
                'Padrão para estruturas de dados'
            ])
        }
    ]

    try:
        for exercicio_data in exercicios:
            # Verificar se o exercício já existe
            existente = Exercicio.query.filter_by(pergunta=exercicio_data['pergunta']).first()
            if not existente:
                exercicio = Exercicio(**exercicio_data)
                db.session.add(exercicio)
                print(f"✅ Adicionado: {exercicio_data['pergunta'][:50]}...")
        
        db.session.commit()
        total = Exercicio.query.count()
        print(f"🎉 População concluída! Total de exercícios no banco: {total}")
        
        # Estatísticas
        freemium = Exercicio.query.filter_by(premium=False).count()
        premium = Exercicio.query.filter_by(premium=True).count()
        multipla_escolha = Exercicio.query.filter(Exercicio.tipo == 'multiple_choice').count()
        
        print(f"📊 Estatísticas:")
        print(f"   - Freemium: {freemium} exercícios")
        print(f"   - Premium: {premium} exercícios")
        print(f"   - Múltipla escolha: {multipla_escolha} exercícios")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro durante a população: {str(e)}")
        raise

if __name__ == '__main__':
    with app.app_context():
        populate_exercises()