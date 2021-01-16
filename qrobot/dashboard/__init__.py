from .frontend import app as _app

def run_dashboard():
    _app.run_server(debug=False)