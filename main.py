from client import Client
from utils.consts import *

'''
API Key:
a4vDIBnO0dFKZemW8URNMawuyuU0eyRUI3VGh1wekSlNXDOk704iTPdMisSrYEx8
Secret Key:
T0GEN5C8c8U4YKDMNjbjQeE3HLRLTfTugpatoC9a3eTxIRV4C30aqifHKu2fIa68
'''


client = Client(api_key, api_secret)
print(client.ping())
# print(client.get_ticker("BNBBTC"))