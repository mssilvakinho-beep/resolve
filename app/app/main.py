from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import APP_VERSION
from app.api.routes import router

app=FastAPI(title='RESOLVE 2.0 CORE',version=APP_VERSION,description='Núcleo operacional: casos, memória estrutural, financeiro e relatórios.')
app.include_router(router)

@app.get('/', include_in_schema=False)
def panel():
    return FileResponse(Path(__file__).parent / 'web' / 'index.html', media_type='text/html')
