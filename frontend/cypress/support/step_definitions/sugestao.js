import { After, Before, Given, Then, When } from '@badeball/cypress-cucumber-preprocessor'

const API = 'http://localhost:8000/api'
const SUGESTOES = '/planejamentos/sugestoes'
const SENHA = 'SenhaE2E!2026'
const NOME_PLANO = 'Planejamento manual US13'
const PAINEL = '[aria-labelledby="titulo-sugestao"]'
const BOTAO_GERAR = '[data-cy="gerar-sugestao"]'
const COMPARACAO = '[data-cy="comparacao-sequencias"]'
const MANUAL = '[data-cy="sequencia-manual"]'
const SUGERIDA = '[data-cy="sequencia-sugerida"]'
const AVISO_CATALOGO = '[data-cy="aviso-catalogo-maquinas"]'

let estado
let planejamentoManual
let sugestaoGerada
let respostaOperador

const codigos = (lista) => lista.split(',').map((codigo) => codigo.trim())
const idsDasOrdens = (lista) => codigos(lista).map((codigo) => estado.ordens[codigo].id)
const cardDoPlano = () => cy.contains('[data-cy="planejamento-card"]', NOME_PLANO)
const inspecionarSugestoes = () => cy.task('e2e:inspecionar-sugestoes', null, { log: false })

function requisitar(method, rota, body, status = 200) {
  return cy.request({ method, url: API + rota, body, failOnStatusCode: false, log: false })
    .then((resposta) => {
      expect(resposta.status, `${method} ${rota}`).to.equal(status)
      return resposta.body
    })
}

function autenticar(usuario) {
  return requisitar('POST', '/auth/login', { email: estado.usuarios[usuario].email, password: SENHA })
}

function cadastrarSetup(origem, destino, minutos) {
  return requisitar('POST', '/tempos-setup', {
    familia_origem_id: estado.familias[origem],
    familia_destino_id: estado.familias[destino],
    tempo_setup_minutos: minutos,
  }, 201)
}

function navegarAoPlanejamento() {
  cy.get('[data-cy="menu-planejamentos"]').click()
  return cy.get(BOTAO_GERAR).should('be.enabled')
}

function abrirPlanejamento() {
  cy.intercept('POST', `**/api${SUGESTOES}`).as('gerarSugestao')
  cy.visit('/')
  return navegarAoPlanejamento()
}

function conferirSugestaoNaTela(sugestao) {
  const codigosPorId = Object.fromEntries(
    Object.entries(estado.ordens).map(([codigo, ordem]) => [ordem.id, codigo]),
  )
  const ordensEsperadas = sugestao.itens.map(({ ordem_id }) => codigosPorId[ordem_id])
  cy.get(PAINEL).find('[role="status"]')
    .should('contain.text', `${sugestao.tempo_setup_total_minutos} minutos`)
  return cy.get(PAINEL).find('[data-cy="sugestao-ordem"]').should(($ordens) => {
    expect($ordens.toArray().map((ordem) => ordem.textContent)).to.deep.equal(ordensEsperadas)
  })
}

function verificarGeracao(minutos, verificarOrdens) {
  return cy.wait('@gerarSugestao').its('response').then(({ statusCode, body }) => {
    expect(statusCode).to.equal(201)
    expect(body.tempo_setup_total_minutos).to.equal(minutos)
    verificarOrdens(body.itens.map(({ ordem_id }) => ordem_id))
    sugestaoGerada = body
    return conferirSugestaoNaTela(body)
  })
}

Before({ tags: '@US13 or @US14 or @US15 or @US16' }, () => {
  planejamentoManual = undefined
  sugestaoGerada = undefined
  respostaOperador = undefined
  return cy.task('e2e:reset', 'sugestao', { log: false }).then((dados) => { estado = dados })
})

After({ tags: '@US13 and not @CT85' }, ({ pickle }) => {
  const caso = pickle.tags.find(({ name }) => /^@CT\d+$/.test(name))
  return cy.screenshot(caso.name.replace('@CT', 'CT-'), { capture: 'viewport' })
})

Given('que o Planejador está autenticado para gerar sugestões', () => autenticar('ana'))

Given('que os tempos são de {int} minutos de A para B e {int} minutos de B para A', (ab, ba) => {
  cadastrarSetup('A', 'B', ab)
  return cadastrarSetup('B', 'A', ba)
})

Given('que somente o tempo de A para B está cadastrado com {int} minutos', (minutos) => (
  cadastrarSetup('A', 'B', minutos)
))

