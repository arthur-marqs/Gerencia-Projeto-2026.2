import { Before, After, Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

const API = 'http://localhost:8000/api'
const SENHA = 'SenhaE2E!2026'
const NOVA_SENHA = 'NovaSenhaE2E!2026'
const campo = (nome) => cy.get(`[data-cy="usuario-${nome}"]`)
let estado
let tokenAna
let tokenExclusao
let ultimaResposta
let anterior
let alvo
let vinculoAtual
let snapshot

function requisitar(method, rota, body) {
  return cy.request({ method, url: API + rota, body, failOnStatusCode: false, log: false })
}

function entrar(email, senha = SENHA) {
  cy.clearCookies()
  cy.visit('/')
  cy.get('[data-cy="login-email"]').type(email)
  cy.get('[data-cy="login-senha"]').type(senha, { log: false })
  cy.get('[data-cy="login-entrar"]').click()
  cy.contains('h1', 'Bem-vindo').should('be.visible')
}

function abrirUsuarios() {
  cy.get('[data-cy="menu-usuarios"]').should('be.visible').click()
  cy.get('[data-cy="usuario-linha"]').should('exist')
}

function selecionar(chave) {
  alvo = estado.usuarios[chave]
  cy.get(`[data-usuario-id="${alvo.id}"]`).find('button').click()
  campo('nome').should('have.value', alvo.nome)
  campo('editar').should('be.enabled')
}

function confirmar() {
  campo('confirmacao').should('be.visible').and('contain', alvo.nome).and('contain', alvo.email)
  campo('confirmar').should('be.enabled').click()
}

function sucesso(mensagem) {
  campo('sucesso').should('contain', mensagem)
  campo('editar').should('be.enabled')
}

Before({ tags: '@US32' }, ({ pickle }) => {
  estado = undefined
  tokenAna = undefined
  tokenExclusao = undefined
  ultimaResposta = undefined
  anterior = undefined
  snapshot = undefined
  const modo = pickle.tags.some(tag => tag.name === '@instalacao') ? 'vazio' : 'normal'
  cy.task('e2e:reset', modo, { log: false }).then(dados => { estado = dados })
})

After({ tags: '@US32' }, ({ pickle }) => {
  // Captura de cada cenário aprovado; falhas também são capturadas pelo Cypress.
  const nome = pickle.name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9 -]/g, '').slice(0, 150)
  cy.screenshot(nome, { capture: 'viewport' })
})

Given('que o administrador acessou o menu Usuários', () => {
  entrar(estado.usuarios.admin.email)
  abrirUsuarios()
})

When('cadastrar pela interface uma conta com nome e e-mail aparados e dois perfis', () => {
  campo('novo').click()
  campo('nome').type('  Nova Conta E2E  ')
  campo('email').type('NOVA.E2E@EXAMPLE.COM')
  campo('senha').type(SENHA, { log: false })
  campo('perfil-PLANEJADOR').check()
  campo('perfil-OPERADOR').check()
  campo('salvar').click()
})

Then('uma única conta ativa deve ser confirmada', () => {
  sucesso('Usuário cadastrado com sucesso.')
  campo('detalhes').should('contain', 'Situação: Ativo')
  campo('nome').should('have.value', 'Nova Conta E2E')
  campo('email').should('have.value', 'nova.e2e@example.com')
  requisitar('GET', '/usuarios').then(({ status, body }) => {
    expect(status).to.equal(200)
    const contas = body.filter(u => u.email === 'nova.e2e@example.com')
    expect(contas).to.have.length(1)
    expect(contas[0].ativo).to.equal(true)
    expect(contas[0].perfis).to.deep.equal(['OPERADOR', 'PLANEJADOR'])
  })
})

Then('a nova conta deve entrar com sua senha e acessar produtos como planejador', () => {
  entrar('nova.e2e@example.com')
  cy.get('[data-cy="menu-usuarios"]').should('not.exist')
  cy.get('[data-cy="menu-produtos"]').should('be.visible').click()
  requisitar('GET', '/produtos').its('status').should('equal', 200)
})

When('consultar Ana e a conta inativa pela interface', () => {
  selecionar('ana')
  campo('detalhes').should('contain', 'Situação: Ativo')
  campo('perfil-PLANEJADOR').should('be.checked')
  campo('senha').should('not.exist')
  selecionar('inativo')
  campo('detalhes').should('contain', 'Situação: Inativo')
  campo('perfil-OPERADOR').should('be.checked')
})

