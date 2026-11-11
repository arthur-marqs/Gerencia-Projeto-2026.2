
# language: pt
Funcionalidade: Autenticação no SetupFlow
  Como usuário do sistema
  Quero acessar a tela de login
  Para informar minhas credenciais

  Cenário: Exibir a tela de login
    Dado que o usuário acessa o SetupFlow
    Então a tela de login deve ser exibida

  Cenário: Tentar entrar com os campos vazios
    Dado que o usuário acessa o SetupFlow
    Quando ele tenta entrar sem preencher os campos
    Então deve aparecer a mensagem "Informe seu e-mail."
    E deve aparecer a mensagem "Informe sua senha."

  Cenário: Tentar entrar com e-mail inválido
    Dado que o usuário acessa o SetupFlow
    Quando ele informa o e-mail "emailinvalido" e a senha "senha123"
    E tenta entrar no sistema
    Então deve aparecer a mensagem "Informe um e-mail válido."

  Cenário: Tentar entrar sem informar a senha
    Dado que o usuário acessa o SetupFlow
    Quando ele informa o e-mail "usuario@empresa.com"
    E tenta entrar no sistema
    Então deve aparecer a mensagem "Informe sua senha."

  Cenário: Tentar entrar com credenciais incorretas
    Dado que o usuário acessa o SetupFlow
    Quando ele informa o e-mail "usuario@empresa.com" e a senha "senhaerrada"
    E a API rejeita as credenciais
    E tenta entrar no sistema
    Então deve aparecer o erro de autenticação "Credenciais inválidas."
