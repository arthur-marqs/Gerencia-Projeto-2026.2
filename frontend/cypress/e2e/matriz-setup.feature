# language: pt
@US11 @R2 @regressao
Funcionalidade: Consultar matriz de setup entre famílias de produtos
  Como Planejador de Produção
  Quero consultar os tempos de setup entre famílias
  Para compreender os custos de transição entre produtos

  @matriz-configurada
  Cenário: Consultar tempos de setup diferentes em cada direção
    Dado que o Planejador acessou a matriz de setup
    Então a transição de "FAM-A" para "FAM-B" deve apresentar "30 min"
    E a transição de "FAM-B" para "FAM-A" deve apresentar "75 min"

  @matriz-vazia
  Cenário: Consultar matriz sem configurações de setup
    Dado que o Planejador acessou a matriz de setup
    Então deve ser informado que nenhuma configuração de setup está cadastrada
    E o botão de atualização deve estar disponível
    Quando solicitar a atualização da matriz
    Então a mensagem de ausência de configurações deve continuar visível