Given('que não há tempos de troca cadastrados', () => (
  requisitar('GET', '/tempos-setup').should('deep.equal', [])
))

function verificarAusenciaDePlanejamento() {
  return requisitar('GET', '/planejamentos').should('deep.equal', [])
}

Given('que ainda não existe planejamento manual', verificarAusenciaDePlanejamento)
Then('nenhum planejamento manual deve ser criado automaticamente', verificarAusenciaDePlanejamento)

Given('que existe um planejamento manual para {string}', (lista) => {
  return requisitar('POST', '/planejamentos', { nome: NOME_PLANO, ordens_ids: idsDasOrdens(lista) }, 201)
    .then((plano) => { planejamentoManual = plano })
})

Given('que já existe uma sugestão para esse planejamento', () => {
  const ordens_ids = planejamentoManual.itens.map(({ ordem_id }) => ordem_id)
  return requisitar('POST', SUGESTOES, { ordens_ids }, 201)
    .then((sugestao) => { sugestaoGerada = sugestao })
})

When('selecionar {string} para a sugestão', (lista) => {
  abrirPlanejamento()
  for (const codigo of codigos(lista)) {
    cy.contains('label', new RegExp(`^${codigo}$`)).find('input[type="checkbox"]').check()
  }
})

When('abrir o planejamento para sugerir sem selecionar ordens', abrirPlanejamento)

When('abrir o planejamento manual para editar', () => {
  abrirPlanejamento()
  cardDoPlano().contains('button', 'Editar').click()
  cy.get('[data-cy="nome-planejamento"]').should('have.value', NOME_PLANO)
})

When('solicitar a sequência sugerida', () => cy.get(BOTAO_GERAR).click())

When('associar o produto de {string} à família A e cadastrar B para A com {int} minutos', (codigo, minutos) => {
  requisitar('PATCH', `/produtos/${estado.ordens[codigo].produto_id}/familia`, { family_id: estado.familias.A })
  return cadastrarSetup('B', 'A', minutos)
})

When('recarregar a tela e consultar a sugestão do planejamento', () => {
  cy.intercept('GET', `**/api/planejamentos/${planejamentoManual.id_planejamento}/sugestao`).as('consultarSugestao')
  cy.reload()
  navegarAoPlanejamento()
  return cardDoPlano().contains('button', 'Consultar sugestão').click()
})

When('o Operador solicitar a mesma sugestão diretamente à API', () => {
  const ordens_ids = planejamentoManual.itens.map(({ ordem_id }) => ordem_id)
  autenticar('operador')
  return requisitar('POST', SUGESTOES, { ordens_ids }, 403)
    .then((resposta) => { respostaOperador = resposta })
})

Then('{string} devem vir antes de {string} com setup total de {int} minutos', (familiaA, ordemB, minutos) => (
  verificarGeracao(minutos, (ordens) => {
    expect(ordens.slice(0, -1)).to.have.members(idsDasOrdens(familiaA))
    expect(ordens.at(-1)).to.equal(estado.ordens[ordemB].id)
  })
))

Then('a sequência sugerida deve ser {string} com setup total de {int} minutos', (lista, minutos) => (
  verificarGeracao(minutos, (ordens) => expect(ordens).to.deep.equal(idsDasOrdens(lista)))
))

Then('a sugestão deve conter exatamente {string} com setup total de {int} minutos', (lista, minutos) => (
  verificarGeracao(minutos, (ordens) => expect(ordens).to.have.members(idsDasOrdens(lista)))
))

Then('a geração deve ser rejeitada com {string}', (mensagem) => {
  cy.wait('@gerarSugestao').its('response').then(({ statusCode, body }) => {
    expect(statusCode).to.equal(422)
    expect(body.detail).to.include(mensagem)
  })
  cy.get('main [role="alert"]').should('be.visible').and('contain.text', mensagem)
  cy.get(PAINEL).should('not.exist')
})

Then('o erro de geração também deve indicar {string}', (mensagem) => (
  cy.get('main [role="alert"]').should('contain.text', mensagem)
))

Then('nenhuma sugestão deve ter sido gravada', () => (
  inspecionarSugestoes().should('deep.equal', { sugestoes: 0, itens: 0 })
))

Then('deve existir uma única sugestão gravada com {int} itens', (itens) => (
  inspecionarSugestoes().should('deep.equal', { sugestoes: 1, itens })
))

