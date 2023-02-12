"""added analytic table

Revision ID: 162418348d12
Revises: 37b04528e4cf
Create Date: 2023-02-12 02:30:22.243845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '162418348d12'
down_revision = '37b04528e4cf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sales_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product_price', sa.Float(), nullable=False),
    sa.Column('product_category', sa.String(length=64), nullable=True),
    sa.Column('sale_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('shipping_cost', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_product',
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], )
    )
    op.add_column('products', sa.Column('category', sa.String(length=64), nullable=False))
    op.add_column('products', sa.Column('release_date', sa.DateTime(), nullable=False))
    op.drop_column('products', 'stock')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('stock', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('products', 'release_date')
    op.drop_column('products', 'category')
    op.drop_table('order_product')
    op.drop_table('orders')
    op.drop_table('sales_record')
    # ### end Alembic commands ###
