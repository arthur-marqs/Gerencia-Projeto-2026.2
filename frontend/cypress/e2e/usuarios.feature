# language: pt
@US32 @R2 @regressao
Funcionalidade: Gerenciar usuários e preservar seus acessos e autoria
  Como administrador do SetupFlow
  Quero gerenciar contas e seus perfis
  Para controlar os acessos e preservar os registros de produção

  @CT32 @smoke
  Cenário: CT32 - Cadastrar uma conta ativa e permitir login com os perfis atribuídos
    Dado que o administrador acessou o menu Usuários
    Quando cadastrar pela interface uma conta com nome e e-mail aparados e dois perfis
    Então uma única conta ativa deve ser confirmada
    E a nova conta deve entrar com sua senha e acessar produtos como planejador

  @CT33 @smoke
  Cenário: CT33 - Consultar usuários ativos e inativos sem expor senha ou hash
    Dado que o administrador acessou o menu Usuários
    Quando consultar Ana e a conta inativa pela interface
    Então a consulta da interface e da API deve omitir senha e hash

  @CT34
  Cenário: CT34 - Editar dados e substituir perfis mantendo a senha e aplicando novas permissões
    Dado que o administrador acessou o menu Usuários
    E Ana possui uma sessão de planejador aberta
    Quando editar Ana para operador deixando a nova senha em branco
    Então os novos dados devem persistir e a senha atual deve continuar válida
    E a sessão já aberta deve receber 403 ao consultar produtos

  @CT35
  Cenário: CT35 - Cancelar a exclusão e depois confirmar a remoção de uma conta sem vínculos
    Dado que o administrador acessou o menu Usuários
    Quando solicitar a exclusão da conta sem vínculos e cancelar a confirmação
    Então a conta sem vínculos deve permanecer inalterada
    Quando confirmar a exclusão da mesma conta
    Então a conta deve desaparecer e seus acessos devem ser recusados

  @CT36 @excecao
  Cenário: CT36 - Identificar todos os campos inválidos e preservar os dados anteriores na edição
    Dado que o administrador acessou o menu Usuários
    Quando tentar cadastrar com nome vazio, e-mail inválido, senha curta e sem perfil
    Então cada campo inválido deve ter sua mensagem
    Quando tentar uma edição inválida de Ana
    Então seus dados e perfis anteriores devem continuar salvos

  @CT36 @excecao
  Cenário: CT36 - Rejeitar perfis inexistentes enviados diretamente à API
    Dado que o administrador acessou o menu Usuários
    Quando tentar editar Ana pela API com um perfil inexistente
    Então a API deve responder 422 e preservar todos os dados anteriores

  @CT37 @excecao
  Esquema do Cenário: CT37 - Recusar e-mail duplicado de conta <situacao> durante <operacao>
    Dado que o administrador acessou o menu Usuários
    Quando tentar um "<operacao>" com o e-mail normalizado de uma conta "<situacao>"
    Então o e-mail deve ser identificado como já em uso sem modificar as contas

    Exemplos:
      | situacao | operacao |
      | ativa    | cadastro |
      | inativa  | cadastro |
      | ativa    | edição   |
      | inativa  | edição   |

  @CT38
  Cenário: CT38 - Desativar e reativar sem recuperar as sessões antigas
    Dado que o administrador acessou o menu Usuários
    E Ana possui uma sessão de planejador aberta
    Quando desativar Ana com confirmação
    Então suas sessões e novos logins devem ser recusados
    Quando reativar Ana com confirmação
    Então a sessão antiga deve continuar inválida e um novo login deve funcionar

  @CT39 @excecao
  Esquema do Cenário: CT39 - Preservar autoria ao recusar exclusão por <vinculo>
    Dado que o administrador acessou o menu Usuários
    Quando tentar excluir a conta autora de "<vinculo>"
    Então o bloqueio deve identificar "<vinculo>" e oferecer desativação
    Quando aceitar a desativação oferecida
    Então a autoria e o registro de produção devem permanecer preservados

    Exemplos:
      | vinculo           |
      | ordens de produção |
      | planejamentos      |

  @CT40 @excecao @smoke
  Esquema do Cenário: CT40 - Preservar o último administrador ativo ao tentar <operacao>
    Dado que o administrador acessou o menu Usuários
    Quando tentar "<operacao>" o acesso do último administrador ativo
    Então a operação deve ser recusada e a conta administrativa deve permanecer ativa

    Exemplos:
      | operacao         |
      | excluir          |
      | desativar        |
      | remover o perfil |

  @CT41 @excecao
  Esquema do Cenário: CT41 - Recusar <operacao> quando o acesso está <acesso>
    Dado que o acesso à aplicação está "<acesso>"
    Quando solicitar "<operacao>" de usuários diretamente pela API
    Então a API deve responder <status> sem expor ou modificar os usuários
    E o menu Usuários deve permanecer indisponível

    Exemplos:
      | acesso      | operacao  | status |
      | sem sessão  | listar    | 401    |
      | sem sessão  | consultar | 401    |
      | sem sessão  | cadastrar | 401    |
      | sem sessão  | editar    | 401    |
      | sem sessão  | desativar | 401    |
      | sem sessão  | reativar  | 401    |
      | sem sessão  | excluir   | 401    |
      | operador    | listar    | 403    |
      | operador    | consultar | 403    |
      | operador    | cadastrar | 403    |
      | operador    | editar    | 403    |
      | operador    | desativar | 403    |
      | operador    | reativar  | 403    |
      | operador    | excluir   | 403    |

  @CT42
  Cenário: CT42 - Substituir a senha e encerrar as sessões anteriores
    Dado que o administrador acessou o menu Usuários
    E Ana possui uma sessão de planejador aberta
    Quando substituir a senha de Ana por uma nova senha válida
    Então a sessão anterior e a senha antiga devem ser recusadas
    E o próximo login pela interface deve aceitar a senha nova

  @CT43 @instalacao
  Cenário: CT43 - Criar o primeiro administrador pelo script e cadastrar a segunda conta pela interface
    Dado que as migrations estão aplicadas e não existe nenhuma conta
    Quando executar o script inicial selecionando o perfil ADMINISTRADOR
    Então o primeiro administrador deve acessar o menu Usuários
    Quando cadastrar pela interface uma conta com nome e e-mail aparados e dois perfis
    Então uma única conta ativa deve ser confirmada
