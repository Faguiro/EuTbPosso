from app import create_app, db, cli
from app.models import User, Post

app = create_app()
cli.register(app)

def start_ngrok():
    from pyngrok import ngrok

    url = ngrok.connect(8080)
    print(' * Tunnel URL:', url)

if app.config['START_NGROK']:
    start_ngrok()

    
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


