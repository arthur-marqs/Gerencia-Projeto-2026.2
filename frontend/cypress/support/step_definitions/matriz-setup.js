
import { Before, Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

const SENHA = 'SenhaE2E!2026'

let estado

const FAMILIA_A = {
  id: 'familia-a',
  code: 'A',
  name: 'Família A',
}

const FAMILIA_B = {
  id: 'familia-b',
  code: 'B',
  name: 'Família B',
}

const TRANSICAO_A_B = {
  id_tempo_setup: 'tempo-a-b',
  familia_origem: FAMILIA_A,
  familia_destino: FAMILIA_B,
  tempo_setup_minutos: 15,
}

Before({ tags: '@US11' }, ({ pickle }) => {
  estado = undefined

  const modo = pickle.tags.some((tag) => tag.name === '@matriz-vazia')
    ? 'matriz-vazia'
    : 'matriz'

  return cy.task('e2e:reset', modo, { log: false }).then((dados) => {
    estado = dados

    cy.clearCookies()
    cy.visit('/')

    cy.get('[data-cy="login-email"]').type(estado.usuarios.ana.email)
    cy.get('[data-cy="login-senha"]').type(SENHA, { log: false })
    cy.get('[data-cy="login-entrar"]').click()

    cy.contains('h1', 'Bem-vindo').should('be.visible')
  })
})

Given('que o Planejador acessou a matriz de setup', () => {
  cy.intercept('GET', '**/api/families').as('matrizFamilias')
  cy.intercept('GET', '**/api/tempos-setup').as('matrizTempos')

  cy.get('[data-cy="menu-matriz-setup"]')
    .should('be.visible')
    .click()

  cy.contains('h1', 'Matriz de setup').should('be.visible')

  cy.wait('@matrizFamilias')
    .its('response.statusCode')
    .should('eq', 200)

  cy.wait('@matrizTempos')
    .its('response.statusCode')
    .should('eq', 200)
})

Then(
  'a transição de {string} para {string} deve apresentar {string}',
  (origem, destino, tempo) => {
    cy.get(`[data-cy="matriz-celula-${origem}-${destino}"]`)
      .should('be.visible')
      .and('contain.text', tempo)
  },
)

Then('deve ser informado que nenhuma configuração de setup está cadastrada', () => {
  cy.contains(
    'h2',
    'Nenhuma configuração de setup cadastrada',
  ).should('be.visible')
})

Then('o botão de atualização deve estar disponível', () => {
  cy.get('[data-cy="matriz-atualizar"]')
    .should('be.visible')
    .and('be.enabled')
})

When('solicitar a atualização da matriz', () => {
  cy.get('[data-cy="matriz-atualizar"]').click()

  cy.wait('@matrizFamilias')
    .its('response.statusCode')
    .should('eq', 200)

  cy.wait('@matrizTempos')
    .its('response.statusCode')
    .should('eq', 200)
})

Then('a mensagem de ausência de configurações deve continuar visível', () => {
  cy.contains(
    'h2',
    'Nenhuma configuração de setup cadastrada',
  ).should('be.visible')
})
Given(
  'que a API de famílias retorna somente a família {string} e a transição A para B é de 15 minutos',
  (codigo) => {
    const familia = codigo === 'A' ? FAMILIA_A : FAMILIA_B

    cy.intercept('GET', '**/api/families', {
      statusCode: 200,
      body: [familia],
    }).as('matrizFamiliasBug')

    cy.intercept('GET', '**/api/tempos-setup', {
      statusCode: 200,
      body: [TRANSICAO_A_B],
    }).as('matrizTemposBug')
  },
)

When('abrir a matriz de setup', () => {
  cy.get('[data-cy="menu-matriz-setup"]')
    .should('be.visible')
    .click()

  cy.contains('h1', 'Matriz de setup').should('be.visible')

  cy.wait('@matrizFamiliasBug')
    .its('response.statusCode')
    .should('eq', 200)

  cy.wait('@matrizTemposBug')
    .its('response.statusCode')
    .should('eq', 200)
})

Then(
  'as famílias {string} e {string} devem aparecer nos dois eixos',
  (familiaA, familiaB) => {
    cy.get(`[data-cy="matriz-celula-${familiaA}-${familiaB}]`)
      .should('be.visible')

    cy.get(`[data-cy="matriz-celula-${familiaB}-${familiaA}]`)
      .should('be.visible')
  },
)

Then(
  'a transição de {string} para {string} deve indicar ausência de configuração',
  (origem, destino) => {
    cy.get(`[data-cy="matriz-celula-${origem}-${destino}]`)
      .should('contain.text', '—')
  },
)

Then('o contador deve indicar uma configuração', () => {
  cy.contains('1 configuração').should('be.visible')
})
