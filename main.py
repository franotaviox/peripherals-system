from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
import random
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

engine = create_engine('sqlite:///loja_perifericos.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

pedido_produto = Table(
    'pedido_produto', Base.metadata,
    Column('pedido_id', Integer, ForeignKey('pedidos.id')),
    Column('produto_id', Integer, ForeignKey('produtos.id'))
)

class Produto(Base):
    __tablename__ = 'produtos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    categoria = Column(String)
    marca = Column(String)
    preco = Column(Float)
    estoque = Column(Integer)
    
    def __repr__(self):
        return f'<Produto(nome={self.nome}, categoria={self.categoria}, preco={self.preco}, estoque={self.estoque})>'

class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    telefone = Column(String)
    endereco = Column(String)
    
    def __repr__(self):
        return f'<Cliente(nome={self.nome}, email={self.email}, endereco={self.endereco})>'

class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    valor_total = Column(Float, default=0)
    status = Column(String, default="Pendente")
    
    cliente = relationship("Cliente", backref='pedidos')
    produtos = relationship("Produto", secondary=pedido_produto, backref='pedidos')
    
    def __repr__(self):
        return f'<Pedido(cliente={self.cliente.nome}, valor_total={self.valor_total}, status={self.status}, id={self.id:04})>'

Base.metadata.create_all(engine)

# Função para adicionar um produto
def adicionar_produto(id, nome, categoria, marca, preco, estoque):
    produto = Produto(id=id, nome=nome, categoria=categoria, marca=marca, preco=preco, estoque=estoque)
    session.add(produto)
    session.commit()
    print("Produto adicionado com sucesso!")

# Função para adicionar um cliente
def adicionar_cliente(id, nome, email, telefone, endereco):
    cliente = Cliente(id=id, nome=nome, email=email, telefone=telefone, endereco=endereco)
    session.add(cliente)
    session.commit()
    print("Cliente adicionado com sucesso!")

def realizar_pedido(cliente_id, produtos_quantidades):
    cliente = session.query(Cliente).get(cliente_id)
    if not cliente:
        print("Cliente não encontrado.")
        return
    
    pedido = Pedido(cliente=cliente)
    valor_total = 0
    
    for produto_id, quantidade in produtos_quantidades.items():
        produto = session.query(Produto).get(produto_id)
        if not produto:
            print(f"Produto com ID {produto_id} não encontrado.")
            continue
        if produto.estoque < quantidade:
            print(f"Produto '{produto.nome}' indisponível na quantidade solicitada.")
            continue
        valor_total += produto.preco * quantidade
        produto.estoque -= quantidade
        pedido.produtos.append(produto) 

    pedido.valor_total = valor_total
    session.add(pedido)
    session.commit()
    print(f"Pedido realizado com sucesso! ID do pedido: {pedido.id:04}, Valor total: R${valor_total:.2f}")

def consultar_produtos():
    produtos = session.query(Produto).all()
    for produto in produtos:
        print(produto)

def consultar_clientes():
    clientes = session.query(Cliente).all()
    for cliente in clientes:
        print(cliente)

def consultar_pedidos():
    pedidos = session.query(Pedido).all()
    for pedido in pedidos:
        print(pedido)
        for produto in pedido.produtos:
            print(f'- {produto.nome} ({produto.categoria}) - R${produto.preco}')

def main():
    while True:
        print('\n=== Loja de Periféricos ===')
        print('1. Adicionar Produto')
        print('2. Consultar Produtos')
        print('3. Adicionar Cliente')
        print('4. Realizar Pedido')
        print('5. Consultar Clientes')
        print('6. Consultar Pedidos')
        print('7. Sair')
        
        opcao = input('Escolha uma opção: ')
        
        if opcao == '1':
            id = input('ID do Produto: ')
            nome = input('Nome do Produto: ')
            categoria = input('Categoria: ')
            marca = input('Marca: ')
            preco = float(input('Preço: '))
            estoque = int(input('Quantidade em Estoque: '))
            adicionar_produto(id, nome, categoria, marca, preco, estoque)
        
        elif opcao == '2':
            consultar_produtos()
        
        elif opcao == '3':
            id = input('ID do Cliente: ')
            nome = input('Nome do Cliente: ')
            email = input('Email: ')
            telefone = input('Telefone: ')
            endereco = input('Endereço: ')
            adicionar_cliente(id, nome, email, telefone, endereco)
        
        elif opcao == '4':
            cliente_id = int(input('ID do Cliente: '))
            produtos_quantidades = {}
            while True:
                produto_id = int(input('ID do Produto (0 para finalizar): '))
                if produto_id == 0:
                    break
                quantidade = int(input('Quantidade: '))
                produtos_quantidades[produto_id] = quantidade
            realizar_pedido(cliente_id, produtos_quantidades)
        
        elif opcao == '5':
            consultar_clientes()
        
        elif opcao == '6':
            consultar_pedidos()
        
        elif opcao == '7':
            break
        else:
            print('Opção inválida. Tente novamente.')

if __name__ == "__main__":
    main()

