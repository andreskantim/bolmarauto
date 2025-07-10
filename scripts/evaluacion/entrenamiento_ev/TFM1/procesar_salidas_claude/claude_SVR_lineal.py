import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, Normalizer
from sklearn.decomposition import PCA
from sklearn.svm import SVR
from sklearn.linear_model import SGDRegressor
from sklearn.kernel_approximation import Nystroem
from itertools import product
import re
import ast
import os
import glob
from pathlib import Path


def parse_param_dict_svm(param_str):
    """
    Parsea el diccionario de parámetros desde el string del archivo para SVM/SVR
    Maneja tanto regressor__C como regressor__alpha
    """
    try:
        # Limpiar el string y convertir a formato evaluable
        clean_str = param_str.strip()
        
        # Reemplazar objetos complejos con representaciones evaluables
        clean_str = clean_str.replace('StandardScaler()', '"StandardScaler"')
        clean_str = clean_str.replace('RobustScaler()', '"RobustScaler"')
        clean_str = clean_str.replace('Normalizer()', '"Normalizer"')
        clean_str = clean_str.replace('PCA(n_components=0.95)', '"PCA"')
        clean_str = clean_str.replace('SVR()', '"SVR"')
        clean_str = clean_str.replace('SGDRegressor()', '"SGDRegressor"')
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
                    elif value == "Normalizer":
                        new_values.append("Normalizer")
                    elif value == "PCA":
                        new_values.append("PCA")
                    elif value == "SVR":
                        new_values.append("SVR")
                    elif value == "SGDRegressor":
                        new_values.append("SGDRegressor")
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
                elif values == "Normalizer":
                    param_dict[key] = ["Normalizer"]
                elif values == "PCA":
                    param_dict[key] = ["PCA"]
                elif values == "SVR":
                    param_dict[key] = ["SVR"]
                elif values == "SGDRegressor":
                    param_dict[key] = ["SGDRegressor"]
                elif values is None:
                    param_dict[key] = [None]
                else:
                    param_dict[key] = [values]
        
        return param_dict
        
    except Exception as e:
        print(f"Error parseando parámetros: {e}")
        print(f"String original: {param_str}")
        return None


def extract_regressor_from_filename(filename):
    """
    Extrae el tipo de regresor del nombre del archivo
    """
    filename = filename.lower()
    
    if filename.startswith('linsvr'):
        return 'LinSVR'
    elif filename.startswith('sdg') or filename.startswith('sgd'):
        return 'SGD'
    elif filename.startswith('svr'):
        return 'SVR'
    else:
        # Fallback: buscar en el nombre del archivo
        if 'linsvr' in filename:
            return 'LinSVR'
        elif 'sdg' in filename or 'sgd' in filename:
            return 'SGD'
        else:
            return 'SVR'  # Por defecto


def detect_regressor_from_params(param_dict):
    """
    Detecta el tipo de regresor basándose en los parámetros presentes
    """
    if param_dict is None:
        return 'Unknown'
    
    # SGD tiene alpha y loss, SVR tiene C
    if 'regressor__alpha' in param_dict and 'regressor__loss' in param_dict:
        return 'SGD'
    elif 'regressor__C' in param_dict:
        if 'regressor__kernel' in param_dict:
            return 'SVR'
        else:
            return 'LinSVR'
    else:
        return 'Unknown'


