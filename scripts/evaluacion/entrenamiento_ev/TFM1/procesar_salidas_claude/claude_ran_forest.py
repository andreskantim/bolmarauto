import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor
from itertools import product
import re
import ast
import os
import glob
from pathlib import Path


def parse_param_dict_rf(param_str):
    """
    Parsea el diccionario de parámetros desde el string del archivo para RandomForestRegressor
    """
    try:
        # Limpiar el string y convertir a formato evaluable
        clean_str = param_str.strip()
        
        # Reemplazar objetos complejos con representaciones evaluables
        clean_str = clean_str.replace('StandardScaler()', '"StandardScaler"')
        clean_str = clean_str.replace('RobustScaler()', '"RobustScaler"')
        clean_str = clean_str.replace('RandomForestRegressor()', '"RandomForestRegressor"')
        clean_str = clean_str.replace('None', 'None')
        
        # Evaluar el diccionario
        param_dict = eval(clean_str)
        
        # Convertir de vuelta los valores especiales
        for key, values in param_dict.items():
            if isinstance(values, list):
                new_values = []
                for value in values:
                    if value == "StandardScaler":
                        new_values.append("StandardScaler")
                    elif value == "RobustScaler":
                        new_values.append("RobustScaler")
                    elif value == "RandomForestRegressor":
                        new_values.append("RandomForestRegressor")
                    elif value is None:
                        new_values.append(None)
                    else:
                        new_values.append(value)
                param_dict[key] = new_values
            else:
                # Si no es una lista, convertir a lista
                if values == "StandardScaler":
                    param_dict[key] = ["StandardScaler"]
                elif values == "RobustScaler":
                    param_dict[key] = ["RobustScaler"]
                elif values == "RandomForestRegressor":
                    param_dict[key] = ["RandomForestRegressor"]
                elif values is None:
                    param_dict[key] = [None]
                else:
                    param_dict[key] = [values]
        
        return param_dict
        
    except Exception as e:
        print(f"Error parseando parámetros: {e}")
        print(f"String original: {param_str}")
        return None

def parse_rf_results_file(file_path):
    """
    Lee el archivo de resultados de RandomForestRegressor y extrae la información de cada variable
    MANTIENE EL ORDEN ORIGINAL DEL ARCHIVO
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Buscar todas las variables y sus datos
    variables = []
    
    # Patrón para RandomForest con stds: variable_name \n [param_dict] \n [scores] \n [stds]
    pattern_with_stds = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]'
    matches_with_stds = re.findall(pattern_with_stds, content, re.DOTALL)
    
    # Patrón para RandomForest sin stds: variable_name \n [param_dict] \n [scores]
    pattern_without_stds = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\](?!\s*\[)'
    matches_without_stds = re.findall(pattern_without_stds, content, re.DOTALL)
    
    # Procesar matches con stds
    for match in matches_with_stds:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict_rf(param_dict_str)
        
        # Parsear los scores y stds
        scores = [float(x) for x in scores_str.split()]
        stds = [float(x) for x in stds_str.split()]
        indices = list(range(len(scores)))
        
        print(f"Variable {var_name} (con stds):")
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
    
    # Procesar matches sin stds
    for match in matches_without_stds:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict_rf(param_dict_str)
        
        # Parsear los scores
        scores = [float(x) for x in scores_str.split()]
        stds = [0.0] * len(scores)  # Llenar con ceros si no hay stds
        indices = list(range(len(scores)))
        
        print(f"Variable {var_name} (sin stds):")
        print(f"  - Scores: {len(scores)} valores")
        print(f"  - Primeros 5 scores: {scores[:5]}")
        
        if param_dict:
            total_combinations = 1
            for key, values in param_dict.items():
                total_combinations *= len(values)
            print(f"  - Combinaciones esperadas: {total_combinations}")
            
            if len(scores) != total_combinations:
                print(f"  - ADVERTENCIA: Scores ({len(scores)}) != combinaciones esperadas ({total_combinations})")
        
        variables.append({
            'name': var_name,
            'param_dict': param_dict,
            'scores': scores,
            'stds': stds,
            'indices': indices
        })
    
    return variables

def generate_rf_param_combinations(param_dict):
    """
    Genera todas las combinaciones posibles de parámetros para RandomForestRegressor
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

