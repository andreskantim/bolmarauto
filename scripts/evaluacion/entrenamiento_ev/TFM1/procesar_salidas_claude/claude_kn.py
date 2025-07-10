import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler
from itertools import product
import re
import ast
import os
import glob
from pathlib import Path


def parse_param_dict(param_str):
    """
    Parsea el diccionario de parámetros desde el string del archivo
    """
    try:
        # Limpiar el string y convertir a formato evaluable
        clean_str = param_str.strip()
        
        # Crear un mapeo más cuidadoso de objetos
        # Primero, reemplazar los objetos sklearn con representaciones evaluables
        clean_str = clean_str.replace('KNeighborsRegressor()', '"KNeighborsRegressor"')
        clean_str = clean_str.replace('PCA(n_components=0.95)', '"PCA_n_components_0.95"')
        clean_str = clean_str.replace('StandardScaler()', '"StandardScaler"')
        clean_str = clean_str.replace('RobustScaler()', '"RobustScaler"')
        
        # Evaluar el diccionario
        param_dict = eval(clean_str)
        
        # Convertir de vuelta los valores especiales
        for key, values in param_dict.items():
            new_values = []
            for value in values:
                if value == "KNeighborsRegressor":
                    new_values.append("KNeighborsRegressor")
                elif value == "PCA_n_components_0.95":
                    new_values.append("PCA(n_components=0.95)")
                elif value == "StandardScaler":
                    new_values.append("StandardScaler")
                elif value == "RobustScaler":
                    new_values.append("RobustScaler")
                elif value is None:
                    new_values.append(None)
                else:
                    new_values.append(value)
            param_dict[key] = new_values
        
        return param_dict
        
    except Exception as e:
        print(f"Error parseando parámetros: {e}")
        print(f"String original: {param_str}")
        return None