def parse_svm_results_file(file_path):
    """
    Lee el archivo de resultados de SVM/SVR y extrae la información de cada variable
    """
    regressor_type = extract_regressor_from_filename(os.path.basename(file_path))
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Limpiar el contenido de errores de slurm
    content = re.sub(r'slurmstepd: info: Setting TMPDIR to /scratch/\d+\. Previous errors about TMPDIR can be discarded\s*', '', content)
    
    # Buscar todas las variables y sus datos
    variables = []
    
    # Patrón mejorado para capturar el diccionario de parámetros completo
    pattern = r'(\w+)\s*\n\[\s*\n?\s*\{\s*(.*?)\s*\}\s*\n?\s*\]\s*\n\[([-\d\.\s+e-]+)\]'
    matches = re.findall(pattern, content, re.DOTALL)
    
    # Procesar matches
    for match in matches:
        var_name = match[0]
        param_dict_str = '{' + match[1] + '}'
        scores_str = match[2]
        
        # Parsear el diccionario de parámetros
        param_dict = parse_param_dict_svm(param_dict_str)
        
        # Detectar el tipo de regresor basándose en los parámetros
        detected_regressor = detect_regressor_from_params(param_dict)
        if detected_regressor != 'Unknown':
            regressor_type = detected_regressor
        
        # Parsear los scores
        scores = []
        for score_str in scores_str.split():
            try:
                score = float(score_str)
                scores.append(score)
            except ValueError:
                print(f"Error convirtiendo score: {score_str}")
                scores.append(np.nan)
        
        # Crear std con 0.0 para cada score (ya que no hay std en el archivo)
        stds = [0.0] * len(scores)
        indices = list(range(len(scores)))
        
        print(f"Variable {var_name} (archivo: {regressor_type}):")
        print(f"  - Scores: {len(scores)} valores")
        print(f"  - Stds: {len(stds)} valores (todos 0.0)")
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
            'indices': indices,
            'regressor_type': regressor_type
        })
    
    return variables


