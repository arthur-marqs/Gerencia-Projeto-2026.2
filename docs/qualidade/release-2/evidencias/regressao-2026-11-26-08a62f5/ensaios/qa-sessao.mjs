// Ensaio de QA avulso. Usa o Chrome descartável, API e frontend locais.
// No ensaio de restauração, a primeira consulta de identidade recebe um 503 simulado.
// O modo --medir-driver06 observa respostas reais.
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import { setTimeout as aguardar } from 'node:timers/promises'

const navegador = 'http://127.0.0.1:9234'
const frontend = 'http://localhost:5173'
const api = 'http://localhost:8000'
const senha = process.env.QA_AUDIT_FIXTURE_PASSWORD
assert.ok(senha && process.argv[2], 'Informe a senha da fixture e o caminho da evidência.')

const { Browser: versao } = await (await fetch(navegador + '/json/version')).json()
const abas = await (await fetch(navegador + '/json/list')).json()
const aba = abas.find(item => item.type === 'page' && item.url === 'about:blank')
assert.ok(aba, 'Use uma instância Chrome recém-aberta com perfil descartável.')
const socket = new WebSocket(aba.webSocketDebuggerUrl)
await new Promise((resolve, reject) => {
  socket.addEventListener('open', resolve, { once: true })
  socket.addEventListener('error', reject, { once: true })
})
let id = 0
const pendentes = new Map()
socket.addEventListener('message', ({ data }) => {
  const mensagem = JSON.parse(data)
  const callback = pendentes.get(mensagem.id)
  if (callback) {
    pendentes.delete(mensagem.id)
    callback(mensagem)
  }
})

function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const identificador = ++id
    pendentes.set(identificador, ({ error, result }) => {
      clearTimeout(prazo)
      if (error) reject(new Error(error.message))
      else resolve(result)
    })
    const prazo = setTimeout(() => {
      pendentes.delete(identificador)
      reject(new Error('Tempo esgotado no comando ' + method))
    }, 12_000)
    socket.send(JSON.stringify({ id: identificador, method, params }))
  })
}

