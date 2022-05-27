from sanic import Sanic, json
from sanic.response import text

from chargingInBupt.auth import authorized, generate_token, authorized_admin
from chargingInBupt.orm import User, session


app = Sanic("Charging_in_BUPT")


@app.post('/login')
async def login(request):
    print(request)
    if request.json:
        username = request.json.get('username')
        password = request.json.get('password')
        if username == '' or password == '':
            return text('Invalid username or password', status=400)
        user = session.query(User).filter(User.username == username).first()
        if user is None:
            return text('Invalid username or password', status=400)
        if user.password != password:
            return text('Invalid username or password', status=400)
        token = generate_token(user.id, username)
        return json({'token': token})
    else:
        return text('No json', status=400)


@app.post('/register')
async def register(request):
    username = request.json.get('username')
    password = request.json.get('password')
    if username == '' or password == '':
        return text('Invalid username or password', status=400)
    user = session.query(User).filter(User.username == username).first()
    if user is not None:
        return text('Username already exists', status=400)
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return json({'status': 'success', 'token': generate_token(user.id, username)})


@app.get("/")
@authorized()
async def hello_world(request):
    return text("Hello, world.")

@app.get("/admin")
@authorized_admin()
async def hello_world(request):
    return text("Hello, admin.")