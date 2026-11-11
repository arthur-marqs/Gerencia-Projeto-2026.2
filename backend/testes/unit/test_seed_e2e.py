"""A preparação destrutiva do Cypress deve recusar bancos de desenvolvimento."""
import pytest

from scripts import seed_e2e


@pytest.mark.parametrize('url', [
    '', 'URL inválida', 'sqlite:///setupflow_e2e_test',
    'postgresql://user:password@localhost/setupflow_dev',
    'postgresql://user:password@localhost/setupflow_test',
    'postgresql://user:password@localhost/setupflow_e2e_test_copia',
])
def test_fixture_recusa_banco_antes_de_abrir_conexao(monkeypatch, url):
    monkeypatch.setenv('E2E_DATABASE_URL', url)

    def nao_conectar(*args, **kwargs):
        pytest.fail('A validação permitiu abrir uma conexão com banco não autorizado.')

    monkeypatch.setattr(seed_e2e, 'create_engine', nao_conectar)
    with pytest.raises(SystemExit):
        seed_e2e.preparar('normal')
