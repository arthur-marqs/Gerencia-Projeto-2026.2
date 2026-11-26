# language: pt
@US16 @R2 @S3 @regressao
Funcionalidade: Comparar sequência manual e sequência sugerida
  Como Planejador de Produção
  Quero comparar os planejamentos manual e sugerido
  Para avaliar qual planejamento é mais eficiente

  Contexto:
    Dado que o Planejador está autenticado para gerar sugestões
    E que existe um planejamento manual para "OP01, OP02, OP03"

  @CT120 @smoke
  Cenário: CT-120 Exibir as duas sequências e as diferenças
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que já existe uma sugestão para esse planejamento
    Quando solicitar a comparação do planejamento
    Então a comparação deve exibir a sequência manual "OP01, OP02, OP03" e a sugerida "OP01, OP03, OP02"
    E deve destacar as duas ordens que mudaram de posição
    E deve mostrar 50 minutos de setup manual e 20 minutos de setup sugerido

  @CT121 @excecao
  Cenário: CT-121 Orientar a geração quando falta sequência sugerida
    Quando solicitar a comparação do planejamento
    Então a comparação deve pedir que a sequência sugerida seja gerada
    E nenhuma sugestão deve ter sido gravada

  @CT122
  Cenário: CT-122 Preservar os registros ao consultar a comparação
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que já existe uma sugestão para esse planejamento
    Quando solicitar a comparação do planejamento
    Então a comparação deve exibir a sequência manual "OP01, OP02, OP03" e a sugerida "OP01, OP03, OP02"
    E os registros do planejamento manual e da sugestão devem permanecer iguais
    E deve existir uma única sugestão gravada com 3 itens

  @US16_Catalogo
  Cenário: Comparar o planejamento quando o catálogo de máquinas responde 503
    Dado que os tempos são de 20 minutos de A para B e 30 minutos de B para A
    E que já existe uma sugestão para esse planejamento
    E que o catálogo de máquinas responde 503
    Quando solicitar a comparação do planejamento
    Então a comparação deve exibir a sequência manual "OP01, OP02, OP03" e a sugerida "OP01, OP03, OP02"
    E deve mostrar 50 minutos de setup manual e 20 minutos de setup sugerido
    E o Planejador deve ver o aviso do catálogo e a ordem pendente "OP04"
    Quando o catálogo voltar a ficar disponível
    E solicitar a comparação do planejamento
    Então a comparação deve voltar a mostrar a máquina "M01" pelo nome
