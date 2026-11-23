import {
  Given,
  When,
  Then,
} from '@badeball/cypress-cucumber-preprocessor'

let sessaoValida = true
let statusReconsulta: 401 | 503 = 401

Given('que o planejador possui uma sessão válida no Driver06', () => {
  sessaoValida = true
  statusReconsulta = 401

  cy.intercept('GET', '**/api/auth/me', (req) => {
    const statusCode = sessaoValida ? 200 : statusReconsulta

    req.reply({
      statusCode,
      body: sessaoValida
        ? {
            usuario: {
              nome: 'Planejador de Teste',
              perfis: ['PLANEJADOR'],
            },
          }
        : {
            detail: statusCode === 503
              ? 'Serviço temporariamente indisponível.'
              : 'Sessão inválida ou expirada.',
          },
    })
  }).as('verificarSessao')
})

Given('a reconsulta de identidade está configurada para responder 503 após o 401', () => {
  statusReconsulta = 503
})

Given('a API permite consultar as famílias', () => {
  cy.intercept('GET', '**/api/families', {
    statusCode: 200,
    body: [],
  }).as('consultarFamilias')
})

Given('a API rejeita a consulta de famílias com sessão expirada', () => {
  cy.intercept('GET', '**/api/families', (req) => {
    sessaoValida = false

    req.reply({
      statusCode: 401,
      body: { detail: 'Sessão inválida ou expirada.' },
    })
  }).as('consultarFamilias')
})

When('ele acessa a página de famílias', () => {
  cy.viewport(1280, 800)
  cy.visit('/')

  cy.contains('nav button', 'Famílias de produtos').click()
})

Then('a listagem de famílias deve ser exibida', () => {
  cy.wait('@consultarFamilias')

  cy.contains('h2', 'Famílias cadastradas').should('be.visible')
})

Then('a consulta de famílias deve ter sido rejeitada com 401', () => {
  cy.wait('@consultarFamilias').its('response.statusCode').should('eq', 401)
})

Then('o sistema deve retornar para a tela de login', () => {
  cy.contains('h2', 'Acesse sua conta').should('be.visible')
  cy.get('nav[aria-label="Navegação principal"]').should('not.exist')
  cy.contains('h2', 'Cadastrar família').should('not.exist')
  cy.contains('h2', 'Famílias cadastradas').should('not.exist')
  cy.get('input[type="email"]').should('be.visible')
})

Given('a API rejeita a consulta de máquinas por sessão inválida', () => {
  cy.intercept('GET', '**/api/maquinas', (req) => {
    sessaoValida = false

    req.reply({
      statusCode: 401,
      body: { detail: 'Sessão inválida ou expirada.' },
    })
  }).as('consultarMaquinas')
})

When('ele acessa a página de máquinas', () => {
  cy.viewport(1280, 800)
  cy.visit('/')

  cy.contains('nav button', 'Máquinas').click()
  cy.wait('@consultarMaquinas').its('response.statusCode').should('eq', 401)
})

Given('a API rejeita a consulta de {string} da matriz por sessão inválida', (recurso: string) => {
  for (const rota of ['families', 'tempos-setup']) {
    cy.intercept('GET', `**/api/${rota}`, (req) => {
      if (rota === recurso) {
        sessaoValida = false
        req.alias = 'matrizSessaoRejeitada'
        req.reply({ statusCode: 401, body: { detail: 'Sessão inválida ou expirada.' } })
      } else {
        req.reply({ statusCode: 200, body: [] })
      }
    })
  }
})

When('ele acessa a matriz de setup no Driver06', () => {
  cy.viewport(1280, 800)
  cy.visit('/')
  cy.get('[data-cy="menu-matriz-setup"]').click()
})

Then('a consulta da matriz deve ter sido rejeitada com 401', () => {
  cy.wait('@matrizSessaoRejeitada').its('response.statusCode').should('eq', 401)
})