Then('a consulta da interface e da API deve omitir senha e hash', () => {
  campo('senha').should('not.exist')
  for (const rota of ['/usuarios', `/usuarios/${estado.usuarios.inativo.id}`]) {
    requisitar('GET', rota).then(({ status, body }) => {
      expect(status).to.equal(200)
      for (const usuario of Array.isArray(body) ? body : [body]) {
        expect(usuario).to.have.all.keys('id', 'nome', 'email', 'perfis', 'ativo')
      }
    })
  }
})

Given('Ana possui uma sessão de planejador aberta', () => {
  cy.task('e2e:login', { email: estado.usuarios.ana.email, senha: SENHA }, { log: false })
    .then(token => { tokenAna = token })
  cy.then(() => cy.task('e2e:session', { token: tokenAna, caminho: '/api/produtos' }, { log: false }))
    .its('status').should('equal', 200)
})

When('editar Ana para operador deixando a nova senha em branco', () => {
  selecionar('ana')
  campo('editar').click()
  campo('nome').clear().type('Ana Editada E2E')
  campo('email').clear().type('ANA.EDITADA.E2E@EXAMPLE.COM')
  campo('perfil-PLANEJADOR').uncheck()
  campo('perfil-OPERADOR').check()
  campo('senha').should('have.value', '')
  campo('salvar').click()
  sucesso('Usuário atualizado com sucesso.')
})

Then('os novos dados devem persistir e a senha atual deve continuar válida', () => {
  requisitar('GET', `/usuarios/${estado.usuarios.ana.id}`).then(({ body }) => {
    expect(body.nome).to.equal('Ana Editada E2E')
    expect(body.email).to.equal('ana.editada.e2e@example.com')
    expect(body.perfis).to.deep.equal(['OPERADOR'])
  })
  cy.task('e2e:credentials', { email: 'ana.editada.e2e@example.com', senha: SENHA }, { log: false })
    .its('status').should('equal', 200)
})

Then('a sessão já aberta deve receber 403 ao consultar produtos', () => {
  cy.task('e2e:session', { token: tokenAna, caminho: '/api/produtos' }, { log: false })
    .its('status').should('equal', 403)
  cy.task('e2e:session', { token: tokenAna, caminho: '/api/auth/me' }, { log: false })
    .then(({ status, corpo }) => {
      expect(status).to.equal(200)
      expect(corpo.usuario.perfis).to.deep.equal(['OPERADOR'])
    })
})

When('solicitar a exclusão da conta sem vínculos e cancelar a confirmação', () => {
  selecionar('exclusao')
  cy.task('e2e:login', { email: alvo.email, senha: SENHA }, { log: false }).then(token => { tokenExclusao = token })
  campo('excluir').click()
  campo('confirmacao').should('contain', alvo.nome).and('contain', alvo.email)
  cy.screenshot('CT35-confirmacao-antes-do-cancelamento', { capture: 'viewport' })
  campo('cancelar').click()
  campo('confirmacao').should('not.exist')
})

Then('a conta sem vínculos deve permanecer inalterada', () => {
  requisitar('GET', `/usuarios/${alvo.id}`).then(({ status, body }) => {
    expect(status).to.equal(200)
    expect(body).to.deep.equal({ ...alvo, perfis: [...alvo.perfis].sort() })
  })
  cy.reload()
  abrirUsuarios()
  selecionar('exclusao')
})

When('confirmar a exclusão da mesma conta', () => { campo('excluir').click(); confirmar() })

Then('a conta deve desaparecer e seus acessos devem ser recusados', () => {
  campo('sucesso').should('contain', 'Usuário excluído com sucesso.')
  cy.get(`[data-usuario-id="${alvo.id}"]`).should('not.exist')
  requisitar('GET', `/usuarios/${alvo.id}`).its('status').should('equal', 404)
  cy.task('e2e:session', { token: tokenExclusao, caminho: '/api/auth/me' }, { log: false })
    .its('status').should('equal', 401)
  cy.task('e2e:credentials', { email: alvo.email, senha: SENHA }, { log: false }).its('status').should('equal', 401)
})

When('tentar cadastrar com nome vazio, e-mail inválido, senha curta e sem perfil', () => {
  campo('nome').type('   ')
  campo('email').type('email-invalido')
  campo('senha').type('curta', { log: false })
  campo('salvar').click()
})

Then('cada campo inválido deve ter sua mensagem', () => {
  for (const id of ['nome', 'email', 'senha', 'perfis']) cy.get(`#erro-${id}`).should('be.visible')
  requisitar('GET', '/usuarios').its('body.length').should('equal', Object.keys(estado.usuarios).length)
})

