import hashlib
import json
from time import time
import requests
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set() # usado para manter a lista de nós

        # criacao do primeiro bloco
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        """
        Inclui um novo no na lista
        :param address: endereco do no. Ex. 'http://192.168.0.3:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # aceita um endereco fora do padrao '192.168.0.3:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Endereço inválido')

    def valid_chain(self, chain):
        """
        Valida a blockchain

        :param chain: <list> Blockchain
        :return: <bool> Verdadeiro se válido, caso não, Falso
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n--------\n")
            # verifica se o hash do bloco esta correto
            if block['previous_hash'] != self.hash(last_block):
                return False

            # verifica a prova de trabalho
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Faz a substituição da blockchain mais curta
        pela mais longa na rede.

        :return: <bool> caso verdadeiro, a blackchain foi substituida
        """

        neighbours = self.nodes
        new_chain = None

        # busca uma corrent mais longa que a atual
        max_length = len(self.chain)

        # verifica as blockchains de todos os nós na rede
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # verifica o tamanho da blockchain e se ela e valida
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # subsitui a blockchain pela mais longa
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash=None):
        """
        cria um novo bloclo

        :param proof: <int> prova de trabalho
        :param previous_hash: (Optional) <str> hash do bloco anterior
        :return: <dict> novo bloco
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # reseta a atual lista de transacoes
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        cria uma nova transação para ir para o próximo bloco
        :param sender: <str> endereco do remetente
        :param recipient: <str> endereco de destino
        :param amount: <int> quantidade
        :return: <int> indice do bloco responsavel pela transacao
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        cria o hash do bloco e ordena os hashes para que nao haja inconsistencia
        :param block: <dict> Bloco
        :return: <str>

        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # obtem o ultimo bloco da blockchain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        funcao de prova de trabalho:
        - encontra um numero x, onde o hash(xx') possui 4 zeros a esquerda'
        - x e a prova anterior e x' e a nova

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova de trabalho, certificando que existem 4 zeros anteriores

        :param last_proof: <int> Prova Anterior
        :param proof: <int> Prova Atual
        :return: <bool> True se estiver correto, caso não False
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

