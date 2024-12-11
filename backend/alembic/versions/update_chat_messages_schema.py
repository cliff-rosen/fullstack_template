"""update chat messages schema

Revision ID: update_chat_messages_schema
Revises: your_previous_revision
Create Date: 2024-03-24 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'update_chat_messages_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing chat_messages table if it exists
    op.execute('DROP TABLE IF EXISTS chat_messages')
    
    # Create new chat_messages table with correct structure
    op.create_table('chat_messages',
        sa.Column('message_id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.Enum('user', 'assistant', 'system', name='message_type'), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('message_id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_chat_messages_thread_id',
        'chat_messages', 'chat_threads',
        ['thread_id'], ['thread_id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_chat_messages_user_id',
        'chat_messages', 'users',
        ['user_id'], ['user_id'],
        ondelete='CASCADE'
    )
    
    # Create indexes
    op.create_index('ix_chat_messages_message_id', 'chat_messages', ['message_id'])
    op.create_index('ix_chat_messages_thread_id', 'chat_messages', ['thread_id'])
    op.create_index('ix_chat_messages_user_id', 'chat_messages', ['user_id'])

def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_chat_messages_thread_id', 'chat_messages', type_='foreignkey')
    op.drop_constraint('fk_chat_messages_user_id', 'chat_messages', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('ix_chat_messages_message_id', table_name='chat_messages')
    op.drop_index('ix_chat_messages_thread_id', table_name='chat_messages')
    op.drop_index('ix_chat_messages_user_id', table_name='chat_messages')
    
    # Drop table
    op.drop_table('chat_messages')
    
    # Drop enum type
    op.execute('DROP TYPE message_type') 