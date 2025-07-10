import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from itertools import product
import re
import ast
import os
import glob
from pathlib import Path


def parse_param_dict_neural(param_str):
    """
    Parsea el diccionario de parámetros desde el string del archivo para redes neuronales
    """
    try:
        # Limpiar el string y convertir a formato evaluable
        clean_str = param_str.strip()
        
        # Reemplazar objetos complejos con representaciones evaluables
        clean_str = clean_str.replace('StandardScaler()', '"StandardScaler"')
        clean_str = clean_str.replace('RobustScaler()', '"RobustScaler"')
        
        # Reemplazar clases de PyTorch con strings
        clean_str = clean_str.replace("<class 'torch.nn.modules.activation.ReLU'>", '"ReLU"')
        clean_str = clean_str.replace("<class 'torch.nn.modules.activation.Tanh'>", '"Tanh"')
        clean_str = clean_str.replace("<class 'torch.nn.modules.activation.Sigmoid'>", '"Sigmoid"')
        clean_str = clean_str.replace("<class 'torch.nn.modules.activation.LeakyReLU'>", '"LeakyReLU"')
        clean_str = clean_str.replace("<class 'torch.nn.modules.activation.ELU'>", '"ELU"')
        
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
                elif value in ["ReLU", "Tanh", "Sigmoid", "LeakyReLU", "ELU"]:
                    new_values.append(value)
                elif value is None:
                    new_values.append(None)
                else:
                    new_values.append(value)
            param_dict[key] = new_values
        
        return param_dict
        
    except Exception as e:
        print(f"Error parseando parámetros neurales: {e}")
        print(f"String original: {param_str}")
        return None


def parse_param_dict_sklearn(param_str):
    """
    Parsea el diccionario de parámetros desde el string del archivo para modelos sklearn
    """
    try:
        # Limpiar el string y convertir a formato evaluable
        clean_str = param_str.strip()
        
        # Reemplazar objetos de sklearn con representaciones evaluables
        clean_str = clean_str.replace('DecisionTreeRegressor()', '"DecisionTreeRegressor"')
        clean_str = clean_str.replace('RandomForestRegressor()', '"RandomForestRegressor"')
        clean_str = clean_str.replace('StandardScaler()', '"StandardScaler"')
        clean_str = clean_str.replace('RobustScaler()', '"RobustScaler"')
        
        # Evaluar el diccionario
        param_dict = eval(clean_str)
        
        # Convertir de vuelta los valores especiales
        for key, values in param_dict.items():
            new_values = []
            for value in values:
                if value in ["DecisionTreeRegressor", "RandomForestRegressor", "StandardScaler", "RobustScaler"]:
                    new_values.append(value)
                elif value is None:
                    new_values.append(None)
                else:
                    new_values.append(value)
            param_dict[key] = new_values
        
        return param_dict
        
    except Exception as e:
        print(f"Error parseando parámetros sklearn: {e}")
        print(f"String original: {param_str}")
        return None


def detect_file_type(file_path):
    """
    Detecta si un archivo contiene resultados de redes neuronales o modelos sklearn
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Buscar indicadores de redes neuronales
    neural_indicators = [
        'regressor__activation',
        'regressor__lr',
        'regressor__epochs',
        'regressor__batch_size',
        'ReLU', 'Tanh', 'Sigmoid'
    ]
    
    # Buscar indicadores de sklearn
    sklearn_indicators = [
        'DecisionTreeRegressor',
        'RandomForestRegressor',
        'regressor__max_depth',
        'regressor__min_samples_split',
        'regressor__min_samples_leaf',
        'regressor__n_estimators'
    ]
    
    neural_count = sum(1 for indicator in neural_indicators if indicator in content)
    sklearn_count = sum(1 for indicator in sklearn_indicators if indicator in content)
    
    if neural_count > sklearn_count:
        return 'neural'
    elif sklearn_count > neural_count:
        return 'sklearn'
    else:
        return 'unknown'


def parse_neural_results_file(file_path):
    """
    Lee el archivo de resultados de redes neuronales y extrae la información de cada variable
    MANTIENE EL ORDEN ORIGINAL DEL ARCHIVO
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Buscar todas las variables y sus datos
    variables = []
    
    # Patrón para capturar el diccionario completo de parámetros de redes neuronales
    pattern = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([\d\s]+)\]'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        indices_str = match[4]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict_neural(param_dict_str)
        
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


