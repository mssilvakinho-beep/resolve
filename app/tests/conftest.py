import os, tempfile
DB=os.path.join(tempfile.gettempdir(),'resolve_2_0_suite.sqlite3')
os.environ['RESOLVE_DB']=DB
try: os.remove(DB)
except FileNotFoundError: pass
