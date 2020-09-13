from uuid import uuid4

from flask import Flask
from flask import jsonify
from flask import request

from main import Blockchain

app = Flask(__name__)

# gera um edereco global para esse no
node_identifier = str(uuid4()).replace('-', '')

# inicia a blockchain
blockchain = Blockchain()

@app.route("/")
def hello():
    return "Bem vindo ao S4Coin"

@app.route('/mine', methods=['GET'])
def mine():
    # executa o algoritmo da prova de trabalho para obter a proxima
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    # recompensa por achar a prova
    # sender=0 para mostrar que o bloco foi minerado
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    # cria um novo bloco para adicionar a cadeia
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message': "Novo bloco adicionado",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Nossa cadeia foi substituída',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Rede autorizada',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Erro: insira uma lista válida", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Novos nós foram adicionados',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # verifica se os campos exigidos estao nos dados postados
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return "Missing Values", 400

    # cria uma nova transacao
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transação será adicionada ao Bloco {index}'}
    return jsonify(response), 201


if __name__ == '__main__':
    app.run()
