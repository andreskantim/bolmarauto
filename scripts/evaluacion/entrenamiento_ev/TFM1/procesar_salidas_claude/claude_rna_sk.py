import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from itertools import product
import re
import ast
import os
import glob
from pathlib import Path


def parse_param_dict_mlp(param_str):
    """
    Parsea el diccionario de parámetros desde el string del archivo para MLPRegressor
    """
    try:
        # Limpiar el string y convertir a formato evaluable
        clean_str = param_str.strip()
        
        # Reemplazar objetos complejos con representaciones evaluables
        clean_str = clean_str.replace('StandardScaler()', '"StandardScaler"')
        clean_str = clean_str.replace('RobustScaler()', '"RobustScaler"')
        clean_str = clean_str.replace('None', 'None')
        
        # Evaluar el diccionario
        param_dict = eval(clean_str)
        
        # Convertir de vuelta los valores especiales
        for key, values in param_dict.items():
            new_values = []
            for value in values:
                if value == "StandardScaler":
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

def parse_mlp_results_file(file_path):
    """
    Lee el archivo de resultados de MLPRegressor y extrae la información de cada variable
    MANTIENE EL ORDEN ORIGINAL DEL ARCHIVO
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Buscar todas las variables y sus datos
    variables = []
    
    # Patrón actualizado para MLPRegressor: variable_name \n [param_dict] \n [scores] \n [stds]
    pattern = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict_mlp(param_dict_str)
        
        # Parsear los scores y stds
        scores = [float(x) for x in scores_str.split()]
        stds = [float(x) for x in stds_str.split()]
        indices = list(range(len(scores)))  # Indices secuenciales
        
        # Diagnóstico: verificar que las longitudes coincidan
        print(f"Variable {var_name}:")
        print(f"  - Scores: {len(scores)} valores")
        print(f"  - Stds: {len(stds)} valores")
        print(f"  - Primeros 5 scores: {scores[:5]}")
        print(f"  - Primeros 5 stds: {stds[:5]}")
        
        if param_dict:
            total_combinations = 1
            for key, values in param_dict.items():
                total_combinations *= len(values)
            print(f"  - Combinaciones esperadas: {total_combinations}")
            
            if len(scores) != total_combinations:
                print(f"  - ADVERTENCIA: Scores ({len(scores)}) != combinaciones esperadas ({total_combinations})")
            
            if len(scores) != len(stds):
                print(f"  - ADVERTENCIA: Scores ({len(scores)}) != Stds ({len(stds)})")
        
        variables.append({
            'name': var_name,
            'param_dict': param_dict,
            'scores': scores,
            'stds': stds,
            'indices': indices
        })
    
    return variables

def generate_mlp_param_combinations(param_dict):
    """
    Genera todas las combinaciones posibles de parámetros para MLPRegressor
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

def format_mlp_param_value(value):
    """
    Formatea los valores de parámetros de MLPRegressor para mostrar en el DataFrame
    """
    if value is None:
        return None
    elif isinstance(value, tuple):
        return str(value)
    else:
        return value

def create_mlp_results_dataframe(variables_data, file_order=0, source_file=None):
    """
    Crea un DataFrame con todas las combinaciones y resultados de MLPRegressor
    MANTIENE EL ORDEN ORIGINAL - añade índices para preservar el orden
    """
    all_results = []
    variable_order = 0  # Orden de las variables dentro del archivo
    
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
        combinations, _ = generate_mlp_param_combinations(param_dict)
        
        print(f"\nProcesando variable {var_name}:")
        print(f"  - Combinaciones generadas: {len(combinations)}")
        print(f"  - Scores disponibles: {len(scores)}")
        
        # Verificar el orden de los scores
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
        
        # Mapear directamente por posición - MANTENER ORDEN ORIGINAL
        for i in range(max_items):
            row = {
                'variable': var_name,
                'file_order': file_order,  # Orden del archivo
                'variable_order': variable_order,  # Orden de la variable dentro del archivo
                'combination_order': i,  # Orden de la combinación dentro de la variable
                'global_order': file_order * 10000 + variable_order * 1000 + i  # Orden global único
            }
            
            # Agregar parámetros de la combinación i
            combo = combinations[i]
            for param_name, param_value in combo.items():
                row[param_name] = format_mlp_param_value(param_value)
            
            # Asignar score y std por posición directa
            row['score'] = scores[i]
            row['std'] = stds[i]
            
            all_results.append(row)
            
            # Mostrar los primeros ejemplos para verificar
            if i < 5:
                print(f"    Combinación {i}: {combo} -> score: {scores[i]}")
        
        print(f"  - ✓ {max_items} filas procesadas para {var_name}")
        variable_order += 1  # Incrementar el orden de la variable
    
    return pd.DataFrame(all_results)

