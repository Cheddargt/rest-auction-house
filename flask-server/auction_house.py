from flask import Flask, request, jsonify
import time
import threading
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Members API Route
@app.route('/members')
def get_members():
    return {'members': ['Member1', 'Member2', 'Member3']}

class Bid(object):
    def __init__(self, itemName, itemCode, clientName, price):
        self.itemName = itemName
        self.itemCode = itemCode
        self.clientName = clientName
        self.price = price

    def getItemName(self):
        return self.itemName
    
    def getItemCode(self):
        return self.itemCode
    
    def getClientName(self):
        return self.clientName
    
    def getPrice(self):
        return self.price
    
    # pra printar o objeto
    def __str__(self):
        return f"Bidder: {self.name}\nBids: {self.bids}"

class Auction(object):
    def __init__(self, clientName, code, name, description, initialPrice, endTime):
        self.clientName = clientName
        self.code = code
        self.name = name
        self.description = description
        self.initialPrice = initialPrice
        self.endTime = endTime
        self.currentBid = initialPrice
        self.currentBidder = ''
        self.bids = []

    def newBid(self, price, clientName):
        self.currentBid = price
        self.bids.append(Bid(self.name, self.code, clientName, price))
        self.currentBidder = clientName
        
    def getCode(self):
        return self.code

    def getName(self):
        return self.name
    
    def getClientName(self):
        return self.clientName

    def getInitialPrice(self):
        return self.initialPrice
    
    def getCurrentBid(self):
        return self.currentBid
    
    def getCurrentBidder(self):
        return self.currentBidder
    
    def getBids(self):
        return self.bids
    
    def getAuctionJson(self):
        return {
            "code": self.code,
            "name": self.name,
            "currentBid": self.currentBid,
            "remainingTime": self.endTime,
        }

class Cliente(object):
    def __init__(self, name):
        self.name = name
        self.bids = []
        
    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name 
    
    def addBid(self, auctionName, auctionCode, price):
        
        newBid = {
            "code": auctionCode,
            "name": auctionName,
            "price": price,
        }

        self.bids.append(newBid)

    def getBids(self):
        print(self.bids)
        return self.bids


auctions = []

client_list = []

def add_bid(clientName, auctionCode, price):

    # get auctionName
    for auction in auctions:    
        if auction.getCode() == auctionCode:
            auctionName = auction.getName()

    for client in client_list:
        if client.getName() == clientName:
            client.addBid(auctionName, auctionCode, price)
    
    print (client_list)

@app.route('/create_auction', methods=['POST'])
def create_auction():
    data = request.get_json()
    clientName = data['clientName']
    code = data['code']
    name = data['auctionName']
    description = data['description']
    initialPrice = data['initialPrice']
    endTime = data['endTime']

    auction = Auction(clientName, code, name, description, initialPrice, endTime)
    auctions.append(auction)
    return jsonify(success=True), 200

@app.route('/bid_auction', methods=['POST'])
def bid_auction():
    data = request.get_json()
    clientName = data['clientName']
    auctionCode = data['auctionCode']
    price = data['price']

    for auction in auctions:
        if auction.getCode() == auctionCode:
            if clientName != auction.getClientName():
                if price > auction.getCurrentBid():
                    auction.newBid(price, clientName)
                    add_bid(clientName, auctionCode, price)
                    return jsonify(success=True, res_code=200, message='Bid placed sucessfully!'), 200
                else:
                    return jsonify(success=False, res_code=500, message='Bid lower than current bid'), 200
            else:
                return jsonify(success=False, res_code=510, message='You cannot bid on your own auction'), 200
    return jsonify(success=False, res_code=400, message='Auction not found'), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    nomeCliente = data['nomeCliente']

    for client in client_list:
        if client.getName() == nomeCliente:
            return jsonify(success=False, res_code=500, message='Client already registered, please login'), 200

    client_list.append(Cliente(nomeCliente))
    return jsonify(success=True), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nomeCliente = data['nomeCliente']

    for client in client_list:
        if client.name == nomeCliente:
            return jsonify(success=True), 200
    return jsonify(success=False, res_code=500, message='Client not found'), 200

@app.route('/bids', methods=['POST'])
def get_bids():
    data = request.get_json()
    nomeCliente = data['nomeCliente']

    for client in client_list:
        if client.getName() == nomeCliente:
            clientBids = client.getBids()
            if clientBids == []:
                return jsonify(bids=None), 200
            return jsonify(bids=clientBids), 200

    return jsonify(bids=None), 200


@app.route('/auctions', methods=['GET'])
def show_auctions():
    auction_list = []
    if not auctions:
        return jsonify(auction_list), 200
    else:
        for auction in auctions:
            auction_list.append(auction.getAuctionJson())
        return jsonify(auction_list), 200


def count_upwards():
    t = 1
    while t:
        # TODO: verificar se precisa disso
        for i in range(len(auctions)-1, -1, -1):
            endTime = int(auctions[i].endTime)
            if endTime == 0:
                auctions.pop(i)
                print("An auction has finished!")
        for auction in auctions:
            endTime = int(auction.endTime)
            endTime -= 1
            auction.endTime = str(endTime)
        time.sleep(1)


if __name__ == "__main__":
    threading.Thread(target=count_upwards).start()
    app.run(debug=True)