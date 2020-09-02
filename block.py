import hashlib
import time

class block:
    def __init__(self, index, prevhash, timestamp, data, hash):
        self.index = index
        self.prevhash = prevhash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class blockchain:
    def __init__(self, genesisblock):
        self.__chain = []
        self.__chain.append(genesisblock)

    def getlastblock(self):
        return self.__chain[len(self.__chain) - 1]

    def gennextblock(self, data):
        prevblck = self.getlastblock()
        nextindex = prevblck.index + 1
        nexttimest = int(round(time.time() * 1000))
        nextprevhash = prevblck.hash
        newblck = block(nextindex, nextprevhash, nexttimest, data,
                        calchash(nextindex, nextprevhash, nexttimest, data))
        if self.validateblck(newblck) == True:
            self.__chain.append(newblck)

    def validateblck(self, newblck):
        prevblck = self.getlastblock()
        if prevblck.index + 1 != newblck.index:
            return False
        elif prevblck.hash != newblck.prevhash:
            return False
        return True

def calchash(index, prevhash, timestamp, data):
    return hashlib.sha256((str(index) + prevhash + str(timestamp) + data).encode('utf-8')).hexdigest()

carimbotempo = int(round(time.time() * 1000))
genesisblock = block(0, "", carimbotempo, "Bloco inicial", calchash(0, "", carimbotempo, "Bloco inicial"))
print(genesisblock)
print("Tudo certo até aqui")