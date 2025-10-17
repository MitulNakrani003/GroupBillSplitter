import sys
from streamlit.web import cli as stcli
from core.logic import resource_path

if __name__ == '__main__':
    # Point to the app.py file within the bundled package
    app_path = resource_path('app.py')
    # Add the --server.headless=true flag
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false", "--server.headless=true"]
    sys.exit(stcli.main())