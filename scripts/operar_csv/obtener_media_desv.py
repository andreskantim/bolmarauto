import csv
import statistics
import sys
import os

def leer_csv_y_calcular_estadisticas(nombre_archivo):
    """
    Lee un archivo CSV y calcula la media y desviación típica de cada columna
    """
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            lector = csv.reader(archivo)
            
            # Leer todas las filas
            filas = list(lector)
            
            if not filas:
                print("El archivo está vacío.")
                return
            
            # Detectar si hay encabezados
            primera_fila = filas[0]
            encabezados = []
            datos_inicio = 0
            
            # Intentar convertir la primera fila a números
            valores_numericos = []
            for valor in primera_fila:
                if valor.strip():
                    try:
                        valores_numericos.append(float(valor))
                    except ValueError:
                        valores_numericos.append(None)
            
            # Si hay valores no numéricos, probablemente son encabezados
            if None in valores_numericos:
                encabezados = primera_fila
                datos_inicio = 1
                print(f"Encabezados detectados: {encabezados}")
            else:
                # Crear encabezados automáticos
                encabezados = [f"Columna {i+1}" for i in range(len(primera_fila))]
                datos_inicio = 0
                print("No se detectaron encabezados. Usando nombres automáticos.")
            
            print("-" * 60)
            
            # Determinar el número de columnas
            num_columnas = len(encabezados)
            
            # Inicializar listas para cada columna
            columnas_datos = [[] for _ in range(num_columnas)]
            
            # Procesar cada fila de datos
            for i, fila in enumerate(filas[datos_inicio:], datos_inicio + 1):
                for j, valor in enumerate(fila):
                    if j < num_columnas and valor.strip():  # Solo procesar valores no vacíos
                        try:
                            columnas_datos[j].append(float(valor))
                        except ValueError:
                            # Ignorar valores no numéricos silenciosamente
                            pass
            
            # Columnas a omitir (en minúsculas para comparación)
            columnas_omitir = {'valid time', 'emision_time', 'valid_time', 'dwi', 'mdts'}
            
            # Calcular estadísticas para cada columna
            print("\nRESULTADOS POR COLUMNA:")
            print("=" * 60)
            
            # Encabezado de la tabla
            print(f"{'Columna':<25} {'Media':<15} {'Desv. Típica':<15}")
            print("-" * 60)
            
            resultados = []
            for i, datos in enumerate(columnas_datos):
                nombre_columna = encabezados[i] if i < len(encabezados) else f"Columna {i+1}"
                
                # Verificar si la columna debe ser omitida
                if nombre_columna.lower() in columnas_omitir:
                    continue
                
                if datos:  # Si hay datos numéricos
                    media = statistics.mean(datos)
                    
                    # Calcular desviación típica (necesita al menos 2 valores)
                    if len(datos) > 1:
                        desviacion = statistics.stdev(datos)
                    else:
                        desviacion = 0.0
                    
                    resultados.append({
                        'columna': nombre_columna,
                        'media': media,
                        'desviacion': desviacion
                    })
                    
                    print(f"{nombre_columna:<25} {media:<15.4f} {desviacion:<15.4f}")
                else:
                    print(f"{nombre_columna:<25} {'N/A':<15} {'N/A':<15}")
            
            print("-" * 60)
            
            # Resumen
            if resultados:
                print(f"\nTotal de columnas procesadas: {len(resultados)}")
            else:
                print("\nNo se encontraron datos numéricos válidos en ninguna columna.")
                
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{nombre_archivo}'")
        print("Asegúrate de que el archivo existe y la ruta es correcta.")
    except Exception as e:
        print(f"Error inesperado: {e}")

def main():
    print("CALCULADORA DE MEDIA Y DESVIACIÓN TÍPICA POR COLUMNAS - CSV")
    print("=" * 60)
    
    # Aquí puedes especificar directamente el path al archivo CSV
    # Cambia esta línea por el path completo a tu archivo
    path_archivo = "../../datasets/boletines/FQXX41MM/cantabria.csv"  # Ejemplo: "/ruta/completa/a/tu/archivo.csv"
    
    # Verificar si se proporcionó el nombre del archivo como argumento (opcional)
    if len(sys.argv) > 1:
        path_archivo = sys.argv[1]
        print(f"Usando archivo desde argumento: {path_archivo}")
    else:
        print(f"Usando archivo por defecto: {path_archivo}")
        print("(Puedes cambiar el path en la función main() o pasar como argumento)")
    
    print()
    
    # Verificar que el archivo existe
    if not os.path.exists(path_archivo):
        print(f"El archivo '{path_archivo}' no existe.")
        print("Verifica que el path sea correcto y que el archivo exista.")
        return
    
    # Procesar el archivo
    leer_csv_y_calcular_estadisticas(path_archivo)

if __name__ == "__main__":
    main()
        