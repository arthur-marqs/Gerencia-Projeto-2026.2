# language: pt
@US14 @R2 @S3 @regressao
Funcionalidade: Considerar prazos e prioridades no sequenciamento
  Como Planejador de Produção
  Quero que os prazos e prioridades sejam considerados na sequência sugerida
  Para que as ordens mais urgentes sejam consideradas no planejamento

  Contexto:
    Dado que o Planejador está autenticado para gerar sugestões

  @US14_CT01 @smoke
  Cenário: Priorizar uma ordem urgente mesmo com aumento de setup
    Dado que os tempos são de 5 minutos de A para B e 30 minutos de B para A
    E que a ordem "OP01" tem prazo em 7 dias, prioridade "Baixa" e duração de 30 minutos
    E que a ordem "OP03" tem prazo em 7 dias, prioridade "Média" e duração de 30 minutos
    E que a ordem "OP02" tem prazo em 2 dias, prioridade "Alta" e duração de 40 minutos
    Quando selecionar "OP01, OP03, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP02, OP03, OP01" com setup total de 30 minutos
    E deve existir uma única sugestão gravada com 3 itens

  @US14_CT02
  Cenário: Considerar o prazo antes do setup em ordens de mesma prioridade
    Dado que os tempos são de 5 minutos de A para B e 30 minutos de B para A
    E que a ordem "OP01" tem prazo em 7 dias, prioridade "Média" e duração de 30 minutos
    E que a ordem "OP02" tem prazo em 2 dias, prioridade "Média" e duração de 30 minutos
    Quando selecionar "OP01, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP02, OP01" com setup total de 30 minutos

  @US14_CT03
  Cenário: Considerar prioridades diferentes em ordens de mesmo prazo
    Dado que a ordem "OP01" tem prazo em 7 dias, prioridade "Baixa" e duração de 30 minutos
    E que a ordem "OP03" tem prazo em 7 dias, prioridade "Alta" e duração de 30 minutos
    Quando selecionar "OP01, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "OP03, OP01" com setup total de 0 minutos

  @US14_CT04 @excecao
  Cenário: Informar dados de planejamento incompletos
    Dado que a ordem "OP01" tem prazo em 7 dias, prioridade "Alta" e duração de 30 minutos
    Quando selecionar "OP01, OP03" para a sugestão
    E solicitar a sequência sugerida
    Então a geração deve ser rejeitada com "A ordem OP03 está sem: prazo, prioridade, duração estimada."
    E nenhuma sugestão deve ter sido gravada

  @US14_CT05 @CT115
  Esquema do Cenário: Resolver o conflito entre prazo, prioridade e setup
    Dado que os tempos são de 5 minutos de A para B e 30 minutos de B para A
    E que a ordem "OP01" tem prazo em 7 dias, prioridade "Alta" e duração de 2400 minutos
    E que a ordem "OP02" tem prazo em <prazo> dias, prioridade "Baixa" e duração de 2400 minutos
    Quando selecionar "OP01, OP02" para a sugestão
    E solicitar a sequência sugerida
    Então a sequência sugerida deve ser "<sequencia>" com setup total de <setup> minutos
    E deve existir uma única sugestão gravada com 2 itens

    Exemplos:
      | prazo | sequencia  | setup |
      | 2     | OP02, OP01 | 30    |
      | 7     | OP01, OP02 | 5     |
