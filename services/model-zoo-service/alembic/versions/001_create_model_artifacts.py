"""create model_artifacts

Revision ID: 001
"""

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
        "model_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("platform", sa.Enum("maixcam", "k210", "esp32", "stm32", "generic", name="platform"), nullable=False),
        sa.Column("task_type", sa.Enum("classification", "detection", "segmentation", "other", name="tasktype"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default="false"),
        sa.Column("download_count", sa.BigInteger(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_model_artifacts_owner_user_id", "model_artifacts", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index("ix_model_artifacts_owner_user_id", table_name="model_artifacts")
    op.drop_table("model_artifacts")
    op.execute("DROP TYPE IF EXISTS platform")
    op.execute("DROP TYPE IF EXISTS tasktype")
