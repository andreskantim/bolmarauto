import pandas as pd

def filtrar_csv(archivo_entrada, archivo_salida, columna, valor_a_eliminar):
    """
    Elimina filas de un CSV donde una columna específica coincide con un valor dado.
    
    Parámetros:
    - archivo_entrada (str): Ruta del archivo CSV de entrada
    - archivo_salida (str): Ruta del archivo CSV de salida
    - columna (str): Nombre de la columna a evaluar
    - valor_a_eliminar: Valor que se quiere eliminar (puede ser str, int, float, etc.)
    
    Retorna:
    - dict: Información sobre el procesamiento (filas originales, eliminadas, restantes)
    """
    try:
        # Leer el CSV
        df = pd.read_csv(archivo_entrada)
        filas_originales = len(df)
        
        # Verificar que la columna existe
        if columna not in df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el archivo CSV")
        
        # Filtrar las filas (mantener las que NO coinciden con el valor)
        df_filtrado = df[df[columna] != valor_a_eliminar]
        filas_restantes = len(df_filtrado)
        filas_eliminadas = filas_originales - filas_restantes
        
        # Exportar el CSV filtrado
        df_filtrado.to_csv(archivo_salida, index=False)
        
        # Retornar información del procesamiento
        return {
            'filas_originales': filas_originales,
            'filas_eliminadas': filas_eliminadas,
            'filas_restantes': filas_restantes,
            'archivo_salida': archivo_salida
        }
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_entrada}")
        return None
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Eliminar filas donde la columna 'estado' sea 'inactivo'
    resultado = filtrar_csv(
        archivo_entrada='svr_lin.csv',
        archivo_salida='svr_lin_filtrado.csv',
        columna='regressor',
        valor_a_eliminar='SDG'
    )
    
    if resultado:
        print(f"Procesamiento completado:")
        print(f"- Filas originales: {resultado['filas_originales']}")
        print(f"- Filas eliminadas: {resultado['filas_eliminadas']}")
        print(f"- Filas restantes: {resultado['filas_restantes']}")
        print(f"- Archivo guardado: {resultado['archivo_salida']}")
    
    # Ejemplo 2: Eliminar filas donde la columna 'edad' sea 0
    resultado2 = filtrar_csv(
        archivo_entrada='usuarios.csv',
        archivo_salida='usuarios_validos.csv',
        columna='edad',
        valor_a_eliminar=0
    )
    
    # Ejemplo 3: Eliminar múltiples valores (versión extendida)
    def filtrar_csv_multiples_valores(archivo_entrada, archivo_salida, columna, valores_a_eliminar):
        """
        Versión extendida que permite eliminar múltiples valores
        """
        try:
            df = pd.read_csv(archivo_entrada)
            filas_originales = len(df)
            
            if columna not in df.columns:
                raise ValueError(f"La columna '{columna}' no existe en el archivo CSV")
            
            # Filtrar múltiples valores
            df_filtrado = df[~df[columna].isin(valores_a_eliminar)]
            filas_restantes = len(df_filtrado)
            filas_eliminadas = filas_originales - filas_restantes
            
            df_filtrado.to_csv(archivo_salida, index=False)
            
            return {
                'filas_originales': filas_originales,
                'filas_eliminadas': filas_eliminadas,
                'filas_restantes': filas_restantes,
                'archivo_salida': archivo_salida
            }
            
        except Exception as e:
            print(f"Error al procesar el archivo: {str(e)}")
            return None
    
    # Ejemplo de uso con múltiples valores
    resultado3 = filtrar_csv_multiples_valores(
        archivo_entrada='productos.csv',
        archivo_salida='productos_activos.csv',
        columna='estado',
        valores_a_eliminar=['descontinuado', 'agotado', 'pendiente']
    )