Then('a tela deve pedir a seleção de pelo menos uma ordem', () => {
  cy.get('main [role="alert"]').should('be.visible').and('contain.text', 'Selecione pelo menos uma ordem')
  cy.get('@gerarSugestao.all').should('have.length', 0)
  cy.get(PAINEL).should('not.exist')
})

Then('a mesma sugestão deve ser recuperada com as ordens manuais preservadas', () => {
  cy.wait('@consultarSugestao').its('response').then(({ statusCode, body }) => {
    expect(statusCode).to.equal(200)
    expect(body).to.deep.equal(sugestaoGerada)
    return conferirSugestaoNaTela(body)
  })
  return requisitar('GET', `/planejamentos/${planejamentoManual.id_planejamento}`)
    .should('deep.equal', planejamentoManual)
})

When('solicitar a comparação do planejamento', () => {
  cy.intercept('GET', `**/api/planejamentos/${planejamentoManual.id_planejamento}/comparacao`).as('comparar')
  abrirPlanejamento()
  return cardDoPlano().find('[data-cy="comparar-sequencias"]').click()
})

Given('que o catálogo de máquinas responde 503', () => (
  cy.intercept('GET', '**/api/maquinas', {
    statusCode: 503,
    body: { detail: 'Indisponibilidade simulada do catálogo.' },
  }).as('catalogoIndisponivel')
))

When('o catálogo voltar a ficar disponível', () => (
  cy.intercept('GET', '**/api/maquinas', (pedido) => pedido.continue()).as('catalogoRestaurado')
))

Then('o Planejador deve ver o aviso do catálogo e a ordem pendente {string}', (codigo) => {
  cy.wait('@catalogoIndisponivel').its('response.statusCode').should('eq', 503)
  cy.get(AVISO_CATALOGO).should('be.visible').and('contain.text', 'Catálogo de máquinas indisponível.')
  cy.contains('label', new RegExp(`^${codigo}$`)).find('input[type="checkbox"]').should('be.enabled')
  const maquinaId = sugestaoGerada.itens[0].maquina_id
  cy.get(SUGERIDA).should('contain.text', `Máquina ${maquinaId.slice(0, 8)}`)
})

Then('a comparação deve voltar a mostrar a máquina {string} pelo nome', (codigoMaquina) => {
  cy.wait('@catalogoRestaurado').its('response.statusCode').should('eq', 200)
  cy.get(AVISO_CATALOGO).should('not.exist')
  cy.get(COMPARACAO).find(SUGERIDA).should('contain.text', `${codigoMaquina} — Máquina ${codigoMaquina}`)
})

Then('a comparação deve exibir a sequência manual {string} e a sugerida {string}', (manual, sugerida) => {
  cy.wait('@comparar').its('response.statusCode').should('eq', 200)
  cy.get(COMPARACAO).should('be.visible').and('contain.text', NOME_PLANO)
  for (const [seletor, lista] of [[MANUAL, manual], [SUGERIDA, sugerida]]) {
    cy.get(COMPARACAO).find(seletor).find('[data-cy="ordem-comparada"]').should(($ordens) => {
      expect($ordens.toArray().map((ordem) => ordem.textContent)).to.deep.equal(codigos(lista))
    })
  }
})

Then('deve destacar as duas ordens que mudaram de posição', () => {
  cy.get(COMPARACAO).find('[role="status"]').should('have.text', '2 de 3 ordens mudaram de posição.')
  cy.get(MANUAL).find('[data-cy="posicao-alternativa"]').should(($posicoes) => {
    expect($posicoes.toArray().map((posicao) => posicao.textContent)).to.deep.equal([
      '3º na sugerida', '2º na sugerida',
    ])
  })
})

Then('deve mostrar {int} minutos de setup manual e {int} minutos de setup sugerido', (manual, sugerido) => {
  cy.get(COMPARACAO).find('[data-cy="setup-manual"]').should('have.text', `${manual} min`)
  cy.get(COMPARACAO).find('[data-cy="setup-sugerido"]').should('have.text', `${sugerido} min`)
  cy.get(COMPARACAO).find('[data-cy="diferenca-setup"]').should('have.text', `${manual - sugerido} min a menos`)
})

Then('a comparação deve pedir que a sequência sugerida seja gerada', () => {
  const mensagem = 'Gere uma sequência sugerida para este planejamento antes de comparar.'
  cy.wait('@comparar').its('response').then(({ statusCode, body }) => {
    expect(statusCode).to.equal(404)
    expect(body).to.deep.equal({ detail: mensagem })
  })
  cy.get('main [role="alert"]').should('be.visible').and('have.text', mensagem)
  cy.get(COMPARACAO).should('not.exist')
})

