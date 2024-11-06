import subprocess
import sys

def git_commit_push(commit_message):
    try:
        # Añadir todos los cambios, incluidos los eliminados
        subprocess.run(["git", "add", "-A"], check=True)
        
        # Hacer el commit con el mensaje especificado
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Intentar hacer push al repositorio remoto
        push_result = subprocess.run(["git", "push"], check=False)

        # Verificar si el push falló debido a la falta de upstream y solucionarlo
        if push_result.returncode != 0:
            print("La rama actual no tiene upstream. Configurando upstream y volviendo a intentar...")
            # Configurar el upstream automáticamente y hacer el push
            subprocess.run(["git", "push", "--set-upstream", "origin", "main"], check=True)
        
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