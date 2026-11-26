// Ensaio de QA avulso com respostas HTTP simuladas.
const rotaOrdens = '**/api/ordens-producao'
const produto = { id_produto: 'produto-qa', codigo: 'P-QA', nome: 'Produto QA', unidade: 'un', ativo: true }
const ordem = {
  id_ordem: 'ordem-qa', codigo: 'OP-BASE', produto_id: produto.id_produto,
  quantidade: '5', duracao_estimada_minutos: 30, status: 'PENDENTE',
  prazo: null, prioridade: null, criado_em: '2026-11-25T12:00:00Z',
}

function falharUmaVez(method, url, statusCode, body) {
  let chamadas = 0
  cy.intercept(method, url, (req) => {
    chamadas += 1
    req.reply(chamadas === 1
      ? { statusCode: 503, body: { detail: 'Não foi possível confirmar a gravação.' } }
      : { statusCode, body })
  }).as('gravar')
}

function verificarFalha(mensagem) {
  cy.wait('@gravar').its('response.statusCode').should('eq', 503)
  cy.contains('[role=alert]', mensagem).should('be.visible')
  cy.get('[role=status]').should('not.exist')
}

beforeEach(() => {
  cy.intercept('GET', '**/api/auth/me', { usuario: { nome: 'Planejador QA', perfis: ['PLANEJADOR'] } })
  cy.intercept('GET', '**/api/produtos', [produto])
  cy.intercept('GET', rotaOrdens, [ordem]).as('consultar')
  cy.visit('/')
  cy.contains('nav button', 'Ordens de produção').click()
  cy.wait('@consultar')
})

it('informa falha no cadastro e confirma somente a resposta de sucesso', () => {
  falharUmaVez('POST', rotaOrdens, 201, { ...ordem, id_ordem: 'ordem-nova', codigo: 'OP-NOVA' })
  cy.get('#ordem-codigo').type('OP-NOVA')
  cy.get('#ordem-produto').select(produto.id_produto)
  cy.get('#ordem-quantidade').type('5')
  cy.contains('button', 'Cadastrar ordem').click()
  verificarFalha('Não foi possível cadastrar a ordem.')
  cy.contains('td', 'OP-NOVA').should('not.exist')
  cy.contains('button', 'Cadastrar ordem').click()
  cy.wait('@gravar').its('response.statusCode').should('eq', 201)
  cy.contains('[role=status]', 'Ordem OP-NOVA cadastrada').should('be.visible')
})

it('informa falha na duração e confirma somente a resposta de sucesso', () => {
  falharUmaVez('PATCH', `${rotaOrdens}/${ordem.id_ordem}/duracao-estimada`, 200, {
    ...ordem, duracao_estimada_minutos: 45,
  })
  cy.get(`#duracao-${ordem.id_ordem}`).clear().type('45')
  cy.contains('button', /^Salvar$/).click()
  verificarFalha('Não foi possível salvar a duração estimada.')
  cy.contains('button', /^Salvar$/).click()
  cy.wait('@gravar').its('response.statusCode').should('eq', 200)
  cy.contains('[role=status]', 'Duração estimada salva.').should('be.visible')
})

it('informa falha no prazo e na prioridade e confirma somente a resposta de sucesso', () => {
  const prazo = '2099-12-15'
  falharUmaVez('PUT', `${rotaOrdens}/${ordem.id_ordem}`, 200, { ...ordem, prazo, prioridade: 'Alta' })
  cy.contains('button', 'Editar').click()
  cy.get('#ordem-prazo').type(prazo)
  cy.get('#ordem-prioridade').select('Alta')
  cy.contains('button', 'Confirmar alteração').click()
  verificarFalha('Não foi possível atualizar a ordem.')
  cy.contains('td', 'Não definida').should('be.visible')
  cy.contains('button', 'Confirmar alteração').click()
  cy.wait('@gravar').its('response.statusCode').should('eq', 200)
  cy.contains('[role=status]', 'Prazo e prioridade da ordem OP-BASE atualizados.').should('be.visible')
})