Then('os registros do planejamento manual e da sugestão devem permanecer iguais', () => {
  requisitar('GET', `/planejamentos/${planejamentoManual.id_planejamento}`)
    .should('deep.equal', planejamentoManual)
  return requisitar('GET', `${SUGESTOES}/${sugestaoGerada.id_sugestao}`).should('deep.equal', sugestaoGerada)
})

Then('a API deve negar a geração, preservar os registros e retornar somente a mensagem de acesso negado', () => {
  expect(respostaOperador).to.deep.equal({ detail: 'Acesso não autorizado para este perfil.' })
  inspecionarSugestoes().should('deep.equal', { sugestoes: 1, itens: planejamentoManual.itens.length })
  autenticar('ana')
  requisitar('GET', '/planejamentos').should('deep.equal', [planejamentoManual])
  return requisitar('GET', `${SUGESTOES}/${sugestaoGerada.id_sugestao}`)
    .should('deep.equal', sugestaoGerada)
})


After({ tags: '@US14' }, ({ pickle }) => {
  const caso = pickle.tags.find(({ name }) => /^@US14_CT\d+$/.test(name))
  return cy.screenshot(caso.name.slice(1), { capture: 'viewport' })
})

Given('que a ordem {string} tem prazo em {int} dias, prioridade {string} e duração de {int} minutos', (codigo, dias, prioridade, duracao) => {
  const prazo = new Date()
  prazo.setUTCDate(prazo.getUTCDate() + dias)
  const rota = `/ordens-producao/${estado.ordens[codigo].id}`

  requisitar('PUT', rota, { prazo: prazo.toISOString().slice(0, 10), prioridade })
  return requisitar('PATCH', `${rota}/duracao-estimada`, { duracao_estimada_minutos: duracao })
})

After({ tags: '@US15' }, ({ pickle }) => {
  const caso = pickle.tags.find(({ name }) => /^@US15_CT\d+$/.test(name))
  return cy.screenshot(caso.name.replace('@', ''), { capture: 'viewport' })
})

Given('que existe uma máquina adicional {string}', (codigo) => {
  return requisitar('POST', '/maquinas', {
    codigo,
    nome: `Máquina ${codigo}`,
  }, 201).then((maquina) => {
    estado.maquinas[codigo] = maquina.id_maquina
  })
})

Given('que o produto de {string} é compatível com {string}', (ordem, lista) => {
  return requisitar('PUT', `/produtos/${estado.ordens[ordem].produto_id}/maquinas`, {
    maquinas_ids: codigos(lista).map((codigo) => estado.maquinas[codigo]),
  })
})

Given('que o produto de {string} não possui máquinas compatíveis', (ordem) => {
  return requisitar('PUT', `/produtos/${estado.ordens[ordem].produto_id}/maquinas`, {
    maquinas_ids: [],
  })
})

Given('que a máquina {string} está inativa', (codigo) => {
  return requisitar('PATCH', `/maquinas/${estado.maquinas[codigo]}/status`, {
    ativo: false,
  })
})

Then('a sugestão deve apresentar as atribuições {string} com setup total de {int} minutos', (lista, minutos) => {
  const esperadas = Object.fromEntries(
    codigos(lista).map((atribuicao) => {
      const [ordem, maquina] = atribuicao.split(':')
      return [estado.ordens[ordem].id, estado.maquinas[maquina]]
    }),
  )

  return cy.wait('@gerarSugestao').its('response').then(({ statusCode, body }) => {
    expect(statusCode).to.equal(201)
    expect(body.tempo_setup_original_minutos).to.equal(minutos)
    expect(body.tempo_setup_total_minutos).to.equal(minutos)

    const atribuicoes = Object.fromEntries(
      body.itens.map((item) => [item.ordem_id, item.maquina_id]),
    )

    expect(body.itens).to.have.length(Object.keys(esperadas).length)
    expect(atribuicoes).to.deep.equal(esperadas)

    sugestaoGerada = body
    conferirSugestaoNaTela(body)

    for (const atribuicao of codigos(lista)) {
      const [ordem, maquina] = atribuicao.split(':')

      cy.get(PAINEL)
        .contains('[data-cy="sugestao-ordem"]', ordem)
        .closest('li')
        .find('[data-cy="sugestao-maquina"]')
        .should('be.visible')
        .and('contain.text', maquina)
    }
  })
})
