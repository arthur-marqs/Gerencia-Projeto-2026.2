# Q-07 — Ensaio de carga do SetupFlow

A meta é p95 de até 2.000 ms para cada operação e rodada. O protocolo inicia com um smoke de 10 s e 1 VU. As rodadas sequenciais usam 5 e 10 VUs, cada uma com aquecimento de 30 s e medição de 3 min. Cada VU faz uma pausa de 1 s após seu ciclo. O k6 dispõe de até 45 s para concluir iterações já iniciadas.

## Preparação e execução

1. Instale o k6 v2.4.0 e use o Python 3.11 com as dependências de `backend/requirements.txt`. [Instalação oficial do k6](https://grafana.com/docs/k6/latest/set-up/install-k6/)
2. Inicie um PostgreSQL descartável em loopback com um banco vazio `q07_base_test`. A conta exclusiva precisa poder criar bancos no cluster descartável. O executor migra e povoa a base e cria três cópias, `q07_smoke_test`, `q07_5_test` e `q07_10_test`. Use um cluster novo para repetir o protocolo.
3. Ao executar, deixe a porta local 8017 livre. Configure `DB_USER`, `DB_PASSWORD` e `DB_PORT` no ambiente. Use um diretório novo de saída e informe o SHA efetivamente avaliado.

```powershell
$sha = git rev-parse HEAD
$branch = git branch --show-current
$estado = if (git status --porcelain) { 'Árvore com alterações locais' } else { 'Árvore limpa' }
python tests/performance/run_q07.py --backend backend --out .tmp/q07-nova-execucao --commit $sha --branch $branch --estado $estado
python tests/performance/summarize_q07.py .tmp/q07-nova-execucao
```

Use `--k6 <caminho>` para um binário portátil. O executor usa Uvicorn em HTTP no loopback com um worker e inicia uma instância para cada banco. A configuração de cookie é a prevista pelo projeto para HTTP local. Cada VU tem uma conta fictícia e obtém uma sessão no preparo, antes de cronometrar as operações. Se o smoke falhar, o executor preserva as evidências e encerra antes das rodadas.

## Dados e operações

A massa inicial de cada rodada tem 10 contas de Planejador, 2 máquinas, 2 famílias, 4 produtos compatíveis, 2.280 ordens pendentes, 2 setups direcionais (8 e 13 min), 10 planos manuais e 2.240 sugestões de uma ordem reservadas para aprovações. Cada geração usa 4 ordens próprias do VU. A comparação recupera a sugestão recém-gerada para as mesmas 4 ordens. A aprovação consome uma sugestão exclusiva e deve retornar 201. Um reenvio idempotente com 200 reprova o cenário.

| Operação medida | Endpoint | Condição verificada |
| --- | --- | --- |
| Consultar ordens | `GET /api/ordens-producao` | HTTP 200, total previsto e ordem da conta de teste |
| Consultar famílias da matriz | `GET /api/families` | HTTP 200 e presença das famílias A e B |
| Consultar tempos da matriz | `GET /api/tempos-setup` | HTTP 200 e os dois tempos |
| Gerar sequência sugerida | `POST /api/planejamentos/sugestoes` | HTTP 201, quatro ordens e máquinas atribuídas |
| Comparar manual e sugerido | `GET /api/planejamentos/{id}/comparacao` | HTTP 200, plano e sugestão esperados e diferença de setup |
| Aprovar uma sugestão | `POST /api/planejamentos/aprovacoes` | HTTP 201, ordem esperada e status aprovado |
| Consultar planejamentos aprovados | `GET /api/planejamentos/aprovacoes` | HTTP 200 e presença da aprovação recém-gravada |

As duas consultas da matriz são disparadas em paralelo e reportadas separadamente. A consulta de aprovados foi incluída por servir à execução da produção. O ciclo usa sugestão preparada e mede a aprovação por POST. A listagem de candidatos, os cadastros auxiliares e a interface ficam fora da medição.

## Avaliação e evidências

O p95, a mediana, o máximo e o total são baseados em `Response.timings.duration` do k6, que soma envio, espera e recebimento da resposta HTTP. Renderização, espera por conexão e processamento da interface ficam fora do tempo reportado. Os indicadores incluem as requisições iniciadas na fase de medição e concluídas durante o período de graça.

Cada operação precisa ter 100 amostras por rodada oficial, p95 dentro da meta e nenhuma falha de transporte, status ou conteúdo para este cenário ser considerado válido. A exigência de zero falhas é uma condição deste ensaio. O k6 retorna código diferente de zero se um threshold for violado. A duração registrada de cada tentativa permanece na distribuição, inclusive em caso de falha. As contagens de erro são publicadas separadamente.

O manifesto contém comandos, horários, SHAs e códigos de saída. Os JSONs guardam o resultado da ferramenta, os CSVs preservam as durações individuais e os logs registram falhas. Para compartilhar evidências, selecione `manifesto.json`, `resultados-*.json`, `amostras-*.csv` e logs conferidos. A massa privada e o stream JSON bruto ficam na pasta de execução isolada.

O protocolo modela sete operações HTTP locais com dados sintéticos e gerador e serviços na mesma máquina. As aprovações e sugestões acumulam registros em cada rodada. Os limites observados aplicam-se ao escopo e à infraestrutura documentados.

## GitHub Actions

O workflow `Q-07 carga local` foi preparado com acionamento manual. Após integrá-lo ao GitHub, use **Actions → Q-07 carga local → Run workflow** e escolha a branch. O job prepara PostgreSQL isolado e publica a tabela no Summary e os artefatos mesmo se os thresholds falharem. Essa configuração usa um runner Linux e constitui outra medição quando for executada.
