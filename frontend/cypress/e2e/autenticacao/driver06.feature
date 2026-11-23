# language: pt
@Driver06 @SC61 @R2 @regressao
Funcionalidade: Expiração e invalidação de sessão
  Como usuário do SetupFlow
  Quero que sessões inválidas sejam rejeitadas
  Para impedir acessos sem autenticação válida

  Cenário: Permitir acesso com sessão válida
    Dado que o planejador possui uma sessão válida no Driver06
    E a API permite consultar as famílias
    Quando ele acessa a página de famílias
    Então a listagem de famílias deve ser exibida

  Cenário: Retornar ao login após a sessão expirar
    Dado que o planejador possui uma sessão válida no Driver06
    E a API rejeita a consulta de famílias com sessão expirada
    Quando ele acessa a página de famílias
    Então o sistema deve retornar para a tela de login

  Cenário: Retornar ao login quando a sessão for invalidada em outra funcionalidade
    Dado que o planejador possui uma sessão válida no Driver06
    E a API rejeita a consulta de máquinas por sessão inválida
    Quando ele acessa a página de máquinas
    Então o sistema deve retornar para a tela de login

  Cenário: Voltar ao login em Famílias após 401 mesmo se a identidade responder 503
    Dado que o planejador possui uma sessão válida no Driver06
    E a reconsulta de identidade está configurada para responder 503 após o 401
    E a API rejeita a consulta de famílias com sessão expirada
    Quando ele acessa a página de famílias
    Então a consulta de famílias deve ter sido rejeitada com 401
    E o sistema deve retornar para a tela de login

  Cenário: Voltar ao login em Máquinas após 401 mesmo se a identidade responder 503
    Dado que o planejador possui uma sessão válida no Driver06
    E a reconsulta de identidade está configurada para responder 503 após o 401
    E a API rejeita a consulta de máquinas por sessão inválida
    Quando ele acessa a página de máquinas
    Então o sistema deve retornar para a tela de login
