from bottle import run, request, post

@post('/')
def index():
    print(request.body)
    #postdata = request.body.read()
    #print (postdata) #this goes to log file only, not to client
    #if request.forms.get("password") == "08c0cb57e165842a808294a6a6dbe26b":
        
    #    return "Recived!"
    return "Recived!"

run(host='localhost', port=8080, debug=True)