def parse_knn_results_file(file_path):
    """
    Lee el archivo de resultados y extrae la información de cada variable
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Buscar todas las variables y sus datos
    variables = []
    
    # Patrón más preciso para capturar el diccionario completo
    pattern = r'(\w+)\s+\[\s*\{\s*([^}]+)\s*\}\s*\]\s+\[([-\d\.\s]+)\]\s+\[([-\d\.\s]+)\]\s+\[([\d\s]+)\]'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        indices_str = match[4]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict(param_dict_str)
        
        # Parsear los scores y stds
        scores = [float(x) for x in scores_str.split()]
        stds = [float(x) for x in stds_str.split()]
        indices = [int(x) for x in indices_str.split()]
        
        # Diagnóstico: verificar que las longitudes coincidan
        print(f"Variable {var_name}:")
        print(f"  - Scores: {len(scores)} valores")
        print(f"  - Stds: {len(stds)} valores")
        print(f"  - Indices: {len(indices)} valores")
        print(f"  - Primeros 5 scores: {scores[:5]}")
        print(f"  - Primeros 5 indices: {indices[:5]}")
        
        if param_dict:
            total_combinations = 1
            for key, values in param_dict.items():
                total_combinations *= len(values)
            print(f"  - Combinaciones esperadas: {total_combinations}")
            
            if len(scores) != len(stds) or len(scores) != len(indices):
                print(f"  - ADVERTENCIA: Las longitudes no coinciden!")
        
        variables.append({
            'name': var_name,
            'param_dict': param_dict,
            'scores': scores,
            'stds': stds,
            'indices': indices
        })
    
    return variables

def generate_param_combinations_from_dict(param_dict):
    """
    Genera todas las combinaciones posibles de parámetros desde un diccionario
    IMPORTANTE: Debe generar las combinaciones en el MISMO ORDEN que sklearn GridSearchCV
    """
    if param_dict is None:
        return [], {}
    
    # Generar todas las combinaciones usando el mismo orden que sklearn
    keys = list(param_dict.keys())
    values = list(param_dict.values())
    
    combinations = []
    for combination in product(*values):
        param_combination = dict(zip(keys, combination))
        combinations.append(param_combination)
    
    return combinations, param_dict

def format_param_value(value):
    """
    Formatea los valores de parámetros para mostrar en el DataFrame
    """
    if value is None:
        return None
    else:
        return value

def create_results_dataframe(variables_data, source_file=None):
    """
    Crea un DataFrame con todas las combinaciones y resultados
    CORREGIDO: Mapeo directo secuencial entre scores y combinaciones
    """
    all_results = []
    
    for var_data in variables_data:
        var_name = var_data['name']
        param_dict = var_data['param_dict']
        scores = var_data['scores']
        stds = var_data['stds']
        indices = var_data['indices']
        
        if param_dict is None:
            print(f"Saltando variable {var_name} por error en parámetros")
            continue
            
        # Generar combinaciones específicas para esta variable
        combinations, _ = generate_param_combinations_from_dict(param_dict)
        
        print(f"\nProcesando variable {var_name}:")
        print(f"  - Combinaciones generadas: {len(combinations)}")
        print(f"  - Scores disponibles: {len(scores)}")
        print(f"  - Indices disponibles: {len(indices)}")
        
        # CORRECCIÓN PRINCIPAL: Los scores están en el orden correcto
        # Solo necesitamos mapear directamente por posición
        print(f"  - Verificando orden de scores:")
        print(f"    Primeros 5 scores del archivo: {scores[:5]}")
        
        # Verificar que tenemos la misma cantidad de combinaciones que scores
        if len(combinations) != len(scores):
            print(f"  - ADVERTENCIA: Número de combinaciones ({len(combinations)}) != número de scores ({len(scores)})")
            # Usar el mínimo para evitar errores
            max_items = min(len(combinations), len(scores))
        else:
            max_items = len(combinations)
            print(f"  - ✓ Número de combinaciones coincide con número de scores")
        
        # Mapear directamente por posición
        for i in range(max_items):
            row = {'variable': var_name}
            
            # Agregar parámetros de la combinación i
            combo = combinations[i]
            for param_name, param_value in combo.items():
                row[param_name] = format_param_value(param_value)
            
            # Asignar score y std por posición directa
            row['score'] = scores[i]
            row['std'] = stds[i]
            
            all_results.append(row)
            
            # Mostrar los primeros ejemplos para verificar
            if i < 5:
                print(f"    Combinación {i}: {combo} -> score: {scores[i]}")
        
        print(f"  - ✓ {max_items} filas procesadas para {var_name}")
    
    return pd.DataFrame(all_results)

def find_common_filename_part(file_paths):
    """
    Encuentra la parte común de los nombres de archivo hasta la primera diferencia
    """
    if not file_paths:
        return "combined_results"
    
    # Obtener solo los nombres de archivo sin la ruta y sin extensión
    filenames = [os.path.splitext(os.path.basename(path))[0] for path in file_paths]
    
    if len(filenames) == 1:
        # Si hay solo un archivo, usar su nombre completo
        return filenames[0]
    
    # Encontrar la parte común hasta la primera diferencia
    # Tomar el primer archivo como referencia
    common_part = ""
    min_length = min(len(filename) for filename in filenames)
    
    for i in range(min_length):
        # Verificar si todos los archivos tienen el mismo caracter en la posición i
        chars_at_i = [filename[i] for filename in filenames]
        if len(set(chars_at_i)) == 1:  # Todos los caracteres son iguales
            common_part += chars_at_i[0]
        else:
            break
    
    # Limpiar caracteres no deseados al final
    common_part = common_part.rstrip('_-. ')
    
    # Si no hay parte común significativa, usar un nombre genérico
    if len(common_part) < 3:
        return "combined_results"
    
    return common_part

def find_knn_files(directory_path, pattern="*.txt"):
    """
    Encuentra todos los archivos que coinciden con el patrón en el directorio
    """
    if not os.path.exists(directory_path):
        print(f"El directorio {directory_path} no existe")
        return []
    
    # Buscar archivos con el patrón especificado
    search_pattern = os.path.join(directory_path, pattern)
    files = glob.glob(search_pattern)
    
    # Filtrar solo archivos KNN si es necesario
    knn_files = [f for f in files if 'KN' in os.path.basename(f)]
    
    return knn_files

def debug_file_structure(file_path):
    """
    Función de diagnóstico para examinar la estructura del archivo
    """
    print(f"\n=== DIAGNÓSTICO DE ARCHIVO: {os.path.basename(file_path)} ===")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Mostrar una muestra del contenido
    print("Primeras 500 caracteres del archivo:")
    print(content[:500])
    print("...")
    
    # Buscar patrones
    pattern = r'(\w+)\s+\[\s*\{\s*([^}]+)\s*\}\s*\]\s+\[([-\d\.\s]+)\]\s+\[([-\d\.\s]+)\]\s+\[([\d\s]+)\]'
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"\nPatrones encontrados: {len(matches)}")
    
    for i, match in enumerate(matches[:2]):  # Solo mostrar los primeros 2
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        indices_str = match[4]
        
        print(f"\nVariable {i+1}: {var_name}")
        print(f"Parámetros: {param_dict_str}")
        print(f"Scores: {scores_str}")
        print(f"Stds: {stds_str}")
        print(f"Indices: {indices_str}")
        
        # Contar elementos
        scores = scores_str.split()
        stds = stds_str.split()
        indices = indices_str.split()
        
        print(f"Número de scores: {len(scores)}")
        print(f"Número de stds: {len(stds)}")
        print(f"Número de indices: {len(indices)}")
        
        # Mostrar los primeros valores para verificar
        print(f"Primeros 5 scores: {scores[:5]}")
        print(f"Primeros 5 stds: {stds[:5]}")
        print(f"Primeros 5 indices: {indices[:5]}")
        
        # Verificar el orden de los scores
        print(f"Scores esperados (según tu ejemplo): -0.64587882, -0.65090997, -0.66128526...")
        print(f"Scores encontrados: {', '.join(scores[:6])}")

def process_multiple_knn_files(directory_path, output_path=None, file_pattern="*.txt", debug=False):
    """
    Procesa múltiples archivos KNN y los combina en un solo CSV
    """
    try:
        # Encontrar todos los archivos KNN en el directorio
        print(f"Buscando archivos en: {directory_path}")
        knn_files = find_knn_files(directory_path, file_pattern)
        
        if not knn_files:
            print("No se encontraron archivos KNN en el directorio")
            return None
        
        print(f"Encontrados {len(knn_files)} archivos:")
        for file in knn_files:
            print(f"  - {os.path.basename(file)}")
        
        # Diagnóstico opcional
        if debug:
            for file_path in knn_files[:1]:  # Solo el primer archivo para diagnóstico
                debug_file_structure(file_path)
        
        # Procesar cada archivo
        all_dataframes = []
        
        for file_path in knn_files:
            print(f"\nProcesando: {os.path.basename(file_path)}")
            
            try:
                # Leer y parsear el archivo
                variables_data = parse_knn_results_file(file_path)
                print(f"  Encontradas {len(variables_data)} variables")
                
                # Crear DataFrame con resultados
                df = create_results_dataframe(variables_data)
                
                if df is not None and not df.empty:
                    all_dataframes.append(df)
                    print(f"  DataFrame creado con {len(df)} filas")
                    
                    # Verificar valores faltantes en este DataFrame
                    na_count = df['score'].isna().sum()
                    if na_count > 0:
                        print(f"  - ADVERTENCIA: {na_count} valores faltantes en este archivo")
                    else:
                        print(f"  - ✓ Sin valores faltantes en este archivo")
                        
                    # Mostrar los primeros scores para verificar
                    print(f"  - Primeros 5 scores generados: {df['score'].head().tolist()}")
                else:
                    print(f"  Error: DataFrame vacío para {file_path}")
                    
            except Exception as e:
                print(f"  Error procesando {file_path}: {e}")
                continue
        
        if not all_dataframes:
            print("No se pudieron procesar archivos exitosamente")
            return None
        
        # Combinar todos los DataFrames
        print(f"\nCombinando {len(all_dataframes)} DataFrames...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Verificar valores None en score y std
        none_scores = combined_df['score'].isna().sum()
        none_stds = combined_df['std'].isna().sum()
        
        print(f"\nVerificación de valores faltantes:")
        print(f"  - Scores faltantes (None/NaN): {none_scores}")
        print(f"  - Stds faltantes (None/NaN): {none_stds}")
        
        if none_scores > 0 or none_stds > 0:
            print(f"  - Porcentaje de datos faltantes: {(none_scores/len(combined_df))*100:.2f}%")
        else:
            print(f"  - ✓ ¡Sin valores faltantes! Todos los datos se procesaron correctamente")
        
        # Si hay valores faltantes, eliminar esas filas
        if none_scores > 0:
            print(f"\nEliminando {none_scores} filas con valores faltantes...")
            combined_df = combined_df.dropna(subset=['score', 'std'])
            print(f"DataFrame final con {len(combined_df)} filas")
        
        # Mostrar información del DataFrame combinado
        print(f"\nDataFrame combinado creado con {len(combined_df)} filas y {len(combined_df.columns)} columnas")
        print(f"Variables procesadas: {combined_df['variable'].unique()}")
        print(f"Columnas: {list(combined_df.columns)}")
        
        # Verificar los primeros valores del DataFrame combinado
        print(f"\nPrimeras 5 filas del DataFrame (solo scores):")
        print(combined_df[['variable', 'score']].head())
        
        # Generar nombre de archivo de salida si no se especifica
        if output_path is None:
            # Encontrar la parte común de los nombres de archivo
            common_name = find_common_filename_part(knn_files)
            output_path = f"{common_name}.csv"
            print(f"Nombre de archivo generado: {output_path}")
        
        # Eliminar la columna source_file si existe
        if 'source_file' in combined_df.columns:
            combined_df = combined_df.drop('source_file', axis=1)
        
        # Ordenar el DataFrame: primero por variable en orden específico, luego por n_neighbors
        print("Ordenando resultados...")
        
        # Definir el orden específico de las variables
        variable_order = ['dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 'shww_max', 'shww_med', 'mdts_sin', 'mdts_cos', 'shts_max', 'shts_med']
        
        # Crear un mapeo de orden para las variables
        variable_order_map = {var: i for i, var in enumerate(variable_order)}
        
        # Añadir columna auxiliar para el orden
        combined_df['variable_order'] = combined_df['variable'].map(variable_order_map)
        
        # Buscar la columna de n_neighbors (puede tener diferentes nombres)
        neighbors_column = None
        for col in combined_df.columns:
            if 'n_neighbors' in col.lower():
                neighbors_column = col
                break
        
        if neighbors_column:
            # Convertir n_neighbors a numérico para ordenar correctamente
            combined_df[neighbors_column] = pd.to_numeric(combined_df[neighbors_column], errors='coerce')
            combined_df = combined_df.sort_values(['variable_order', neighbors_column])
        else:
            combined_df = combined_df.sort_values(['variable_order'])
        
        # Eliminar la columna auxiliar de orden
        combined_df = combined_df.drop('variable_order', axis=1)
        
        # Reemplazar valores None con "None" para mejor visualización en CSV
        df_export = combined_df.copy()
        df_export = df_export.fillna("None")
        
        # Guardar CSV
        df_export.to_csv(output_path, index=False)
        print(f"\nArchivo combinado guardado en: {output_path}")
        
        # Estadísticas por archivo
        print("\nEstadísticas por número de archivos procesados:")
        total_files = len(knn_files)
        print(f"Total de archivos procesados: {total_files}")
        
        # Mostrar estadísticas por variable
        print("\nEstadísticas por variable:")
        var_stats = combined_df.groupby('variable').agg({
            'score': ['count', 'mean', 'std'],
            'std': ['mean']
        }).round(4)
        print(var_stats)
        
        # Mostrar muestra de datos
        print("\nPrimeras 10 filas del DataFrame combinado:")
        print(combined_df.head(10))
        
        return combined_df
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None

def analyze_neighbors_parameter(combined_df):
    """
    Analiza específicamente los valores de n_neighbors (adaptable a diferentes nombres de columna)
    """
    # Buscar la columna de n_neighbors
    neighbors_column = None
    for col in combined_df.columns:
        if 'n_neighbors' in col.lower():
            neighbors_column = col
            break
    
    if neighbors_column:
        print(f"\nAnálisis de {neighbors_column}:")
        neighbors_analysis = combined_df.groupby(neighbors_column).agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(neighbors_analysis)
        
        # Resumen por valor de n_neighbors
        print(f"\nResumen por valor de {neighbors_column}:")
        neighbors_summary = combined_df.groupby(neighbors_column).agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(neighbors_summary)
    else:
        print("No se encontró ninguna columna con 'n_neighbors'")

# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la ruta real del directorio
    directory_path = "../../../sk_learn/kn/guardados/"
    
    # Procesar todos los archivos con diagnóstico habilitado
    combined_df = process_multiple_knn_files(directory_path, debug=True)
    
    if combined_df is not None:
        print("\n¡Procesamiento completado exitosamente!")
        
        # Análisis específico de n_neighbors
        analyze_neighbors_parameter(combined_df)
        
        # Mostrar mejores resultados por variable
        print("\nMejores resultados por variable:")
        best_results = combined_df.loc[combined_df.groupby('variable')['score'].idxmax()]
        # Mostrar todas las columnas disponibles
        print(best_results)