async function avaliar(expression) {
  const resposta = await cdp('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })
  assert.equal(resposta.exceptionDetails, undefined, 'Falha ao inspecionar a página de teste.')
  return resposta.result.value
}

async function aguardarEstado(expressao) {
  for (let tentativa = 0; tentativa < 40; tentativa++) {
    try {
      if (await avaliar(expressao)) return
    } catch {
      // O contexto JavaScript pode ser substituído durante a navegação.
    }
    await aguardar(150)
  }
  throw new Error('A interface não chegou ao estado esperado.')
}

const nav = "Boolean(document.querySelector('nav[aria-label]'))"
const login = "Boolean(document.querySelector('[data-cy=login-email]'))"
const identidade = `fetch('${api}/api/auth/me', {credentials:'include'}).then(r => r.status)`

async function autenticarFixture() {
  return avaliar(`fetch('${api}/api/auth/login', {
    method: 'POST', credentials: 'include', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({email:'ana.e2e@example.com', password:${JSON.stringify(senha)}})
  }).then(r => r.status)`)
}

async function medirDriver06() {
  await cdp('Page.addScriptToEvaluateOnNewDocument', { source: `(() => {
    const fetchReal = window.fetch.bind(window);
    window.fetch = async (entrada, opcoes) => {
      const medicao = window.__qaMedicao;
      if (entrada !== '${api}/api/families') return fetchReal(entrada, opcoes);
      if (medicao) medicao.inicio = performance.now();
      const resposta = await fetchReal(entrada, opcoes);
      await resposta.clone().arrayBuffer();
      window.__qaFamiliasHttp = resposta.status;
      if (medicao) {
        medicao.http = resposta.status;
        medicao.respostaMs = performance.now() - medicao.inicio;
      }
      return resposta;
    };
    new MutationObserver(() => {
      const medicao = window.__qaMedicao;
      if (medicao?.inicio !== undefined && medicao.loginMs === undefined &&
          document.querySelector('[data-cy=login-email]')) {
        medicao.loginMs = performance.now() - medicao.inicio;
      }
    }).observe(document, { childList: true, subtree: true });
  })();` })
  const amostras = []
  for (const estado of ['expirada', 'invalidada']) {
    for (let tentativa = 1; tentativa <= 10; tentativa++) {
      await cdp('Page.navigate', { url: frontend + '/?qa=preparar-' + estado + '-' + tentativa })
      await aguardarEstado('location.search === ' + JSON.stringify('?qa=preparar-' + estado + '-' + tentativa))
      assert.equal(await autenticarFixture(), 200)
      await cdp('Page.navigate', { url: frontend + '/?qa=medir-' + estado + '-' + tentativa })
      await aguardarEstado(nav)
      assert.equal(await avaliar(identidade), 200)
      await avaliar(`[...document.querySelectorAll('nav button')]
        .find(b => b.textContent.trim() === 'Famílias de produtos').click()`)
      const botao = "[...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Atualizar lista')"
      await aguardarEstado('window.__qaFamiliasHttp === 200 && Boolean(' + botao + ' && !(' + botao + ').disabled)')
      if (estado === 'expirada') {
        execFileSync(process.env.QA_AUDIT_PSQL || 'psql', [
          '-h', '127.0.0.1', '-p', '55483', '-U', 'qa_cycle', '-d', 'release2_main_e2e_test',
          '-c', "UPDATE sessoes SET criada_em=now()-interval '2 days', expira_em=now()-interval '1 day' WHERE invalidada_em IS NULL",
        ], { stdio: 'ignore', windowsHide: true })
      } else {
        const { cookies } = await cdp('Network.getCookies', { urls: [api] })
        const sessao = cookies.find(cookie => cookie.name === 'setupflow_session')
        assert.ok(sessao, 'Sessão da fixture indisponível.')
        const logout = await fetch(api + '/api/auth/logout', {
          method: 'POST', headers: { Cookie: 'setupflow_session=' + sessao.value },
        })
        assert.equal(logout.status, 204)
      }
      await avaliar('window.__qaMedicao = {}; ' + botao + '.click()')
      try {
        await aguardarEstado('window.__qaMedicao?.loginMs !== undefined && ' + login)
      } catch (erro) {
        const observado = await avaliar(`({medicao: window.__qaMedicao, login: ${login}, familias: window.__qaFamiliasHttp})`)
        throw new Error(`Medição ${estado}/${tentativa}: ${JSON.stringify(observado)}`, { cause: erro })
      }
      const { http, respostaMs, loginMs } = await avaliar('window.__qaMedicao')
      assert.equal(http, 401)
      assert.ok(loginMs >= respostaMs)
      assert.equal(await avaliar(nav), false)
      amostras.push({ estado, tentativa, http, respostaMs, loginMs })
    }
  }
  await writeFile(process.argv[2], JSON.stringify({ versao, amostras }, null, 2) + '\n')
}

try {
  await cdp('Page.enable')
  if (process.argv.includes('--medir-driver06')) {
    await medirDriver06()
  } else {
    await cdp('Page.navigate', { url: frontend + '/?qa=controle' })
    await aguardarEstado(login)
    const autenticacaoHttp = await autenticarFixture()
    assert.equal(autenticacaoHttp, 200)
    await cdp('Page.navigate', { url: frontend + '/?qa=controle-sessao' })
    await aguardarEstado(nav)
    assert.equal(await avaliar(identidade), 200)

    const amostras = []
    for (let tentativa = 1; tentativa <= 3; tentativa++) {
      const { identifier } = await cdp('Page.addScriptToEvaluateOnNewDocument', {
        source: `(() => {
          const fetchReal = window.fetch.bind(window);
          window.fetch = (entrada, opcoes) => {
            if (entrada !== '${api}/api/auth/me') return fetchReal(entrada, opcoes);
            window.fetch = fetchReal;
            window.__qaIdentidadeSimulada = 503;
            return Promise.resolve(new Response('{"detail":"Indisponível no ensaio de QA"}', {
              status: 503, headers: {'Content-Type': 'application/json'}
            }));
          };
        })();`,
      })
      await cdp('Page.navigate', { url: frontend + '/?qa=temporario-' + tentativa })
      await aguardarEstado('window.__qaIdentidadeSimulada === 503 && ' + login)
      await cdp('Page.removeScriptToEvaluateOnNewDocument', { identifier })
      const identidadeRealHttp = await avaliar(identidade)
      assert.equal(identidadeRealHttp, 200)
      await avaliar("window.dispatchEvent(new Event('focus'))")
      await aguardar(2000)
      assert.equal(await avaliar(login), true)
      assert.equal(await avaliar(nav), false)
      await cdp('Page.navigate', { url: frontend + '/?qa=recuperado-' + tentativa })
      await aguardarEstado(nav)
      assert.equal(await avaliar(identidade), 200)
      amostras.push({
        tentativa, falhaInicialSimuladaHttp: 503, identidadeRealHttp,
        loginAposRecuperacaoEFoco: true, painelAposRecarregarSemNovoLogin: true,
      })
    }
    await writeFile(process.argv[2], JSON.stringify({ versao, autenticacaoHttp, amostras }, null, 2) + '\n')
  }
} finally {
  socket.close()
}
