"""Disponibiliza o perfil ADMINISTRADOR para a US-32."""
from alembic import op

revision = "f032ad660001"
down_revision = "c4e8a1927f30"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        INSERT INTO perfis (codigo, nome, descricao)
        VALUES ('ADMINISTRADOR', 'Administrador', 'Gerencia usuários e seus perfis de acesso.')
        ON CONFLICT (codigo) DO NOTHING
    """)


def downgrade():
    op.execute("DELETE FROM perfis WHERE codigo = 'ADMINISTRADOR'")
