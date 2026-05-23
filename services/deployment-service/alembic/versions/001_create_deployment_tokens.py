"""create deployment_tokens"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "deployment_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.Enum("model", "app", name="resourcetype"), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resource_name", sa.String(200), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("access_count", sa.BigInteger(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_deployment_tokens_token", "deployment_tokens", ["token"], unique=True)
    op.create_index("ix_deployment_tokens_owner_user_id", "deployment_tokens", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index("ix_deployment_tokens_owner_user_id", table_name="deployment_tokens")
    op.drop_index("ix_deployment_tokens_token", table_name="deployment_tokens")
    op.drop_table("deployment_tokens")
    op.execute("DROP TYPE IF EXISTS resourcetype")
