import http from 'k6/http';
import exec from 'k6/execution';
import { sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const host = __ENV.Q07_API || 'http://127.0.0.1:8017';
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+$/.test(host)) {
  throw new Error('A Q-07 requer uma API de teste em loopback.');
}
const massa = JSON.parse(open(__ENV.Q07_MASSA));
const vus = Number(__ENV.Q07_VUS);
const fase = __ENV.Q07_FASE;
const fases = { smoke: '10s', aquecimento: '30s', medicao: '3m' };
if (!(fase in fases) || (fase === 'smoke' ? vus !== 1 : ![5, 10].includes(vus))) {
  throw new Error('Informe a fase e o número de VUs previstos no protocolo.');
}
if (!__ENV.Q07_FIXTURE_PASSWORD || !__ENV.Q07_SUMMARY || massa.contas.length < vus) {
  throw new Error('Configuração do ensaio incompleta.');
}
const operacoes = [
  'ordens', 'matriz_familias', 'matriz_tempos', 'geracao', 'comparacao', 'aprovacao', 'aprovados',
];
const metricas = {};
const thresholds = {};
for (const nome of operacoes) {
  const duracao = `q07_${nome}_ms`;
  const amostras = `q07_${nome}_amostras`;
  const falhas = `q07_${nome}_falhas`;
  metricas[nome] = {
    duracao: new Trend(duracao, true),
    amostras: new Counter(amostras),
    falhas: new Counter(falhas),
  };
  thresholds[duracao] = ['p(95)<=2000'];
  thresholds[amostras] = [fase === 'medicao' ? 'count>=100' : 'count>=1'];
  thresholds[falhas] = ['count==0'];
}

export const options = {
  scenarios: { q07: { executor: 'constant-vus', vus, duration: fases[fase], gracefulStop: '45s' } },
  thresholds,
  summaryTrendStats: ['count', 'med', 'p(95)', 'max', 'min'],
  systemTags: ['status', 'method', 'name', 'error_code', 'scenario', 'expected_response'],
  maxRedirects: 0,
};

function params(nome, sessao) {
  return {
    tags: { name: nome, operacao: nome, fase }, timeout: '30s',
    headers: { 'Content-Type': 'application/json' },
    cookies: sessao ? { setupflow_session: sessao } : {},
  };
}

export function setup() {
  const sessoes = [];
  for (const { email } of massa.contas.slice(0, vus)) {
    const resposta = http.post(`${host}/api/auth/login`,
      JSON.stringify({ email, password: __ENV.Q07_FIXTURE_PASSWORD }), params('preparo_login'));
    const cookie = resposta.cookies.setupflow_session?.[0]?.value;
    if (resposta.status !== 200 || !cookie) {
      exec.test.abort(`Login de preparação falhou (HTTP ${resposta.status}).`);
    }
    sessoes.push(cookie);
  }
  return sessoes;
}

function registrar(nome, resposta, status, validar) {
  let corpo;
  let tipo = resposta.status === 0 ? 'transporte' : 'status';
  let valido = resposta.status === status;
  if (valido) {
    tipo = 'conteudo';
    try {
      corpo = resposta.json();
      valido = Boolean(validar(corpo));
    } catch {
      valido = false;
    }
  }
  const m = metricas[nome];
  m.duracao.add(resposta.timings.duration);
  m.amostras.add(1);
  m.falhas.add(valido ? 0 : 1);
  if (!valido) {
    console.error(`Q07 operacao=${nome} falha=${tipo} status=${resposta.status} codigo=${resposta.error_code || 0}`);
  }
  return valido ? corpo : null;
}

export default function (sessoes) {
  const indice = exec.vu.idInTest - 1;
  const conta = massa.contas[indice];
  const alvo = conta.aprovacoes[(fase === 'medicao' ? 40 : 0) + exec.vu.iterationInScenario];
  if (!alvo) exec.test.abort('Pool de aprovações esgotado.');
  const sessao = sessoes[indice];
  const get = (rota, nome) => http.get(host + rota, params(nome, sessao));
  const post = (rota, nome, corpo) => http.post(host + rota, JSON.stringify(corpo), params(nome, sessao));
  const base = '/api/planejamentos';
  registrar('ordens', get('/api/ordens-producao', 'ordens'), 200,
    linhas => Array.isArray(linhas) && linhas.length === massa.massa.ordens &&
      linhas.some(item => item.id_ordem === conta.ordens[0]));
  const [familias, tempos] = http.batch([
    ['GET', `${host}/api/families`, null, params('matriz_familias', sessao)],
    ['GET', `${host}/api/tempos-setup`, null, params('matriz_tempos', sessao)],
  ]);
  registrar('matriz_familias', familias, 200, linhas => Array.isArray(linhas) &&
    ['Q07-A', 'Q07-B'].every(code => linhas.some(it => it.code === code)));
  registrar('matriz_tempos', tempos, 200, linhas => Array.isArray(linhas) && linhas.length === 2 &&
    [8, 13].every(min => linhas.some(it => it.tempo_setup_minutos === min)));
  const sugestao = registrar('geracao', post(`${base}/sugestoes`, 'geracao', { ordens_ids: conta.ordens }), 201,
    corpo => corpo.id_sugestao && corpo.itens.length === conta.ordens.length &&
      conta.ordens.every(id => corpo.itens.some(it => it.ordem_id === id && it.maquina_id)));
  registrar('comparacao', get(`${base}/${conta.plano}/comparacao`, 'comparacao'), 200,
    corpo => sugestao && corpo.planejamento.id_planejamento === conta.plano &&
      corpo.sugestao.id_sugestao === sugestao.id_sugestao && Number.isFinite(corpo.setup.diferenca_minutos));
  const aprovada = registrar('aprovacao', post(`${base}/aprovacoes`, 'aprovacao', {
    origem: 'sugerida', origem_id: alvo.sugestao, ordens_ids: [alvo.ordem],
  }), 201, corpo => corpo.id_aprovacao && corpo.status === 'APROVADO' &&
    corpo.origem_id === alvo.sugestao && corpo.itens.length === 1 &&
    corpo.itens[0].ordem_id === alvo.ordem && corpo.itens[0].maquina_id);
  registrar('aprovados', get(`${base}/aprovacoes`, 'aprovados'), 200,
    linhas => aprovada && Array.isArray(linhas) &&
      linhas.some(item => item.id_aprovacao === aprovada.id_aprovacao && item.status === 'APROVADO'));
  sleep(1);
}

export function handleSummary(data) {
  const resultados = operacoes.map(operacao => {
    const valores = nome => data.metrics[`q07_${operacao}_${nome}`]?.values || {};
    const tempo = valores('ms');
    return {
      operacao, amostras: valores('amostras').count || 0,
      p50_ms: tempo.med ?? null, p95_ms: tempo['p(95)'] ?? null,
      max_ms: tempo.max ?? null, min_ms: tempo.min ?? null,
      falhas: valores('falhas').count || 0,
    };
  });
  const resumo = { fase, vus, duracao: fases[fase], massa: massa.massa, resultados,
    iteracoes: data.metrics.iterations?.values.count || 0, duracao_total_ms: data.state.testRunDurationMs };
  const saida = JSON.stringify(resumo, null, 2) + '\n';
  return { [__ENV.Q07_SUMMARY]: saida, stdout: saida };
}
