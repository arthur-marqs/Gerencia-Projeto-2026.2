# language: pt
@US17 @R2 @S3 @regressao
Funcionalidade: Aprovar planejamento de produção
  Como Planejador de Produção
  Quero aprovar o planejamento selecionado
  Para disponibilizar sua sequência à execução da produção

  Contexto:
    Dado que o Planejador está autenticado para gerar sugestões

  @CT123 @smoke
  Cenário: CT-123 Disponibilizar o planejamento aprovado para execução
    Dado que existe um planejamento manual para "OP01, OP03"
    Quando abrir a execução da produção
    E selecionar a sequência "manual" para aprovação
    Então a sequência exibida para aprovação deve ser "OP01, OP03"
    Quando aprovar o planejamento selecionado
    Então a aprovação deve registrar a origem "manual" e a sequência "OP01, OP03"
    Quando recarregar e consultar a execução da produção
    Então o planejamento "manual" deve estar aprovado para execução com "OP01, OP03"
    Quando o Operador consultar a execução da produção
    Então o planejamento "manual" deve estar aprovado para execução com "OP01, OP03"
    E o Operador deve poder consultar sem opção de aprovar

  @CT124 @excecao
  Cenário: CT-124 Informar que não há planejamento disponível
    Quando abrir a execução da produção
    E aprovar o planejamento selecionado
    Então a tela deve informar que não existe planejamento disponível para aprovação
    E nenhuma aprovação deve ter sido registrada

  @CT125
  Cenário: CT-125 Aprovar a sequência sugerida escolhida sem modificar as origens
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que existe um planejamento manual para "OP01, OP02, OP03"
    E que já existe uma sugestão para esse planejamento
    Quando abrir a execução da produção
    Então as alternativas manual e sugerida devem estar disponíveis sem seleção inicial
    Quando selecionar a sequência "manual" para aprovação
    Então a sequência exibida para aprovação deve ser "OP01, OP02, OP03"
    Quando selecionar a sequência "sugerida" para aprovação
    Então a sequência exibida para aprovação deve ser "OP01, OP03, OP02"
    Quando aprovar o planejamento selecionado
    Então a aprovação deve registrar a origem "sugerida" e a sequência "OP01, OP03, OP02"
    E o planejamento "sugerida" deve estar aprovado para execução com "OP01, OP03, OP02"
    E os registros do planejamento manual e da sugestão devem permanecer iguais
