#libraries required
import pandas as pd
import coinbase
import time
import yfinance as yf
from coinbase.wallet.client import Client


#Initialization of Quantities
coinbase_API_key = ''
coinbase_API_secret = ''

# Get all account information from the system
client = Client(coinbase_API_key, coinbase_API_secret)
payment_method = client.get_payment_methods()  # Gets all available payment methods
accounts = client.get_accounts()  # get all account info
BTC = yf.Ticker("BTC-USD") #set the crypto to be managed
OperatingAmount=input("How much money can the Bot use in USD?") #input how much money will be used

#Set used functions
def GetBasicInfo ():

    # Get specific information about Wallets and Payment Methods
    NoAccounts = len(accounts.data)
    NofPaymentM = len(payment_method.data)
    WalletID = []
    WalletName = []
    PaymentName = []
    PaymentID = []

    for i in range(NoAccounts):
        WalletID.append(accounts.data[i]["id"])
        WalletName.append(accounts.data[i]["name"])
    dfWallet = pd.DataFrame(list(zip(WalletName, WalletID)), columns=['Name', 'Hash ID'])
    for i in range(NofPaymentM):
        PaymentName.append(payment_method.data[i]["name"])
        PaymentID.append(payment_method.data[i]["id"])
    dfPaymentMethods = pd.DataFrame(list(zip(PaymentName, PaymentID)), columns=['Name', 'Hash ID'])

    print(dfWallet)
    print(dfPaymentMethods)

    PaymentIndex = input("Select the payment method by typing the index which corresponds to it:")
    WalletIndex = input("Select the Cryptocurrency to be bought by typing the index which corresponds to :")

    CurrentPaymentMethod = PaymentID[int(PaymentIndex)]
    CurrentWallet = WalletID[int(WalletIndex)]

    return CurrentWallet,CurrentPaymentMethod
def movingaverageturncheck(dfBTCHistory):
    status=''
    dfBTCHistory['13ema'] = dfBTCHistory['Open'].ewm(span=13).mean()
    dfBTCHistory['26ema'] = dfBTCHistory['Open'].ewm(span=26).mean()

    if (dfBTCHistory['13ema'][31] > dfBTCHistory['26ema'][31] and dfBTCHistory['13ema'][30] < dfBTCHistory['26ema'][30]):
        status='UT'
    elif(dfBTCHistory['13ema'][31] < dfBTCHistory['26ema'][31] and dfBTCHistory['13ema'][30] > dfBTCHistory['26ema'][30]):
        status='DT'
    else:
        status='none'

    return status
def bollingercheck(dfBTCHistory):
    dfBTCHistory['TP'] = (dfBTCHistory['High'] + dfBTCHistory['Low'] + dfBTCHistory['Close']) / 3
    dfBTCHistory['std'] = dfBTCHistory['TP'].rolling(20).std(ddof=0)
    dfBTCHistory['MA-TP'] = dfBTCHistory['TP'].rolling(20).mean()
    dfBTCHistory['BU'] = dfBTCHistory['MA-TP'] + dfBTCHistory['std']
    dfBTCHistory['BL'] = dfBTCHistory['MA-TP'] - dfBTCHistory['std']

    if (dfBTCHistory['Close'][31] < dfBTCHistory['BU'][31] and dfBTCHistory['Close'][31]  > dfBTCHistory['BL'][31]):
        return 'inside'

    else:
        return 'outside'

#Get Wallet and Payment info
WalletInfo= GetBasicInfo()
CurrentWallet=WalletInfo[0]
CurrentPaymentMethod=WalletInfo[1]
print("You are starting a bot trade with the following information:")
print("Your Selected Wallet is:"+str(CurrentWallet))
print("Your Selected Payment Method is:"+str(CurrentPaymentMethod))
UserAgreement= input (" Is everything correct and you still wish to activate the bot? y/n")
if(UserAgreement=='y'):
    print("Program Started Running!")
    stage=0 #Set the first buying stage

    while (stage==0): #Continuosly look for a buy oportunity
          print("Looking for first buy...")
          dfBTCHistory = BTC.history(period='1mo', interval='1d') #Get all the data from the Ticker
          dfBTCHistoryMin = BTC.history(period='30m', interval='1m')
          CurrentPriceBTC= dfBTCHistoryMin['High'][24]
          FCAmount = int(OperatingAmount)/CurrentPriceBTC

          MAC=movingaverageturncheck(dfBTCHistory) #Check both bollinger and ma
          BC=bollingercheck(dfBTCHistory)
          print(MAC)
          print(BC)

          if(MAC=='UT'and BC=='inside'):
                 print("Conditions for first buy matched!")
                 buy = client.buy(CurrentWallet, amount=str(FCAmount), currency="BTC", payment_method=CurrentPaymentMethod)
                 CoinAmount = FCAmount
                 MoneyAmount = 0
                 print("You just bought "+str(CoinAmount)+" bitcoins")
                 stage=1 #change to selling stage
          time.sleep(14400)

    print("Main Buy and Sell Loop Started!")
    while True: #Infinite Loop is set
         while (stage==1): #Continuosly look for a sell oportunity
            print("Looking for a Sell...")


            dfBTCHistory = BTC.history(period='1mo', interval='1d') #Get all the data from the Ticker
            dfBTCHistoryMin = BTC.history(period='30m', interval='1m')
            CurrentPriceBTC= dfBTCHistoryMin['High'][24]


            MAC = movingaverageturncheck(dfBTCHistory)
            BC = bollingercheck(dfBTCHistory)

            if(MAC=='DT'and BC=='inside'):
                 print("Conditions for a sell found!")
                 sell = client.sell(CurrentWallet, amount=str(CoinAmount), currency="BTC")
                 MoneyAmount= CoinAmount*CurrentPriceBTC
                 CoinAmount=0
                 print("You just sold " + str(MoneyAmount) + "USD worth of bitcoins")
                 stage=2 #Go back to buying stage
            time.sleep(14400)


         while(stage==2):
           print("Looking for a Buy...")
           dfBTCHistory = BTC.history(period='1mo', interval='1d') #Get all the data from the Ticker
           dfBTCHistoryMin = BTC.history(period='30m', interval='1m')
           CurrentPriceBTC= dfBTCHistoryMin['High'][24]

           MAC = movingaverageturncheck(dfBTCHistory)  # Check both bollinger and ma
           BC = bollingercheck(dfBTCHistory)

           if (MAC == 'UT' and BC == 'inside'):
                 print("Conditions for a buy found!")
                 CBAmount= MoneyAmount/CurrentPriceBTC
                 buy = client.buy(CurrentWallet, amount=str(CBAmount), currency="BTC",payment_method=CurrentPaymentMethod)
                 CoinAmount = CBAmount
                 MoneyAmount=0
                 print("You just bought " + str(CoinAmount) + " bitcoins")
                 stage = 1
           time.sleep(14400)
else:
    print("The trading bot was not activated")