When('tentar uma edição inválida de Ana', () => {
  selecionar('ana')
  campo('editar').click()
  campo('nome').clear().type('Não deve salvar')
  campo('perfil-PLANEJADOR').uncheck()
  campo('senha').type('curta', { log: false })
  campo('salvar').click()
  cy.get('#erro-perfis').should('be.visible')
  cy.get('#erro-senha').should('be.visible')
})

Then('seus dados e perfis anteriores devem continuar salvos', () => {
  requisitar('GET', `/usuarios/${estado.usuarios.ana.id}`).its('body').should('deep.equal', estado.usuarios.ana)
  campo('cancelar-edicao').click()
  campo('nome').should('have.value', estado.usuarios.ana.nome)
  campo('perfil-PLANEJADOR').should('be.checked')
})

When('tentar editar Ana pela API com um perfil inexistente', () => {
  requisitar('PUT', `/usuarios/${estado.usuarios.ana.id}`, {
    nome: 'Não deve salvar', email: estado.usuarios.ana.email, perfis: ['INEXISTENTE'], senha: '',
  }).then(resposta => { ultimaResposta = resposta })
})

Then('a API deve responder 422 e preservar todos os dados anteriores', () => {
  expect(ultimaResposta.status).to.equal(422)
  expect(ultimaResposta.body.detail.some(erro => erro.loc[1] === 'perfis')).to.equal(true)
  requisitar('GET', `/usuarios/${estado.usuarios.ana.id}`).its('body').should('deep.equal', estado.usuarios.ana)
  selecionar('ana')
})

When('tentar um {string} com o e-mail normalizado de uma conta {string}', (operacao, situacao) => {
  const email = estado.usuarios[situacao === 'ativa' ? 'ana' : 'inativo'].email.toUpperCase()
  cy.task('e2e:inspect', null, { log: false }).then(dados => { anterior = dados })
  if (operacao === 'cadastro') {
    campo('nome').type('Duplicada E2E')
    campo('senha').type(SENHA, { log: false })
    campo('perfil-OPERADOR').check()
  } else { selecionar('exclusao'); campo('editar').click() }
  campo('email').clear().type(email)
  campo('salvar').click()
})

Then('o e-mail deve ser identificado como já em uso sem modificar as contas', () => {
  campo('erro').should('contain', 'O e-mail já está em uso.')
  cy.get('#erro-email').should('contain', 'O e-mail já está em uso.')
  cy.task('e2e:inspect', null, { log: false }).then(dados => { expect(dados).to.deep.equal(anterior) })
})

When('desativar Ana com confirmação', () => {
  selecionar('ana'); campo('status').click(); confirmar(); sucesso('Usuário desativado com sucesso.')
  campo('detalhes').should('contain', 'Situação: Inativo')
})

Then('suas sessões e novos logins devem ser recusados', () => {
  cy.task('e2e:session', { token: tokenAna, caminho: '/api/auth/me' }, { log: false })
    .its('status').should('equal', 401)
  cy.task('e2e:credentials', { email: estado.usuarios.ana.email, senha: SENHA }, { log: false })
    .its('status').should('equal', 401)
  cy.screenshot('CT38-conta-desativada', { capture: 'viewport' })
})

When('reativar Ana com confirmação', () => {
  campo('status').click(); confirmar(); sucesso('Usuário reativado com sucesso.')
  campo('detalhes').should('contain', 'Situação: Ativo')
})

Then('a sessão antiga deve continuar inválida e um novo login deve funcionar', () => {
  cy.task('e2e:session', { token: tokenAna, caminho: '/api/auth/me' }, { log: false })
    .its('status').should('equal', 401)
  entrar(estado.usuarios.ana.email)
})

When('tentar excluir a conta autora de {string}', (vinculo) => {
  vinculoAtual = vinculo
  cy.task('e2e:inspect', null, { log: false }).then(dados => { anterior = dados })
  selecionar(vinculo === 'planejamentos' ? 'autor_plano' : 'autor_ordem')
  campo('excluir').click(); confirmar()
})

Then('o bloqueio deve identificar {string} e oferecer desativação', (vinculo) => {
  campo('erro').should('contain', vinculo)
  campo('oferecer-desativacao').should('be.visible')
  cy.screenshot(`CT39-bloqueio-${vinculo}`, { capture: 'viewport' })
})

When('aceitar a desativação oferecida', () => {
  campo('oferecer-desativacao').click(); confirmar(); sucesso('Usuário desativado com sucesso.')
})