def parse_sklearn_results_file(file_path):
    """
    Lee el archivo de resultados de modelos sklearn y extrae la información de cada variable
    MANTIENE EL ORDEN ORIGINAL DEL ARCHIVO
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Buscar todas las variables y sus datos
    variables = []
    
    # Patrón más flexible para capturar el diccionario completo de parámetros de sklearn
    # Busca: variable_name [ { params } ] [scores] [stds]
    pattern = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        stds_str = match[3]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict_sklearn(param_dict_str)
        
        # Parsear los scores y stds
        scores = [float(x) for x in scores_str.split()]
        stds = [float(x) for x in stds_str.split()]
        
        # Para sklearn, generar índices secuenciales
        indices = list(range(len(scores)))
        
        # Diagnóstico: verificar que las longitudes coincidan
        print(f"Variable {var_name}:")
        print(f"  - Scores: {len(scores)} valores")
        print(f"  - Stds: {len(stds)} valores")
        print(f"  - Indices generados: {len(indices)} valores")
        print(f"  - Primeros 5 scores: {scores[:5]}")
        print(f"  - Primeros 5 indices: {indices[:5]}")
        
        if param_dict:
            total_combinations = 1
            for key, values in param_dict.items():
                total_combinations *= len(values)
            print(f"  - Combinaciones esperadas: {total_combinations}")
            
            if len(scores) != len(stds):
                print(f"  - ADVERTENCIA: Las longitudes de scores y stds no coinciden!")
        
        variables.append({
            'name': var_name,
            'param_dict': param_dict,
            'scores': scores,
            'stds': stds,
            'indices': indices
        })
    
    return variables


def generate_param_combinations(param_dict):
    """
    Genera todas las combinaciones posibles de parámetros
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
    elif isinstance(value, tuple):
        return str(value)
    else:
        return value


def create_results_dataframe(variables_data, file_order=0, source_file=None):
    """
    Crea un DataFrame con todas las combinaciones y resultados
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
        combinations, _ = generate_param_combinations(param_dict)
        
        print(f"\nProcesando variable {var_name}:")
        print(f"  - Combinaciones generadas: {len(combinations)}")
        print(f"  - Scores disponibles: {len(scores)}")
        print(f"  - Indices disponibles: {len(indices)}")
        
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
                'global_order': file_order * 10000 + variable_order * 1000 + i,  # Orden global único
                'source_file': os.path.basename(source_file) if source_file else f"file_{file_order}"
            }
            
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
        variable_order += 1  # Incrementar el orden de la variable
    
    return pd.DataFrame(all_results)


def find_ml_files(directory_path, pattern="*.txt"):
    """
    Encuentra todos los archivos ML que coinciden con el patrón en el directorio
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


def debug_file_structure(file_path):
    """
    Función de diagnóstico para examinar la estructura del archivo
    """
    print(f"\n=== DIAGNÓSTICO DE ARCHIVO: {os.path.basename(file_path)} ===")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Detectar tipo de archivo
    file_type = detect_file_type(file_path)
    print(f"Tipo de archivo detectado: {file_type}")
    
    # Mostrar una muestra del contenido
    print("Primeras 1000 caracteres del archivo:")
    print(content[:1000])
    print("...")
    
    # Buscar patrones según el tipo
    if file_type == 'neural':
        pattern = r'(\w+)\s*\n\[\s*\{\s*([^}]+)\s*\}\s*\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([-\d\.\s]+)\]\s*\n\[([\d\s]+)\]'
    else:  # sklearn
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
        
        if file_type == 'neural' and len(match) > 4:
            indices_str = match[4]
            print(f"Indices: {indices_str}")
            indices = indices_str.split()
            print(f"Número de indices: {len(indices)}")
            print(f"Primeros 5 indices: {indices[:5]}")
        
        # Contar elementos
        scores = scores_str.split()
        stds = stds_str.split()
        
        print(f"Número de scores: {len(scores)}")
        print(f"Número de stds: {len(stds)}")
        
        # Mostrar los primeros valores para verificar
        print(f"Primeros 5 scores: {scores[:5]}")
        print(f"Primeros 5 stds: {stds[:5]}")


