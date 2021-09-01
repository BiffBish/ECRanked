import requests
url = "https://discord.com/api/webhooks/882380147645354055/MzYHqnqatGkoidWApt0jlN5CO7FCKyK-kaDB8epctzKGw-tKRJgNovqpWv9cWdmskspb"
data = {"content":"Test"}
requests.post(url,data= data)