def find_mlp_files(directory_path, pattern="*.txt"):
    """
    Encuentra todos los archivos de MLPRegressor que coinciden con el patrón en el directorio
    MANTIENE EL ORDEN ORIGINAL DE LOS ARCHIVOS
    """
    if not os.path.exists(directory_path):
        print(f"El directorio {directory_path} no existe")
        return []
    
    # Buscar archivos con el patrón especificado
    search_pattern = os.path.join(directory_path, pattern)
    files = glob.glob(search_pattern)
    
    # MANTENER EL ORDEN ORIGINAL - ordenar por nombre de archivo
    files = sorted(files)
    
    return files

def debug_mlp_file_structure(file_path):
    """
    Función de diagnóstico para examinar la estructura del archivo de MLPRegressor
    """
    print(f"\n=== DIAGNÓSTICO DE ARCHIVO MLP: {os.path.basename(file_path)} ===")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Mostrar una muestra del contenido
    print("Primeras 1000 caracteres del archivo:")
    print(content[:1000])
    print("...")
    
    # Buscar patrones específicos de MLPRegressor
    pattern = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]'
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"\nPatrones encontrados: {len(matches)}")
    
    for i, match in enumerate(matches[:2]):  # Solo mostrar los primeros 2
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        
        print(f"\nVariable {i+1}: {var_name}")
        print(f"Parámetros: {param_dict_str}")
        print(f"Scores: {scores_str}")
        print(f"Stds: {stds_str}")
        
        # Contar elementos
        scores = scores_str.split()
        stds = stds_str.split()
        
        print(f"Número de scores: {len(scores)}")
        print(f"Número de stds: {len(stds)}")
        
        # Mostrar los primeros valores para verificar
        print(f"Primeros 10 scores: {scores[:10]}")
        print(f"Primeros 10 stds: {stds[:10]}")

