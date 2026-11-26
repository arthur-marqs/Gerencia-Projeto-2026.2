import { Given, Then, When } from '@badeball/cypress-cucumber-preprocessor'

type ResultadoIdentidade = '503' | 'rede' | '200' | '401'

let identidade: ResultadoIdentidade
let loginsEsperados: number

function simularIdentidade(inicial: ResultadoIdentidade, totalLogins = 0) {
  identidade = inicial
  loginsEsperados = totalLogins
  cy.intercept('GET', '**/api/auth/me', (req) => {
    if (identidade === 'rede') {
      req.reply({ forceNetworkError: true })
      return
    }

    req.reply({
      statusCode: Number(identidade),
      body: identidade === '200'
        ? { usuario: { nome: 'Planejador de Teste', perfis: ['PLANEJADOR'] } }
        : { detail: identidade === '503' ? 'Serviço indisponível.' : 'Sessão inválida ou expirada.' },
    })
  }).as('identidade')
}

Given('que a consulta inicial de identidade falha com {string}', (falha: '503' | 'rede') => {
  simularIdentidade(falha)
  cy.intercept('POST', '**/api/auth/login', {
    statusCode: 500,
    body: { detail: 'O reteste deve utilizar a sessão existente.' },
  }).as('login')
})

When('o usuário abre o SetupFlow para restaurar a sessão', () => {
  cy.viewport(1280, 800)
  cy.visit('/')
})

Then('a tela deve informar que não foi possível verificar a sessão', () => {
  cy.contains('[role="alert"]', 'Não foi possível verificar a sessão.').should('be.visible')
  cy.contains('button', 'Tentar novamente').should('be.visible').and('be.enabled')
  cy.get('[data-cy="login-email"]').should('not.exist')
  cy.get('nav[aria-label="Navegação principal"]').should('not.exist')
})

When('a identidade fica disponível e o usuário tenta verificar novamente', () => {
  cy.then(() => { identidade = '200' })
  cy.contains('button', 'Tentar novamente').click()
})

When('a API rejeita a sessão na nova verificação de identidade', () => {
  cy.then(() => { identidade = '401' })
  cy.contains('button', 'Tentar novamente').click()
})

When('o usuário repete a verificação com a identidade ainda indisponível', () => {
  cy.get('@identidade.all').then((consultas) => {
    cy.contains('button', 'Tentar novamente').click()
    cy.get('@identidade.all').should('have.length', consultas.length + 1)
  })
})

Then('o painel do planejador deve aparecer sem solicitar novo login', () => {
  cy.contains('h1', 'Bem-vindo, Planejador de Teste.').should('be.visible')
  cy.get('nav[aria-label="Navegação principal"]').should('be.visible')
  cy.get('[data-cy="login-email"]').should('not.exist')
  cy.get('@login.all').should('have.length', loginsEsperados)
})

Then('o formulário de login deve aparecer sem a navegação autenticada', () => {
  cy.contains('h2', 'Acesse sua conta').should('be.visible')
  cy.get('nav[aria-label="Navegação principal"]').should('not.exist')
})

Given('que o login funciona e a primeira consulta após o login responde 503', () => {
  simularIdentidade('401', 1)
  cy.intercept('POST', '**/api/auth/login', (req) => {
    identidade = '503'
    req.reply({ statusCode: 200, body: { usuario: { nome: 'Planejador de Teste' } } })
  }).as('login')
})

When('o usuário entra com as credenciais de teste', () => {
  cy.viewport(1280, 800)
  cy.visit('/')
  cy.get('[data-cy="login-email"]').type('planejador@example.test')
  cy.get('[data-cy="login-senha"]').type('SenhaDeTeste!123', { log: false })
  cy.get('[data-cy="login-entrar"]').click()
  cy.wait('@login').its('response.statusCode').should('eq', 200)
})
