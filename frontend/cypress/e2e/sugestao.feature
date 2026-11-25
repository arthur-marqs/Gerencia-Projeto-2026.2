# language: pt
@US13 @R2 @S3 @regressao
Funcionalidade: Gerar sequência sugerida de produção
  Como Planejador de Produção
  Quero gerar uma sugestão para as ordens selecionadas
  Para reduzir o tempo estimado de setup entre famílias

  Contexto:
    Dado que o Planejador está autenticado para gerar sugestões

  @CT79
  Cenário: CT-79 Reduzir o setup entre famílias com tempos direcionais
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    Quando selecionar "OP01, OP02, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então "OP01, OP03" devem vir antes de "OP02" com setup total de 20 minutos

  @CT80
  Cenário: CT-80 Gerar sugestão para uma única ordem
    Quando selecionar "OP01" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP01" com setup total de 0 minutos

  @CT81
  Cenário: CT-81 Sugerir somente as ordens do subconjunto selecionado
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    Quando selecionar "OP02, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então a sugestão deve conter exatamente "OP02, OP03" com setup total de 20 minutos

  @CT82 @excecao
  Cenário: CT-82 Bloquear a geração quando o produto não tem família
    Quando selecionar "OP05" para a sugestão
    E solicitar a sequência sugerida
    Então a geração deve ser rejeitada com "A ordem OP05 usa o produto PROD-OP05 (Produto OP05), que está sem família associada."
    E nenhuma sugestão deve ter sido gravada

  @CT83 @excecao
  Cenário: CT-83 Bloquear a geração quando falta um sentido da troca
    Dado que somente o tempo de A para B está cadastrado com 20 minutos
    Quando selecionar "OP01, OP02, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então a geração deve ser rejeitada com "Tempo de setup de B → A sem cadastro."
    E nenhuma sugestão deve ter sido gravada

  @CT84
  Cenário: CT-84 Gerar sugestão após corrigir as pendências
    Dado que somente o tempo de A para B está cadastrado com 20 minutos
    Quando selecionar "OP01, OP02, OP03, OP05" para a sugestão
    E solicitar a sequência sugerida
    Então a geração deve ser rejeitada com "A ordem OP05 usa o produto PROD-OP05 (Produto OP05), que está sem família associada."
    E o erro de geração também deve indicar "Tempo de setup de B → A sem cadastro."
    E nenhuma sugestão deve ter sido gravada
    Quando associar o produto de "OP05" à família A e cadastrar B para A com 30 minutos
    E solicitar a sequência sugerida
    Então a sugestão deve conter exatamente "OP01, OP02, OP03, OP05" com setup total de 20 minutos
    E deve existir uma única sugestão gravada com 4 itens

  @CT85 @excecao @seguranca
  Cenário: CT-85 Negar a solicitação direta à API para o Operador
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que existe um planejamento manual para "OP01, OP02, OP03"
    E que já existe uma sugestão para esse planejamento
    Quando o Operador solicitar a mesma sugestão diretamente à API
    Então a API deve negar a geração, preservar os registros e retornar somente a mensagem de acesso negado

  @CT107 @smoke
  Cenário: CT-107 Gerar uma sugestão antes de salvar o planejamento manual
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que ainda não existe planejamento manual
    Quando selecionar "OP01, OP02, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então "OP01, OP03" devem vir antes de "OP02" com setup total de 20 minutos
    E nenhum planejamento manual deve ser criado automaticamente

  @CT108
  Cenário: CT-108 Preservar a seleção que já tem o menor setup
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    Quando selecionar "OP03, OP01, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP03, OP01, OP02" com setup total de 20 minutos

  @CT109
  Cenário: CT-109 Preservar a seleção no empate entre os sentidos
    Dado que os tempos são de 20 minutos de A para B e 20 minutos de B para A
    Quando selecionar "OP01, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP01, OP02" com setup total de 20 minutos

  @CT110 @smoke
  Cenário: CT-110 Recuperar a sugestão e preservar o planejamento manual
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que existe um planejamento manual para "OP01, OP02, OP03"
    Quando abrir o planejamento manual para editar
    E solicitar a sequência sugerida
    Então "OP01, OP03" devem vir antes de "OP02" com setup total de 20 minutos
    Quando recarregar a tela e consultar a sugestão do planejamento
    Então a mesma sugestão deve ser recuperada com as ordens manuais preservadas

  @CT111 @excecao
  Cenário: CT-111 Bloquear a geração sem ordens selecionadas
    Quando abrir o planejamento para sugerir sem selecionar ordens
    E solicitar a sequência sugerida
    Então a tela deve pedir a seleção de pelo menos uma ordem
    E nenhuma sugestão deve ter sido gravada

  @CT112
  Cenário: CT-112 Manter a seleção de várias ordens da mesma família
    Dado que não há tempos de troca cadastrados
    Quando selecionar "OP04, OP01, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP04, OP01, OP03" com setup total de 0 minutos
