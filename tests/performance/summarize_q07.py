"""Gera a tabela Q-07 a partir dos resumos do k6."""
import json
import sys
from pathlib import Path

OPERACOES = {
    "ordens": "Consultar ordens",
    "matriz_familias": "Matriz — famílias",
    "matriz_tempos": "Matriz — tempos",
    "geracao": "Gerar sugestão",
    "comparacao": "Comparar manual e sugerido",
    "aprovacao": "Aprovar sugestão",
    "aprovados": "Consultar aprovados",
}


def outcome(row):
    if row["falhas"]:
        return "Não atendeu"
    if row["amostras"] < 100 or row["p95_ms"] is None:
        return "Medição inconclusiva"
    return "Atendeu nas condições testadas" if row["p95_ms"] <= 2000 else "Não atendeu"


def format_ms(value):
    return "—" if value is None else f"{value:.2f}".replace(".", ",")


def main(out):
    manifest = out / "manifesto.json"
    print("## Q-07 — Teste de carga e tempo de resposta\n")
    if manifest.is_file():
        info = json.loads(manifest.read_text(encoding="utf-8"))
        print(f"Commit `{info['commit']}`. Código de saída do protocolo: {info.get('codigo', 'pendente')}.\n")
    print("| Operação | Usuários virtuais | Amostras | p50 (ms) | p95 (ms) | Máximo (ms) | Falhas de requisição/validação | Meta p95 | Resultado |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for vus in (5, 10):
        path = out / f"resultados-medicao-{vus}-vus.json"
        if not path.is_file():
            print(f"| Rodada sem relatório | {vus} | — | — | — | — | — | ≤ 2.000 ms | Medição inconclusiva |")
            continue
        for row in json.loads(path.read_text(encoding="utf-8"))["resultados"]:
            stats = " | ".join(format_ms(row[key]) for key in ("p50_ms", "p95_ms", "max_ms"))
            print(f"| {OPERACOES[row['operacao']]} | {vus} | {row['amostras']} | {stats} | "
                  f"{row['falhas']} | ≤ 2.000 ms | {outcome(row)} |")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
