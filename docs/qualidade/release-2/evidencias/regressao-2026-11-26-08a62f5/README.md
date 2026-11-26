# Evidências do ciclo R2-REG-20261126-08a62f5

Execuções de 26/11/2026, America/Sao_Paulo. A versão integrada é `08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`. A versão complementar é `ee2a4a88aea0018cb451c8f9988346fe25551e7a`. Os prefixos `main-` e `corrigida-` identificam as respectivas cópias.

- [Manifesto de comandos, horários e resultados](manifesto.json)
- [Consulta de issues, commits, revisões e CI no GitHub](github.json)
- [JUnit completo do Pytest da main](main-pytest/junit.xml)
- [Fluxo RG-01 e as duas variantes do BUG-004 na main](main-fluxo-bug004/junit.xml) · [Versão corrigida](corrigida-fluxo-bug004/junit.xml)
- [Driver01, amostras de interrupção e recuperação](main-driver01-http/amostras.jsonl)
- [Driver04, matriz de autorização e preservação do banco](main-driver04-matriz-valida/junit.xml)
- [Driver06, amostras HTTP por condição](main-driver06-http/)

## Evidências de navegador

- [Regressão Chrome](main-regressao-chrome/run-summary.json) · [Regressão Electron](main-regressao-electron/run-summary.json).
- [Autenticação Chrome na main](main-auth-chrome/run-summary.json) · [Autenticação na versão corrigida](corrigida-auth-chrome/run-summary.json).
- [Driver06, tempos no navegador](main-driver06-chrome/amostras.json).
- [BUG-005 na main](main-bug005-integrado/junit.xml) · [BUG-005 na versão corrigida](corrigida-bug005-integrado/junit.xml).

## Reprodução e privacidade

- O [registro de regressão](../../regressao-release-2.md) vincula os resultados às histórias, ao plano verificável e aos retestes. O [relatório de qualidade](../../../../releases/release2/relatorio-qualidade-release-2.md) contém o parecer para a versão integrada.
- O diretório [ensaios](ensaios/) guarda os instrumentos auxiliares usados neste ciclo. O Driver01 reutilizou o [script de desconexão versionado](../../evidencias-driver01/qa_desconexao.py). O reteste de navegador do BUG-005 copiou duas specs de suporte para a cópia isolada durante a execução. O código do produto e as suítes oficiais vieram dos respectivos commits.
- O manifesto guarda SHA-256 antes do saneamento e identifica relatórios por comando. Logs brutos, capturas e a saída da preparação de contas ficaram na área local ignorada do ciclo. As cópias deste diretório removem credenciais, cookies, endereços de e-mail e caminhos pessoais. Os JUnits mantêm identificação dos testes, estados, propriedades e mensagens de falha selecionadas.