def process_multiple_mlp_files(directory_path, output_path=None, file_pattern="*.txt", debug=False):
    """
    Procesa múltiples archivos de MLPRegressor y los combina en un solo CSV
    MANTIENE EL ORDEN ORIGINAL DE LOS ARCHIVOS Y DATOS
    """
    try:
        # Encontrar todos los archivos de MLPRegressor en el directorio
        print(f"Buscando archivos de MLPRegressor en: {directory_path}")
        mlp_files = find_mlp_files(directory_path, file_pattern)
        
        if not mlp_files:
            print("No se encontraron archivos de MLPRegressor en el directorio")
            return None
        
        print(f"Encontrados {len(mlp_files)} archivos:")
        for i, file in enumerate(mlp_files):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        # Diagnóstico opcional
        if debug:
            for file_path in mlp_files[:1]:  # Solo el primer archivo para diagnóstico
                debug_mlp_file_structure(file_path)
        
        # Procesar cada archivo MANTENIENDO EL ORDEN
        all_dataframes = []
        
        for file_order, file_path in enumerate(mlp_files):
            print(f"\nProcesando archivo {file_order + 1}/{len(mlp_files)}: {os.path.basename(file_path)}")
            
            try:
                # Leer y parsear el archivo
                variables_data = parse_mlp_results_file(file_path)
                print(f"  Encontradas {len(variables_data)} variables")
                
                # Crear DataFrame con resultados - PASAR EL ORDEN DEL ARCHIVO
                df = create_mlp_results_dataframe(variables_data, file_order=file_order, source_file=file_path)
                
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
        
        # Combinar todos los DataFrames MANTENIENDO EL ORDEN ORIGINAL
        print(f"\nCombinando {len(all_dataframes)} DataFrames...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # ORDENAR POR EL ORDEN ESPECÍFICO DE VARIABLES Y LUEGO POR ORDEN ORIGINAL
        print("Ordenando datos: usando orden específico de variables y manteniendo orden original dentro de cada variable...")
        
        # Definir el orden específico de las variables
        variable_order = ['dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 'shww_max', 'shww_med', 'mdts_sin', 'mdts_cos', 'shts_max', 'shts_med']
        
        # Crear un mapeo de orden para las variables
        variable_order_map = {var: i for i, var in enumerate(variable_order)}
        
        # Añadir columna auxiliar para el orden específico de variables
        combined_df['variable_sort_order'] = combined_df['variable'].map(variable_order_map)
        
        # Manejar variables que no están en el orden predefinido (las pone al final)
        combined_df['variable_sort_order'] = combined_df['variable_sort_order'].fillna(999)
        
        # Ordenar por: orden específico de variables, luego por orden original dentro de cada variable
        combined_df = combined_df.sort_values(['variable_sort_order', 'global_order'])
        
        # Eliminar las columnas auxiliares de orden antes de guardar
        columns_to_remove = ['file_order', 'variable_order', 'combination_order', 'global_order', 'variable_sort_order']
        df_for_export = combined_df.drop(columns=columns_to_remove, errors='ignore')
        
        # Verificar valores None en score y std
        none_scores = df_for_export['score'].isna().sum()
        none_stds = df_for_export['std'].isna().sum()
        
        print(f"\nVerificación de valores faltantes:")
        print(f"  - Scores faltantes (None/NaN): {none_scores}")
        print(f"  - Stds faltantes (None/NaN): {none_stds}")
        
        if none_scores > 0 or none_stds > 0:
            print(f"  - Porcentaje de datos faltantes: {(none_scores/len(df_for_export))*100:.2f}%")
        else:
            print(f"  - ✓ ¡Sin valores faltantes! Todos los datos se procesaron correctamente")
        
        # Si hay valores faltantes, eliminar esas filas
        if none_scores > 0:
            print(f"\nEliminando {none_scores} filas con valores faltantes...")
            df_for_export = df_for_export.dropna(subset=['score'])
            print(f"DataFrame final con {len(df_for_export)} filas")
        
        # Mostrar información del DataFrame combinado
        print(f"\nDataFrame combinado creado con {len(df_for_export)} filas y {len(df_for_export.columns)} columnas")
        print(f"Variables procesadas: {df_for_export['variable'].unique()}")
        print(f"Columnas: {list(df_for_export.columns)}")
        
        # Verificar los primeros valores del DataFrame combinado
        print(f"\nPrimeras 5 filas del DataFrame (solo variable y score):")
        print(df_for_export[['variable', 'score']].head())
        
        # Generar nombre de archivo de salida si no se especifica
        if output_path is None:
            output_path = "mlp_regressor_results_grouped_by_variable.csv"
            print(f"Nombre de archivo generado: {output_path}")
        
        # Reemplazar valores None con "None" para mejor visualización en CSV
        df_export = df_for_export.copy()
        df_export = df_export.fillna("None")
        
        # Guardar CSV - MANTIENE EL ORDEN ORIGINAL
        df_export.to_csv(output_path, index=False)
        print(f"\nArchivo combinado guardado en: {output_path}")
        print("✓ Los datos están ordenados según el orden específico de variables: dwi_sin, dwi_cos, wind_max, wind_med, shww_max, shww_med, mdts_sin, mdts_cos, shts_max, shts_med")
        
        # Mostrar estadísticas por variable
        print("\nEstadísticas por variable:")
        var_stats = df_for_export.groupby('variable').agg({
            'score': ['count', 'mean', 'std'],
            'std': ['mean']
        }).round(4)
        print(var_stats)
        
        # Mostrar muestra de datos
        print("\nPrimeras 10 filas del DataFrame combinado:")
        print(df_for_export.head(10))
        
        return df_for_export
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None

def analyze_mlp_parameters(combined_df):
    """
    Analiza específicamente los parámetros de MLPRegressor
    """
    print("\n=== ANÁLISIS DE PARÁMETROS DE MLPREGRESSOR ===")
    
    # Analizar función de activación
    if 'regressor__activation' in combined_df.columns:
        print("\nAnálisis por función de activación:")
        activation_analysis = combined_df.groupby('regressor__activation').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(activation_analysis)
    
    # Analizar learning rate
    if 'regressor__learning_rate_init' in combined_df.columns:
        print("\nAnálisis por learning rate inicial:")
        lr_analysis = combined_df.groupby('regressor__learning_rate_init').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(lr_analysis)
    
    # Analizar alpha (regularización)
    if 'regressor__alpha' in combined_df.columns:
        print("\nAnálisis por alpha (regularización):")
        alpha_analysis = combined_df.groupby('regressor__alpha').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(alpha_analysis)
    
    # Analizar batch size
    if 'regressor__batch_size' in combined_df.columns:
        print("\nAnálisis por batch size:")
        batch_analysis = combined_df.groupby('regressor__batch_size').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(batch_analysis)
    
    # Analizar solver
    if 'regressor__solver' in combined_df.columns:
        print("\nAnálisis por solver:")
        solver_analysis = combined_df.groupby('regressor__solver').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(solver_analysis)
    
    # Analizar hidden layer sizes
    if 'regressor__hidden_layer_sizes' in combined_df.columns:
        print("\nAnálisis por hidden layer sizes:")
        hidden_analysis = combined_df.groupby('regressor__hidden_layer_sizes').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(hidden_analysis)
    
    # Analizar scaler
    if 'scaler' in combined_df.columns:
        print("\nAnálisis por scaler:")
        scaler_analysis = combined_df.groupby('scaler').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(scaler_analysis)

# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la ruta real del directorio
    directory_path = "../../../sk_learn/rna/guardados"  # Directorio actual
    
    # Procesar todos los archivos con diagnóstico habilitado
    combined_df = process_multiple_mlp_files(directory_path, debug=True)
    
    if combined_df is not None:
        print("\n¡Procesamiento completado exitosamente!")
        print("✓ Los datos han sido ordenados según el orden específico de variables y mantienen el orden original dentro de cada variable")
        
        # Análisis específico de parámetros de MLPRegressor
        analyze_mlp_parameters(combined_df)
        
        # Mostrar mejores resultados por variable
        print("\nMejores resultados por variable:")
        best_results = combined_df.loc[combined_df.groupby('variable')['score'].idxmax()]
        print(best_results[['variable', 'score', 'scaler', 'regressor__activation', 'regressor__learning_rate_init', 'regressor__alpha']])
    else:
        print("No se pudieron procesar los archivos. Verifica que existan archivos con el formato correcto en el directorio.")