import sys
import os
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
sys.path = [path] + [p for p in sys.path if not p == path]
sys.stdout = sys.stderr
import gluon.main
application = gluon.main.wsgibase