from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBearer, HTTPBasicCredentials, HTTPAuthorizationCredentials, OAuth2PasswordBearer
import sqlite3
import secrets
import hashlib

app = FastAPI()

# Configuración CORS
origins = [
    "https://contactos-frontend-6d58a4eb9f51.herokuapp.com",
    "https://contactos-backen-b4d88f351253.herokuapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos
class Contacto(BaseModel):
    email: str
    nombre: str
    telefono: str

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Funciones de utilidad
def generate_token():
    return secrets.token_urlsafe(32)

def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# Función para obtener la conexión en cada solicitud
def get_db():
    db = sqlite3.connect("contactos.db")
    try:
        yield db
    finally:
        db.close()

security_basic = HTTPBasic()
security_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/registro")
def register(credentials: HTTPBasicCredentials = Depends(security_basic)):
    username = credentials.username
    password = credentials.password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Verificar si el usuario ya existe
    with sqlite3.connect("contactos.db") as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM usuarios WHERE username = ?", (username,))
        existing_user = c.fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="El usuario ya existe")

        c.execute(
            'INSERT INTO usuarios (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        conn.commit()

    return {"status": "Usuario registrado con éxito"}


@app.get("/root")
def root(credentials: HTTPAuthorizationCredentials = Depends(security_bearer), conn: sqlite3.Connection = Depends(get_db)):
    usuario_token = credentials.credentials

    with conn:
        c = conn.cursor()
        c.execute("SELECT token FROM usuarios WHERE token = ?", (usuario_token,))
        result = c.fetchone()

    if result and usuario_token == result[0]:
        return {"message": "TOKEN válido"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN no válido")


@app.post("/token")
def login(credentials: HTTPBasicCredentials = Depends(security_basic), conn: sqlite3.Connection = Depends(get_db)):
    # Verifica qué tipo de credenciales estás utilizando
    if isinstance(credentials, HTTPBasicCredentials):
        # Si estás utilizando HTTPBasicCredentials, puedes acceder a 'username' y 'password'
        username = credentials.username
        password = credentials.password

        # Realiza la lógica necesaria con el username y password (por ejemplo, autenticación)
        hashed_password = hash_password(password)

        with conn:
            c = conn.cursor()
            c.execute("SELECT token FROM usuarios WHERE username = ? AND password = ?", (username, hashed_password))
            result = c.fetchone()

    elif isinstance(credentials, HTTPBearer):
        # Si estás utilizando HTTPBearer, puedes acceder al token con 'credentials.credentials'
        # Realiza la lógica necesaria con el token
        token = credentials.credentials

        # Puedes validar el token o realizar otras operaciones según tus necesidades

    else:
        # Manejo de otro tipo de credenciales si es necesario
        raise HTTPException(status_code=400, detail="Tipo de credenciales no admitido")

    if result:
        token = result[0]
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Tu usuario o contraseña son incorrectas verifica por favor")
    


        
# Función de dependencia para obtener el usuario actual
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_bearer), conn: sqlite3.Connection = Depends(get_db)):
    username_token = credentials.credentials

    with conn:
        c = conn.cursor()
        c.execute("SELECT token FROM usuarios WHERE token = ?", (username_token,))
        result = c.fetchone()

    if result and username_token == result[0]:
        return username_token
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida")

# Rutas para las operaciones CRUD

@app.get('/')
def root():
    return {"bienvenido a mi api!"}

@app.post("/contactos")
def crear_contacto(contacto: Contacto, current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Crea un nuevo contacto."""
    # Inserta el contacto en la base de datos y responde con un mensaje
    with conn:
        c = conn.cursor()
        c.execute('INSERT INTO contactos (email, nombre, telefono) VALUES (?, ?, ?)',
                  (contacto.email, contacto.nombre, contacto.telefono))
        conn.commit()
    return contacto

@app.post("/logout")
def logout(current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    # Aquí puedes realizar cualquier acción necesaria para cerrar la sesión
    # Por ejemplo, podrías invalidar el token actual o realizar otras acciones según tu implementación
    return {"message": "Sesión cerrada exitosamente"}
    

@app.get("/contactos")
def obtener_contactos(current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Obtiene todos los contactos."""
    # Consulta todos los contactos de la base de datos y los envía en un JSON
    with conn:
        c = conn.cursor()
        c.execute('SELECT * FROM contactos')
        response = [{"email": row[0], "nombre": row[1], "telefono": row[2]} for row in c.fetchall()]
    return response

@app.get("/contactos/{email}")
def obtener_contacto(email: str, current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Obtiene un contacto por su email."""
    # Consulta el contacto por su email
    with conn:
        c = conn.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        row = c.fetchone()
    if row:
        contacto = {"email": row[0], "nombre": row[1], "telefono": row[2]}
        return JSONResponse(content=contacto)
    else:
        return JSONResponse(content={}, status_code=404)

@app.put("/contactos/{email}")
def actualizar_contacto(email: str, contacto: Contacto, current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Actualiza un contacto."""
    try:
        with conn:
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
def eliminar_contacto(email: str, current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Elimina un contacto."""
    # Elimina el contacto de la base de datos
    with conn:
        c = conn.cursor()
        c.execute('DELETE FROM contactos WHERE email = ?', (email,))
        conn.commit()
    return {"elemento borrado"}




@app.post("/logout")
def logout(current_user: str = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    # Aquí puedes realizar cualquier acción necesaria para cerrar la sesión
    # Por ejemplo, podrías invalidar el token actual o realizar otras acciones según tu implementación
    return {"message": "Sesión cerrada exitosamente"}



