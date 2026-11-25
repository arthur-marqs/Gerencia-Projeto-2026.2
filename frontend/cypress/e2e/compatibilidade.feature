# language: pt
@US15 @R2 @S3 @regressao
Funcionalidade: Considerar compatibilidade entre produtos e máquinas
  Como Planejador de Produção
  Quero que as ordens sejam atribuídas a máquinas compatíveis
  Para evitar sequências de produção inviáveis

  Contexto:
    Dado que o Planejador está autenticado para gerar sugestões

  @US15_CT01 @smoke
  Cenário: Atribuir ordens a máquinas compatíveis diferentes
    Dado que existe uma máquina adicional "M02"
    E que o produto de "OP02" é compatível com "M02"
    Quando selecionar "OP01, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a sugestão deve apresentar as atribuições "OP01:M01, OP02:M02" com setup total de 0 minutos
    E deve existir uma única sugestão gravada com 2 itens

  @US15_CT02
  Cenário: Distribuir ordens entre máquinas compatíveis
    Dado que existe uma máquina adicional "M02"
    E que o produto de "OP01" é compatível com "M01, M02"
    E que o produto de "OP03" é compatível com "M01, M02"
    E que o produto de "OP04" é compatível com "M01, M02"
    Quando selecionar "OP01, OP03, OP04" para a sugestão
    E solicitar a sequência sugerida
    Então a sugestão deve apresentar as atribuições "OP01:M01, OP03:M02, OP04:M01" com setup total de 0 minutos
    E deve existir uma única sugestão gravada com 3 itens

  @US15_CT03 @excecao
  Cenário: Bloquear ordem sem máquina compatível
    Dado que o produto de "OP02" não possui máquinas compatíveis
    Quando selecionar "OP01, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a geração deve ser rejeitada com "A ordem OP02 usa o produto PROD-OP02 (Produto OP02), que não possui máquina compatível ativa."
    E nenhuma sugestão deve ter sido gravada

  @US15_CT04 @excecao
  Cenário: Bloquear ordem compatível somente com máquina inativa
    Dado que a máquina "M01" está inativa
    Quando selecionar "OP01" para a sugestão
    E solicitar a sequência sugerida
    Então a geração deve ser rejeitada com "A ordem OP01 usa o produto PROD-OP01 (Produto OP01), que não possui máquina compatível ativa."
    E nenhuma sugestão deve ter sido gravada