Then('a autoria e o registro de produção devem permanecer preservados', () => {
  cy.task('e2e:inspect', null, { log: false }).then(dados => {
    expect(dados.ordem).to.deep.equal(anterior.ordem)
    expect(dados.plano).to.deep.equal(anterior.plano)
    const registro = vinculoAtual === 'planejamentos' ? dados.plano : dados.ordem
    expect(registro.criado_por).to.equal(alvo.id)
    const usuario = dados.usuarios.find(u => u.id === alvo.id)
    expect(usuario.ativo).to.equal(false)
    expect(usuario.perfis).to.deep.equal(alvo.perfis)
  })
})

When('tentar {string} o acesso do último administrador ativo', (operacao) => {
  selecionar('admin')
  if (operacao === 'remover o perfil') {
    campo('editar').click(); campo('perfil-ADMINISTRADOR').uncheck(); campo('salvar').click()
  } else {
    campo(operacao === 'excluir' ? 'excluir' : 'status').click(); confirmar()
  }
})

Then('a operação deve ser recusada e a conta administrativa deve permanecer ativa', () => {
  campo('erro').should('contain', 'É necessário manter pelo menos um administrador ativo.')
  requisitar('GET', `/usuarios/${estado.usuarios.admin.id}`).then(({ status, body }) => {
    expect(status).to.equal(200)
    expect(body.ativo).to.equal(true)
    expect(body.perfis).to.include('ADMINISTRADOR')
  })
  cy.get('[data-cy="menu-usuarios"]').should('be.visible')
})

Given('que o acesso à aplicação está {string}', (acesso) => {
  if (acesso === 'operador') entrar(estado.usuarios.operador.email)
  else cy.visit('/')
  cy.task('e2e:inspect', null, { log: false }).then(dados => { snapshot = dados })
})

When('solicitar {string} de usuários diretamente pela API', (operacao) => {
  const id = estado.usuarios.ana.id
  const dados = { nome: 'Tentativa', email: 'tentativa.e2e@example.com', perfis: ['OPERADOR'], senha: SENHA }
  const operacoes = {
    listar: ['GET', '/usuarios'], consultar: ['GET', `/usuarios/${id}`],
    cadastrar: ['POST', '/usuarios', dados], editar: ['PUT', `/usuarios/${id}`, dados],
    desativar: ['PATCH', `/usuarios/${id}/status`, { ativo: false }],
    reativar: ['PATCH', `/usuarios/${id}/status`, { ativo: true }],
    excluir: ['DELETE', `/usuarios/${id}`],
  }
  requisitar(...operacoes[operacao]).then(resposta => { ultimaResposta = resposta })
})

Then('a API deve responder {int} sem expor ou modificar os usuários', (status) => {
  expect(ultimaResposta.status).to.equal(status)
  expect(ultimaResposta.body).to.have.all.keys('detail')
  expect(ultimaResposta.body.detail).to.be.a('string')
  cy.task('e2e:inspect', null, { log: false }).then(dados => { expect(dados).to.deep.equal(snapshot) })
})

Then('o menu Usuários deve permanecer indisponível', () => { cy.get('[data-cy="menu-usuarios"]').should('not.exist') })

When('substituir a senha de Ana por uma nova senha válida', () => {
  selecionar('ana'); campo('editar').click()
  campo('senha').type(NOVA_SENHA, { log: false }); campo('salvar').click()
  sucesso('Usuário atualizado com sucesso.')
})

Then('a sessão anterior e a senha antiga devem ser recusadas', () => {
  cy.task('e2e:session', { token: tokenAna, caminho: '/api/auth/me' }, { log: false })
    .its('status').should('equal', 401)
  cy.task('e2e:credentials', { email: estado.usuarios.ana.email, senha: SENHA }, { log: false })
    .its('status').should('equal', 401)
})

Then('o próximo login pela interface deve aceitar a senha nova', () => { entrar(estado.usuarios.ana.email, NOVA_SENHA) })

Given('que as migrations estão aplicadas e não existe nenhuma conta', () => {
  cy.task('e2e:inspect', null, { log: false }).its('usuarios').should('have.length', 0)
})

When('executar o script inicial selecionando o perfil ADMINISTRADOR', () => {
  cy.task('e2e:bootstrap', null, { log: false }).its('mensagem').should('contain', 'ADMINISTRADOR')
})

Then('o primeiro administrador deve acessar o menu Usuários', () => {
  entrar('admin.e2e@example.com'); abrirUsuarios()
  campo('linha').should('have.length', 1)
})
