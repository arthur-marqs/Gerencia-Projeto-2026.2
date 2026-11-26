# language: pt
@US01 @Driver06 @BUG005 @R2 @regressao
Funcionalidade: Recuperar a verificação da sessão
  Como usuário do SetupFlow
  Quero repetir a verificação de identidade após uma falha temporária
  Para voltar ao painel com a sessão que já possuo

  Esquema do Cenário: Recuperar a sessão após "<falha>" na abertura
    Dado que a consulta inicial de identidade falha com "<falha>"
    Quando o usuário abre o SetupFlow para restaurar a sessão
    Então a tela deve informar que não foi possível verificar a sessão
    Quando a identidade fica disponível e o usuário tenta verificar novamente
    Então o painel do planejador deve aparecer sem solicitar novo login

    Exemplos:
      | falha |
      | 503   |
      | rede  |

  Cenário: Solicitar login quando a nova verificação retorna 401
    Dado que a consulta inicial de identidade falha com "503"
    Quando o usuário abre o SetupFlow para restaurar a sessão
    Então a tela deve informar que não foi possível verificar a sessão
    Quando a API rejeita a sessão na nova verificação de identidade
    Então o formulário de login deve aparecer sem a navegação autenticada

  Cenário: Permitir outra tentativa enquanto a identidade estiver indisponível
    Dado que a consulta inicial de identidade falha com "503"
    Quando o usuário abre o SetupFlow para restaurar a sessão
    Então a tela deve informar que não foi possível verificar a sessão
    Quando o usuário repete a verificação com a identidade ainda indisponível
    Então a tela deve informar que não foi possível verificar a sessão
    Quando a identidade fica disponível e o usuário tenta verificar novamente
    Então o painel do planejador deve aparecer sem solicitar novo login

  Cenário: Recuperar a identificação depois de um login bem-sucedido
    Dado que o login funciona e a primeira consulta após o login responde 503
    Quando o usuário entra com as credenciais de teste
    Então a tela deve informar que não foi possível verificar a sessão
    Quando a identidade fica disponível e o usuário tenta verificar novamente
    Então o painel do planejador deve aparecer sem solicitar novo login
