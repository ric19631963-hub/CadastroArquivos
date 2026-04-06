import bcrypt
from db import conectar

def validar_login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT senha_hash FROM captura_web.tb_usuario WHERE usuario = %s",
        (usuario,)
    )

    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        senha_hash = resultado[0].encode("utf-8")
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash)

    return False