def process_multiple_ml_files(directory_path, output_path=None, file_pattern="*.txt", debug=False):
    """
    Procesa múltiples archivos ML y los combina en un solo CSV
    MANTIENE EL ORDEN ORIGINAL DE LOS ARCHIVOS Y DATOS
    """
    try:
        # Encontrar todos los archivos ML en el directorio
        print(f"Buscando archivos ML en: {directory_path}")
        ml_files = find_ml_files(directory_path, file_pattern)
        
        if not ml_files:
            print("No se encontraron archivos ML en el directorio")
            return None
        
        print(f"Encontrados {len(ml_files)} archivos:")
        for i, file in enumerate(ml_files):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        # Diagnóstico opcional
        if debug:
            for file_path in ml_files[:2]:  # Primeros 2 archivos para diagnóstico
                debug_file_structure(file_path)
        
        # Procesar cada archivo MANTENIENDO EL ORDEN
        all_dataframes = []
        
        for file_order, file_path in enumerate(ml_files):
            print(f"\nProcesando archivo {file_order + 1}/{len(ml_files)}: {os.path.basename(file_path)}")
            
            try:
                # Detectar tipo de archivo y usar el parser apropiado
                file_type = detect_file_type(file_path)
                print(f"  Tipo detectado: {file_type}")
                
                if file_type == 'neural':
                    # Leer y parsear el archivo de redes neuronales
                    variables_data = parse_neural_results_file(file_path)
                else:
                    # Leer y parsear el archivo de sklearn
                    variables_data = parse_sklearn_results_file(file_path)
                
                print(f"  Encontradas {len(variables_data)} variables")
                
                # Crear DataFrame con resultados - PASAR EL ORDEN DEL ARCHIVO
                df = create_results_dataframe(variables_data, file_order=file_order, source_file=file_path)
                
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
            df_for_export = df_for_export.dropna(subset=['score', 'std'])
            print(f"DataFrame final con {len(df_for_export)} filas")
        
        # Mostrar información del DataFrame combinado
        print(f"\nDataFrame combinado creado con {len(df_for_export)} filas y {len(df_for_export.columns)} columnas")
        print(f"Variables procesadas: {sorted(df_for_export['variable'].unique())}")
        print(f"Tipos de archivo procesados: {sorted(df_for_export['source_file'].unique())}")
        print(f"Columnas: {list(df_for_export.columns)}")
        
        # Verificar los primeros valores del DataFrame combinado
        print(f"\nPrimeras 5 filas del DataFrame (variable, source_file, score):")
        print(df_for_export[['variable', 'source_file', 'score']].head())
        
        # Generar nombre de archivo de salida si no se especifica
        if output_path is None:
            output_path = "ml_results_combined.csv"
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
        
        # Mostrar estadísticas por archivo fuente
        print("\nEstadísticas por archivo fuente:")
        file_stats = df_for_export.groupby('source_file').agg({
            'score': ['count', 'mean', 'std'],
            'variable': 'nunique'
        }).round(4)
        print(file_stats)
        
        # Mostrar muestra de datos
        print("\nPrimeras 10 filas del DataFrame combinado:")
        print(df_for_export.head(10))
        
        return df_for_export
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None


def analyze_ml_parameters(combined_df):
    """
    Analiza los parámetros de los diferentes tipos de modelos ML
    """
    print("\n=== ANÁLISIS DE PARÁMETROS DE MODELOS ML ===")
    
    # Analizar por tipo de archivo fuente
    print("\nAnálisis por archivo fuente:")
    source_analysis = combined_df.groupby('source_file').agg({
        'score': ['count', 'mean', 'std'],
        'variable': 'nunique'
    }).round(4)
    print(source_analysis)
    
    # Analizar parámetros comunes
    common_params = ['regressor', 'scaler']
    
    for param in common_params:
        if param in combined_df.columns:
            print(f"\nAnálisis por {param}:")
            param_analysis = combined_df.groupby(param).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(param_analysis)
    
    # Analizar parámetros específicos de árboles de decisión
    tree_params = ['regressor__max_depth', 'regressor__min_samples_split', 'regressor__min_samples_leaf']
    
    for param in tree_params:
        if param in combined_df.columns:
            print(f"\nAnálisis por {param}:")
            param_analysis = combined_df.groupby(param).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(param_analysis)
    
    # Analizar parámetros específicos de redes neuronales
    neural_params = ['regressor__activation', 'regressor__lr', 'regressor__epochs', 'regressor__batch_size']
    
    for param in neural_params:
        if param in combined_df.columns:
            print(f"\nAnálisis por {param}:")
            param_analysis = combined_df.groupby(param).agg({
                'score': ['count', 'mean', 'std'],
                'variable': 'nunique'
            }).round(4)
            print(param_analysis)


# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la ruta real del directorio
    directory_path = "../../../sk_learn/tree/guardados"  # o el directorio que contenga tus archivos
    
    # Procesar todos los archivos con diagnóstico habilitado
    combined_df = process_multiple_ml_files(directory_path, debug=True)
    
    if combined_df is not None:
        print("\n¡Procesamiento completado exitosamente!")
        print("✓ Los datos han sido ordenados según el orden específico de variables y mantienen el orden original dentro de cada variable")
        print("✓ Compatible con archivos de redes neuronales y modelos sklearn")
        
        # Análisis específico de parámetros
        analyze_ml_parameters(combined_df)
        
        # Mostrar mejores resultados por variable
        print("\nMejores resultados por variable:")
        best_results = combined_df.loc[combined_df.groupby('variable')['score'].idxmax()]
        print(best_results[['variable', 'source_file', 'score'] + [col for col in best_results.columns if col.startswith('regressor')]].to_string())
        
    else:
        print("No se pudieron procesar los archivos. Verifique la ruta y el formato de los archivos.")