def format_rf_param_value(value):
    """
    Formatea los valores de parámetros de RandomForestRegressor para mostrar en el DataFrame
    """
    if value is None:
        return None
    elif isinstance(value, tuple):
        return str(value)
    else:
        return value

def create_rf_results_dataframe(variables_data, file_order=0, source_file=None):
    """
    Crea un DataFrame con todas las combinaciones y resultados de RandomForestRegressor
    """
    all_results = []
    variable_order = 0
    
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
        combinations, _ = generate_rf_param_combinations(param_dict)
        
        print(f"\nProcesando variable {var_name}:")
        print(f"  - Combinaciones generadas: {len(combinations)}")
        print(f"  - Scores disponibles: {len(scores)}")
        
        # Verificar que tenemos la misma cantidad de combinaciones que scores
        if len(combinations) != len(scores):
            print(f"  - ADVERTENCIA: Número de combinaciones ({len(combinations)}) != número de scores ({len(scores)})")
            max_items = min(len(combinations), len(scores))
        else:
            max_items = len(combinations)
            print(f"  - ✓ Número de combinaciones coincide con número de scores")
        
        # Mapear directamente por posición
        for i in range(max_items):
            row = {
                'variable': var_name,
                'file_order': file_order,
                'variable_order': variable_order,
                'combination_order': i,
                'global_order': file_order * 10000 + variable_order * 1000 + i
            }
            
            # Agregar parámetros de la combinación i
            combo = combinations[i]
            for param_name, param_value in combo.items():
                row[param_name] = format_rf_param_value(param_value)
            
            # Asignar score y std por posición directa
            row['score'] = scores[i]
            row['std'] = stds[i]
            
            all_results.append(row)
            
            # Mostrar los primeros ejemplos para verificar
            if i < 5:
                print(f"    Combinación {i}: {combo} -> score: {scores[i]}")
        
        print(f"  - ✓ {max_items} filas procesadas para {var_name}")
        variable_order += 1
    
    return pd.DataFrame(all_results)

def find_rf_files(directory_path, pattern="*.txt"):
    """
    Encuentra todos los archivos de RandomForestRegressor que coinciden con el patrón en el directorio
    """
    if not os.path.exists(directory_path):
        print(f"El directorio {directory_path} no existe")
        return []
    
    search_pattern = os.path.join(directory_path, pattern)
    files = glob.glob(search_pattern)
    files = sorted(files)
    
    return files

