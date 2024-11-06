import subprocess
import sys

def git_commit_push(commit_message):
    try:
        # Añadir todos los cambios, incluidos los eliminados
        subprocess.run(["git", "add", "-A"], check=True)
        
        # Hacer el commit con el mensaje especificado
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Hacer push al repositorio remoto en la rama actual
        subprocess.run(["git", "push"], check=True)
        
        print("Cambios añadidos, commit realizado y repositorio remoto actualizado.")
    except subprocess.CalledProcessError as e:
        print(f"Ocurrió un error al ejecutar Git: {e}")

if __name__ == "__main__":
    # Verificar que se ha proporcionado un mensaje de commit
    if len(sys.argv) < 2:
        print("Uso: python git_commit_push.py 'mensaje del commit'")
    else:
        # Obtener el mensaje de commit del argumento
        commit_message = sys.argv[1]
        git_commit_push(commit_message)