def generate_svm_param_combinations(param_dict):
    """
    Genera todas las combinaciones posibles de parámetros para SVM/SVR
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


def format_svm_param_value(value):
    """
    Formatea los valores de parámetros de SVM/SVR para mostrar en el DataFrame
    """
    if value is None:
        return None
    elif isinstance(value, tuple):
        return str(value)
    else:
        return value


def normalize_svm_parameters(param_dict, regressor_type):
    """
    Normaliza los parámetros de SVM para que tengan nombres consistentes
    y agrega None para parámetros que no aplican al regresor específico
    Unifica regressor_C y regressor_alpha en una sola columna regressor_C
    """
    normalized_params = {}
    
    # Parámetros base que todos los regresores deben tener
    base_params = {
        'scaler': param_dict.get('scaler', [None]),
        'pca': param_dict.get('pca', [None]),
        'regressor_C': None,  # Unificado: tanto C como alpha van aquí
        'regressor_epsilon': param_dict.get('regressor__epsilon', [None]),
        'regressor_kernel': param_dict.get('regressor__kernel', [None]),
        'regressor_loss': param_dict.get('regressor__loss', [None])
        # Eliminamos nystroem_n_components
    }
    
    # Unificar C y alpha en regressor_C
    if 'regressor__C' in param_dict:
        base_params['regressor_C'] = param_dict['regressor__C']
    elif 'regressor__alpha' in param_dict:
        base_params['regressor_C'] = param_dict['regressor__alpha']
    
    # Rellenar con None los parámetros que no tiene este regresor
    for key, value in base_params.items():
        if value is None:
            normalized_params[key] = [None]
        else:
            normalized_params[key] = value
    
    return normalized_params


def create_svm_results_dataframe(variables_data, file_order=0, source_file=None):
    """
    Crea un DataFrame con todas las combinaciones y resultados de SVM/SVR
    """
    all_results = []
    variable_order = 0
    
    for var_data in variables_data:
        var_name = var_data['name']
        param_dict = var_data['param_dict']
        scores = var_data['scores']
        stds = var_data['stds']
        regressor_type = var_data['regressor_type']
        
        if param_dict is None:
            print(f"Saltando variable {var_name} por error en parámetros")
            continue
        
        # Normalizar parámetros
        normalized_params = normalize_svm_parameters(param_dict, regressor_type)
        
        # Generar combinaciones específicas para esta variable
        combinations, _ = generate_svm_param_combinations(normalized_params)
        
        print(f"\nProcesando variable {var_name}:")
        print(f"  - Combinaciones generadas: {len(combinations)}")
        print(f"  - Scores disponibles: {len(scores)}")
        print(f"  - Stds disponibles: {len(stds)}")
        print(f"  - Tipo de regresor: {regressor_type}")
        
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
                'regressor': regressor_type,
                'file_order': file_order,
                'variable_order': variable_order,
                'combination_order': i,
                'global_order': file_order * 10000 + variable_order * 1000 + i
            }
            
            # Agregar parámetros de la combinación i
            combo = combinations[i]
            for param_name, param_value in combo.items():
                # Modificar regressor_kernel por "lineal" en todas las filas
                if param_name == 'regressor_kernel':
                    row[param_name] = 'lineal'
                else:
                    row[param_name] = format_svm_param_value(param_value)
            
            # Asignar score y std por posición directa
            row['score'] = scores[i]
            row['std'] = stds[i]  # Ahora se asigna correctamente
            
            all_results.append(row)
            
            # Mostrar los primeros ejemplos para verificar
            if i < 5:
                print(f"    Combinación {i}: {combo} -> score: {scores[i]}, std: {stds[i]}")
        
        print(f"  - ✓ {max_items} filas procesadas para {var_name}")
        variable_order += 1
    
    return pd.DataFrame(all_results)


def find_svm_files(directory_path, pattern="*.txt"):
    """
    Encuentra todos los archivos de SVM/SVR que coinciden con el patrón en el directorio
    """
    if not os.path.exists(directory_path):
        print(f"El directorio {directory_path} no existe")
        return []
    
    search_pattern = os.path.join(directory_path, pattern)
    files = glob.glob(search_pattern)
    files = sorted(files)
    
    return files


def debug_svm_file_structure(file_path):
    """
    Función de diagnóstico para examinar la estructura del archivo de SVM/SVR
    """
    print(f"\n=== DIAGNÓSTICO DE ARCHIVO SVM: {os.path.basename(file_path)} ===")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Limpiar contenido de errores de slurm
    content = re.sub(r'slurmstepd: info: Setting TMPDIR to /scratch/\d+\. Previous errors about TMPDIR can be discarded\s*', '', content)
    
    print("Primeras 1000 caracteres del archivo (limpio):")
    print(content[:1000])
    print("...")
    
    # Buscar patrones SVM
    pattern = r'(\w+)\s*\n\[\s*\n?\s*\{\s*(.*?)\s*\}\s*\n?\s*\]\s*\n\[([-\d\.\s+e-]+)\]'
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"\nPatrones encontrados: {len(matches)}")
    
    # Mostrar ejemplo
    if matches:
        print("\nEjemplo:")
        match = matches[0]
        print(f"Variable: {match[0]}")
        print(f"Parámetros: {{{match[1]}}}")
        print(f"Scores (primeros 200 chars): {match[2][:200]}...")
        
        # Determinar tipo de regresor
        regressor_type = extract_regressor_from_filename(os.path.basename(file_path))
        print(f"Tipo de regresor detectado: {regressor_type}")
        
        # Parsear parámetros para detectar tipo
        param_dict_str = '{' + match[1] + '}'
        param_dict = parse_param_dict_svm(param_dict_str)
        detected_regressor = detect_regressor_from_params(param_dict)
        print(f"Tipo de regresor detectado por parámetros: {detected_regressor}")


def filter_extreme_scores(df, threshold=1e6):
    """
    Filtra scores extremos que pueden ser errores numéricos
    """
    print(f"\nFiltrando scores extremos (absoluto > {threshold})...")
    
    # Identificar scores extremos
    extreme_mask = (np.abs(df['score']) > threshold) | np.isinf(df['score'])
    extreme_count = extreme_mask.sum()
    
    if extreme_count > 0:
        print(f"  - Encontrados {extreme_count} scores extremos")
        print(f"  - Ejemplos de scores extremos: {df[extreme_mask]['score'].head().tolist()}")
        
        # Filtrar
        df_filtered = df[~extreme_mask].copy()
        print(f"  - DataFrame filtrado: {len(df_filtered)} filas (eliminadas {extreme_count})")
        
        return df_filtered
    else:
        print("  - No se encontraron scores extremos")
        return df


def process_multiple_svm_files(directory_path, output_path=None, file_pattern="*.txt", debug=False, filter_extremes=True):
    """
    Procesa múltiples archivos de SVM/SVR y los combina en un solo CSV
    """
    try:
        # Encontrar todos los archivos de SVM/SVR en el directorio
        print(f"Buscando archivos de SVM/SVR en: {directory_path}")
        svm_files = find_svm_files(directory_path, file_pattern)
        
        if not svm_files:
            print("No se encontraron archivos de SVM/SVR en el directorio")
            return None
        
        print(f"Encontrados {len(svm_files)} archivos:")
        for i, file in enumerate(svm_files):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        # Diagnóstico opcional
        if debug:
            for file_path in svm_files[:2]:  # Primeros dos archivos para diagnóstico
                debug_svm_file_structure(file_path)
        
        # Procesar cada archivo
        all_dataframes = []
        
        for file_order, file_path in enumerate(svm_files):
            print(f"\nProcesando archivo {file_order + 1}/{len(svm_files)}: {os.path.basename(file_path)}")
            
            try:
                # Leer y parsear el archivo
                variables_data = parse_svm_results_file(file_path)
                print(f"  Encontradas {len(variables_data)} variables")
                
                # Crear DataFrame con resultados
                df = create_svm_results_dataframe(variables_data, file_order=file_order, source_file=file_path)
                
                if df is not None and not df.empty:
                    all_dataframes.append(df)
                    print(f"  DataFrame creado con {len(df)} filas")
                    
                    # Verificar valores faltantes en este DataFrame
                    na_count_score = df['score'].isna().sum()
                    na_count_std = df['std'].isna().sum()
                    if na_count_score > 0 or na_count_std > 0:
                        print(f"  - ADVERTENCIA: {na_count_score} valores faltantes en score, {na_count_std} en std")
                    else:
                        print(f"  - ✓ Sin valores faltantes en score y std")
                        
                    # Mostrar los primeros scores y stds para verificar
                    print(f"  - Primeros 5 scores: {df['score'].head().tolist()}")
                    print(f"  - Primeros 5 stds: {df['std'].head().tolist()}")
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
        
        # Filtrar scores extremos si se solicita
        if filter_extremes:
            combined_df = filter_extreme_scores(combined_df)
        
        # Definir el orden específico de las variables
        variable_order = ['dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 'shww_max', 'shww_med', 'mdts_sin', 'mdts_cos', 'shts_max', 'shts_med']
        
        # Crear una columna auxiliar para el orden de variables
        combined_df['variable_sort_order'] = combined_df['variable'].apply(
            lambda x: variable_order.index(x) if x in variable_order else len(variable_order)
        )
        
        # Ordenar por orden específico de variables y luego por regresor
        print("Ordenando por orden específico de variables y luego por regresor...")
        combined_df = combined_df.sort_values(['variable_sort_order', 'regressor'])
        
        # Eliminar las columnas auxiliares de orden
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
        
        # Si hay valores faltantes en score, eliminar esas filas
        if none_scores > 0:
            print(f"\nEliminando {none_scores} filas con valores faltantes en score...")
            df_for_export = df_for_export.dropna(subset=['score'])
            print(f"DataFrame final con {len(df_for_export)} filas")
        
        # Mostrar información del DataFrame combinado
        print(f"\nDataFrame combinado creado con {len(df_for_export)} filas y {len(df_for_export.columns)} columnas")
        print(f"Variables procesadas: {df_for_export['variable'].unique()}")
        print(f"Regresores procesados: {df_for_export['regressor'].unique()}")
        print(f"Columnas: {list(df_for_export.columns)}")
        
        # Verificar que la columna std esté presente
        if 'std' in df_for_export.columns:
            print(f"✓ Columna 'std' presente con {df_for_export['std'].notna().sum()} valores válidos")
        else:
            print("✗ ADVERTENCIA: Columna 'std' no encontrada")
        
        # Mostrar las primeras filas
        print(f"\nPrimeras 5 filas del DataFrame:")
        print(df_for_export[['variable', 'regressor', 'score', 'std', 'regressor_kernel']].head())
        
        # Generar nombre de archivo de salida si no se especifica
        if output_path is None:
            output_path = "svm_results_sorted.csv"
            print(f"Nombre de archivo generado: {output_path}")
        
        # Reemplazar valores None con "None" para mejor visualización en CSV
        df_export = df_for_export.copy()
        df_export = df_export.fillna("None")
        
        # Guardar CSV
        df_export.to_csv(output_path, index=False)
        print(f"\nArchivo combinado guardado en: {output_path}")
        print("✓ Los datos están ordenados por orden específico de variables y luego por regresor")
        print("✓ Se ha incluido la columna 'regressor' identificando el tipo de regresor")
        print("✓ Se ha unificado regressor_C y regressor_alpha en una sola columna 'regressor_C'")
        print("✓ Se ha eliminado la columna 'nystroem_n_components'")
        print("✓ Se ha modificado 'regressor_kernel' por 'lineal' en todas las filas")
        print("✓ Se ha incluido correctamente la columna 'std'")
        print(f"✓ Variables ordenadas en el orden: {variable_order}")
        
        # Mostrar estadísticas por variable y regresor
        print("\nEstadísticas por variable y regresor:")
        var_reg_stats = df_for_export.groupby(['variable', 'regressor']).agg({
            'score': ['count', 'mean', 'std'],
            'std': ['mean', 'std']
        }).round(4)
        print(var_reg_stats)
        
        return df_for_export
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None


def analyze_svm_parameters(combined_df):
    """
    Analiza específicamente los parámetros de SVM/SVR
    """
    print("\n=== ANÁLISIS DE PARÁMETROS DE SVM/SVR ===")
    
    # Analizar por tipo de regresor
    print("\nAnálisis por tipo de regresor:")
    reg_analysis = combined_df.groupby('regressor').agg({
        'score': ['count', 'mean', 'std'],
        'std': ['mean', 'std'],
        'variable': 'nunique'
    }).round(4)
    print(reg_analysis)
    
    # Analizar parámetro C unificado
    if 'regressor_C' in combined_df.columns:
        print(f"\nAnálisis por regressor_C (C y alpha unificados):")
        param_analysis = combined_df[combined_df['regressor_C'] != 'None'].groupby(['regressor_C', 'regressor']).agg({
            'score': ['count', 'mean', 'std'],
            'std': ['mean', 'std']
        }).round(4)
        print(param_analysis)
    
    # Analizar epsilon
    if 'regressor_epsilon' in combined_df.columns:
        print(f"\nAnálisis por epsilon:")
        epsilon_analysis = combined_df[combined_df['regressor_epsilon'] != 'None'].groupby(['regressor_epsilon', 'regressor']).agg({
            'score': ['count', 'mean', 'std'],
            'std': ['mean', 'std']
        }).round(4)
        print(epsilon_analysis)
    
    # Analizar loss (específico para SGD)
    if 'regressor_loss' in combined_df.columns:
        print(f"\nAnálisis por loss (SGD):")
        loss_analysis = combined_df[combined_df['regressor_loss'] != 'None'].groupby(['regressor_loss', 'regressor']).agg({
            'score': ['count', 'mean', 'std'],
            'std': ['mean', 'std']
        }).round(4)
        print(loss_analysis)
    
    # Verificar que regressor_kernel sea 'lineal' en todas las filas
    if 'regressor_kernel' in combined_df.columns:
        print(f"\nVerificación de regressor_kernel:")
        kernel_values = combined_df['regressor_kernel'].value_counts()
        print(kernel_values)
        if 'lineal' in kernel_values and len(kernel_values) == 1:
            print("✓ Todas las filas tienen regressor_kernel = 'lineal'")
        else:
            print("✗ ADVERTENCIA: No todas las filas tienen regressor_kernel = 'lineal'")


# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar por la ruta real del directorio
    directory_path = "../../../sk_learn/svr/guardados"  # Directorio de archivos SVM
    
    # Procesar todos los archivos con diagnóstico habilitado
    combined_df = process_multiple_svm_files(directory_path, debug=True, filter_extremes=True)
    
    if combined_df is not None:
        print("\n¡Procesamiento completado exitosamente!")
        print("✓ Los datos han sido ordenados por orden específico de variables y luego por regresor")
        print("✓ Se ha incluido la columna 'regressor' identificando el tipo de regresor")
        print("✓ Se ha unificado regressor_C y regressor_alpha en una sola columna 'regressor_C'")
        print("✓ Se ha eliminado la columna 'nystroem_n_components'")
        print("✓ Se ha modificado 'regressor_kernel' por 'lineal' en todas las filas")
        print("✓ Se ha incluido correctamente la columna 'std'")
        print("✓ Variables ordenadas en el orden: dwi_sin, dwi_cos, wind_max, wind_med, shww_max, shww_med, mdts_sin, mdts_cos, shts_max, shts_med")
        print("✓ Se han filtrado scores extremos que pueden ser errores numéricos")