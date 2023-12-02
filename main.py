from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Crea la base de datos
conn = sqlite3.connect("contactos.db")
c = conn.cursor()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


                              
class Contacto(BaseModel):
    email : str
    nombre : str
    telefono : str



# Rutas para las operaciones CRUD

@app.get('/')
def root():
    return {"HOLA MUNDO"}

@app.post("/contactos")
async def crear_contacto(contacto: Contacto):
    """Crea un nuevo contacto."""
    # TODO Inserta el contacto en la base de datos y responde con un mensaje
    c = conn.cursor()
    c.execute('INSERT INTO contactos (email, nombre, telefono) VALUES (?, ?, ?)',
              (contacto.email, contacto.nombre, contacto.telefono))
    conn.commit()
    return contacto

@app.get("/contactos")
async def obtener_contactos():
    """Obtiene todos los contactos."""
    # TODO Consulta todos los contactos de la base de datos y los envia en un JSON
    c = conn.cursor()
    c.execute('SELECT * FROM contactos')
    response = []
    for row in c:
        contacto = {"email":row[0], "nombre":row[1], "telefono":row[2]}
        response.append(contacto)
    return response

@app.get("/contactos/{email}")
async def obtener_contacto(email: str):
    """Obtiene un contacto por su email."""
    # Consulta el contacto por su email
    c = conn.cursor()
    c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
    row = c.fetchone()
    if row:
        contacto = {"email": row[0], "nombre": row[1], "telefono": row[2]}
        return JSONResponse(content=contacto)
    else:
        return JSONResponse(content={}, status_code=404)

from fastapi import HTTPException

@app.put("/contactos/{email}")
async def actualizar_contacto(email: str, contacto: Contacto):
    """Actualiza un contacto."""
    try:
        c = conn.cursor()
        c.execute('UPDATE contactos SET nombre = ?, telefono = ? WHERE email = ?',
                  (contacto.nombre, contacto.telefono, email))
        conn.commit()

        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")
        
        return contacto
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.delete("/contactos/{email}")
async def eliminar_contacto(email: str):
    """Elimina un contacto."""
    # TODO Elimina el contacto de la base de datos
    c = conn.cursor()
    c.execute('DELETE FROM contactos WHERE email = ?', (email,))
    conn.commit()
    return {"elemento borrado"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