def debug_rf_file_structure(file_path):
    """
    Función de diagnóstico para examinar la estructura del archivo de RandomForestRegressor
    """
    print(f"\n=== DIAGNÓSTICO DE ARCHIVO RF: {os.path.basename(file_path)} ===")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    print("Primeras 1000 caracteres del archivo:")
    print(content[:1000])
    print("...")
    
    # Buscar patrones con stds
    pattern_with_stds = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]'
    matches_with_stds = re.findall(pattern_with_stds, content, re.DOTALL)
    
    # Buscar patrones sin stds
    pattern_without_stds = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\](?!\s*\[)'
    matches_without_stds = re.findall(pattern_without_stds, content, re.DOTALL)
    
    print(f"\nPatrones encontrados:")
    print(f"  - Con stds: {len(matches_with_stds)}")
    print(f"  - Sin stds: {len(matches_without_stds)}")
    
    # Mostrar ejemplo de cada tipo
    if matches_with_stds:
        print("\nEjemplo con stds:")
        match = matches_with_stds[0]
        print(f"Variable: {match[0]}")
        print(f"Parámetros: {{{match[1]}}}")
        print(f"Scores: {match[2]}")
        print(f"Stds: {match[3]}")
    
    if matches_without_stds:
        print("\nEjemplo sin stds:")
        match = matches_without_stds[0]
        print(f"Variable: {match[0]}")
        print(f"Parámetros: {{{match[1]}}}")
        print(f"Scores: {match[2]}")

def process_multiple_rf_files(directory_path, output_path=None, file_pattern="*.txt", debug=False):
    """
    Procesa múltiples archivos de RandomForestRegressor y los combina en un solo CSV
    Ordenado por variable y luego por n_estimators
    """
    try:
        # Encontrar todos los archivos de RandomForestRegressor en el directorio
        print(f"Buscando archivos de RandomForestRegressor en: {directory_path}")
        rf_files = find_rf_files(directory_path, file_pattern)
        
        if not rf_files:
            print("No se encontraron archivos de RandomForestRegressor en el directorio")
            return None
        
        print(f"Encontrados {len(rf_files)} archivos:")
        for i, file in enumerate(rf_files):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        # Diagnóstico opcional
        if debug:
            for file_path in rf_files[:1]:  # Solo el primer archivo para diagnóstico
                debug_rf_file_structure(file_path)
        
        # Procesar cada archivo
        all_dataframes = []
        
        for file_order, file_path in enumerate(rf_files):
            print(f"\nProcesando archivo {file_order + 1}/{len(rf_files)}: {os.path.basename(file_path)}")
            
            try:
                # Leer y parsear el archivo
                variables_data = parse_rf_results_file(file_path)
                print(f"  Encontradas {len(variables_data)} variables")
                
                # Crear DataFrame con resultados
                df = create_rf_results_dataframe(variables_data, file_order=file_order, source_file=file_path)
                
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
        
        # Identificar la columna de n_estimators (puede tener diferentes nombres)
        n_estimators_col = None
        for col in combined_df.columns:
            if 'n_estimators' in col:
                n_estimators_col = col
                break
        
        # Definir el orden específico de las variables
        variable_order = ['dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 'shww_max', 'shww_med', 'mdts_sin', 'mdts_cos', 'shts_max', 'shts_med']
        
        # Crear una columna auxiliar para el orden de variables
        combined_df['variable_sort_order'] = combined_df['variable'].apply(
            lambda x: variable_order.index(x) if x in variable_order else len(variable_order)
        )
        
        if n_estimators_col:
            print(f"Ordenando por orden específico de variables y luego por {n_estimators_col}...")
            combined_df = combined_df.sort_values(['variable_sort_order', n_estimators_col])
        else:
            print("No se encontró columna n_estimators, ordenando solo por orden específico de variables...")
            combined_df = combined_df.sort_values(['variable_sort_order'])
        
        # Eliminar las columnas auxiliares de orden y las columnas especificadas
        columns_to_remove = ['file_order', 'variable_order', 'combination_order', 'global_order', 'variable_sort_order']
        df_for_export = combined_df.drop(columns=columns_to_remove, errors='ignore')
        
        # Eliminar las columnas específicas solicitadas
        columns_to_exclude = ['is_implicit', 'has_stds']
        df_for_export = df_for_export.drop(columns=columns_to_exclude, errors='ignore')
        
        # Agregar columna 'regressor' con valor constante
        df_for_export['regressor'] = 'RandomForestRegressor'
        
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
        print(f"\nPrimeras 5 filas del DataFrame (variable, score y n_estimators):")
        display_cols = ['variable', 'score']
        if n_estimators_col:
            display_cols.append(n_estimators_col)
        print(df_for_export[display_cols].head())
        
        # Generar nombre de archivo de salida si no se especifica
        if output_path is None:
            output_path = "random_forest_results_sorted.csv"
            print(f"Nombre de archivo generado: {output_path}")
        
        # Reemplazar valores None con "None" para mejor visualización en CSV
        df_export = df_for_export.copy()
        df_export = df_export.fillna("None")
        
        # Guardar CSV
        df_export.to_csv(output_path, index=False)
        print(f"\nArchivo combinado guardado en: {output_path}")
        sort_info = f"por orden específico de variables y {n_estimators_col}" if n_estimators_col else "por orden específico de variables"
        print(f"✓ Los datos están ordenados {sort_info}")
        print("✓ Se han eliminado las columnas: is_implicit, has_stds")
        print("✓ Se ha agregado la columna 'regressor' con valor 'RandomForestRegressor'")
        print(f"✓ Variables ordenadas en el orden: {variable_order}")
        
        # Mostrar estadísticas por variable
        print("\nEstadísticas por variable:")
        var_stats = df_for_export.groupby('variable').agg({
            'score': ['count', 'mean', 'std']
        }).round(4)
        print(var_stats)
        
        # Mostrar muestra de datos
        print("\nPrimeras 10 filas del DataFrame combinado:")
        print(df_for_export.head(10))
        
        return df_for_export
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None

def analyze_rf_parameters(combined_df):
    """
    Analiza específicamente los parámetros de RandomForestRegressor
    """
    print("\n=== ANÁLISIS DE PARÁMETROS DE RANDOMFORESTREGRESSOR ===")
    
    # Analizar n_estimators (con y sin prefijo)
    n_est_cols = [col for col in combined_df.columns if 'n_estimators' in col]
    if n_est_cols:
        print(f"\nAnálisis por n_estimators:")
        for col in n_est_cols:
            print(f"  Columna: {col}")
            n_est_analysis = combined_df.groupby(col).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(n_est_analysis)
    
    # Analizar max_depth (con y sin prefijo)
    max_depth_cols = [col for col in combined_df.columns if 'max_depth' in col]
    if max_depth_cols:
        print(f"\nAnálisis por max_depth:")
        for col in max_depth_cols:
            print(f"  Columna: {col}")
            depth_analysis = combined_df.groupby(col).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(depth_analysis)
    
    # Analizar min_samples_split (con y sin prefijo)
    min_split_cols = [col for col in combined_df.columns if 'min_samples_split' in col]
    if min_split_cols:
        print(f"\nAnálisis por min_samples_split:")
        for col in min_split_cols:
            print(f"  Columna: {col}")
            split_analysis = combined_df.groupby(col).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(split_analysis)
    
    # Analizar max_features (con y sin prefijo)
    max_feat_cols = [col for col in combined_df.columns if 'max_features' in col]
    if max_feat_cols:
        print(f"\nAnálisis por max_features:")
        for col in max_feat_cols:
            print(f"  Columna: {col}")
            feat_analysis = combined_df.groupby(col).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(feat_analysis)

# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la ruta real del directorio
    directory_path = "../../../sk_learn/tree/guardados"  # Directorio actual
    
    # Procesar todos los archivos con diagnóstico habilitado
    combined_df = process_multiple_rf_files(directory_path, debug=True)
    
    if combined_df is not None:
        print("\n¡Procesamiento completado exitosamente!")
        print("✓ Los datos han sido ordenados por orden específico de variables y luego por n_estimators")
        print("✓ Se han eliminado las columnas: is_implicit, has_stds")
        print("✓ Se ha agregado la columna 'regressor' con valor 'RandomForestRegressor'")
        print("✓ Variables ordenadas en el orden: dwi_sin, dwi_cos, wind_max, wind_med, shww_max, shww_med, mdts_sin, mdts_cos, shts_max, shts_med")
        
        # Análisis específico de parámetros de RandomForestRegressor
        analyze_rf_parameters(combined_df)
        
        # Mostrar mejores resultados por variable
        print("\nMejores resultados por variable:")
        best_results = combined_df.loc[combined_df.groupby('variable')['score'].idxmax()]
        
        # Mostrar columnas relevantes que existan
        display_cols = ['variable', 'score']
        
        # Añadir columnas de parámetros que existan
        param_cols = [col for col in combined_df.columns if any(param in col for param in ['n_estimators', 'max_depth', 'max_features'])]
        display_cols.extend(param_cols[:5])  # Limitar a 5 columnas adicionales
        
        print(best_results[display_cols])
    else:
        print("No se pudieron procesar los archivos. Verifica que existan archivos con el formato correcto en el directorio.")