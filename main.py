import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Configurazione della connessione al database
DB_CONFIG = {
    "dbname": "libreria",
    "user": "admin",
    "password": "Luigi.2010", # <-- ASSICURATI CHE SIA LA TUA PASSWORD
    "host": "localhost",
    "port": "5432"
}

# Modello per i dati in ingresso
class Libro(BaseModel):
    titolo: str
    autore: str
    anno: int

@app.get("/")
def read_root():
    return {"messaggio": "Benvenuto nella tua API con database!"}

@app.get("/libri")
def get_libri():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, titolo, autore, anno FROM libri;")
    righe = cur.fetchall()
    cur.close()
    conn.close()
    
    libri = []
    for riga in righe:
        libri.append({
            "id": riga[0],
            "titolo": riga[1],
            "autore": riga[2],
            "anno": riga[3]
        })
    return libri

@app.post("/libri")
def aggiungi_libro(libro: Libro):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO libri (titolo, autore, anno) VALUES (%s, %s, %s) RETURNING id;",
        (libro.titolo, libro.autore, libro.anno)
    )
    
    nuovo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return {"id": nuovo_id, "messaggio": "Libro aggiunto con successo!"}
from fastapi import HTTPException

@app.put("/libri/{id_libro}")
def modifica_libro(id_libro: int, libro: Libro):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Esegui l'UPDATE
    cur.execute(
        "UPDATE libri SET titolo = %s, autore = %s, anno = %s WHERE id = %s;",
        (libro.titolo, libro.autore, libro.anno, id_libro)
    )
    
    # Se nessuna riga è stata modificata, il libro non esiste
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Libro non trovato")
        
    conn.commit()
    cur.close()
    conn.close()
    
    return {"messaggio": f"Libro {id_libro} modificato con successo!"}
@app.delete("/libri/{id_libro}")
def elimina_libro(id_libro: int):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Esegui il DELETE
    cur.execute("DELETE FROM libri WHERE id = %s;", (id_libro,))
    
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Libro non trovato")
        
    conn.commit()
    cur.close()
    conn.close()
    
    return {"messaggio": f"Libro {id_libro} eliminato con successo!"}