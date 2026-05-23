"""create app_packages"""

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
        "app_packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("platform", sa.Enum("maixcam", "k210", "esp32", "generic", name="appplatform"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("source_url", sa.String(512), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default="false"),
        sa.Column("install_count", sa.BigInteger(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_app_packages_owner_user_id", "app_packages", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index("ix_app_packages_owner_user_id", table_name="app_packages")
    op.drop_table("app_packages")
    op.execute("DROP TYPE IF EXISTS appplatform")
