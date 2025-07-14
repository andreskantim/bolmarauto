import os
import pandas as pd
from pathlib import Path
import re
from typing import Dict, List, Tuple
import warnings
import ast
warnings.filterwarnings('ignore')

class SimpleModelExtractor:
    def __init__(self):
        self.expected_variables = [
            'dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 
            'shww_max', 'shww_med', 'mdts_sin', 'mdts_cos', 
            'shts_max', 'shts_med'
        ]

    def find_result_files(self, base_directory: str, filename: str = "resultados_analisis.txt") -> List[Tuple[str, str]]:
        """Busca archivos de resultados en subdirectorios."""
        files_found = []
        base_path = Path(base_directory)
        
        if not base_path.exists():
            raise FileNotFoundError(f"El directorio {base_directory} no existe")
            
        for subdir in base_path.iterdir():
            if subdir.is_dir():
                file_path = subdir / filename
                if file_path.exists():
                    files_found.append((subdir.name, str(file_path)))
                    
        return files_found

    def parse_pandas_series_text(self, text: str) -> Dict:
        """Parsea texto que representa una pandas Series."""
        result = {}
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('dtype:') or line.startswith('Name:'):
                continue
                
            match = re.match(r'^([^\s]+)\s+(.+)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                if value.lower() == 'nan':
                    value = None
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                else:
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass
                
                result[key] = value
        
        return result

    def parse_nested_dict_text(self, text: str) -> Dict:
        """Parsea texto que representa un diccionario anidado de Python."""
        try:
            # Intentar evaluar directamente como código Python
            result = ast.literal_eval(text)
            return result
        except:
            # Si falla, intentar un parsing manual más robusto
            result = {}
            
            # Usar regex para extraer variables principales
            var_pattern = r"'([^']+)':\s*\{([^}]+)\}"
            matches = re.findall(var_pattern, text, re.DOTALL)
            
            for var_name, var_content in matches:
                var_data = {}
                
                # Parsear contenido de cada variable
                param_pattern = r"'([^']+)':\s*\{([^}]+)\}"
                param_matches = re.findall(param_pattern, var_content)
                
                for param_name, param_content in param_matches:
                    param_data = {}
                    
                    # Extraer valor y score_promedio
                    valor_match = re.search(r"'valor':\s*([^,]+)", param_content)
                    score_match = re.search(r"'score_promedio':\s*([^,}]+)", param_content)
                    
                    if valor_match:
                        valor = valor_match.group(1).strip()
                        try:
                            param_data['valor'] = float(valor) if '.' in valor else int(valor)
                        except:
                            param_data['valor'] = valor
                    
                    if score_match:
                        score = score_match.group(1).strip()
                        try:
                            param_data['score_promedio'] = float(score)
                        except:
                            param_data['score_promedio'] = score
                    
                    var_data[param_name] = param_data
                
                result[var_name] = var_data
            
            return result

    def extract_section_data(self, content: str, start_marker: str, end_marker: str) -> Dict:
        """Extrae datos de una sección específica del archivo."""
        mejores_modelos = {}
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print(f"No se encontró la sección '{start_marker}' en el archivo")
            return mejores_modelos
            
        section = content[start_idx + len(start_marker):end_idx].strip()
        
        try:
            # Buscar patrones de variables
            pattern = r"'([^']+)':\s*([^'}]+?)(?=\s*'[^']*':|$)"
            matches = re.findall(pattern, section, re.DOTALL)
            
            for var_name, data_text in matches:
                var_name = var_name.strip()
                data_text = data_text.strip()
                
                parsed_data = self.parse_pandas_series_text(data_text)
                
                if parsed_data:
                    mejores_modelos[var_name] = parsed_data
                    
        except Exception as e:
            print(f"Error parseando sección: {e}")
            
        return mejores_modelos

    def extract_nested_section_data(self, content: str, start_marker: str, end_marker: str) -> Dict:
        """Extrae datos de una sección con estructura anidada."""
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print(f"No se encontró la sección '{start_marker}' en el archivo")
            return {}
            
        section = content[start_idx + len(start_marker):end_idx].strip()
        
        try:
            # Intentar parsear como diccionario Python
            parsed_data = self.parse_nested_dict_text(section)
            return parsed_data
            
        except Exception as e:
            print(f"Error parseando sección anidada: {e}")
            return {}

    def load_results(self, file_paths: List[Tuple[str, str]]) -> Tuple[Dict, Dict]:
        """Carga resultados de mejores modelos y valores promedio."""
        all_best_models = {}
        all_avg_values = {}
        
        for folder_name, file_path in file_paths:
            try:
                print(f"Procesando: {folder_name}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraer mejores modelos
                mejores_modelos = self.extract_section_data(
                    content, 
                    "MEJORES MODELOS:", 
                    "MEJORES VALORES PROMEDIO:"
                )
                
                # Extraer valores promedio (estructura anidada)
                valores_promedio = self.extract_nested_section_data(
                    content, 
                    "MEJORES VALORES PROMEDIO:", 
                    "VARIABILIDAD:"
                )
                
                # Almacenar mejores modelos
                for variable, data in mejores_modelos.items():
                    if variable not in all_best_models:
                        all_best_models[variable] = []
                    model_info = data.copy()
                    model_info['modelo_origen'] = folder_name
                    all_best_models[variable].append(model_info)
                
                # Almacenar valores promedio - solo el mejor score de cada variable
                for variable, param_data in valores_promedio.items():
                    if variable not in all_avg_values:
                        all_avg_values[variable] = []
                    
                    # Encontrar el mejor parámetro para esta variable en este archivo
                    best_param = None
                    best_score = float('-inf')
                    
                    for param_name, param_info in param_data.items():
                        score = param_info.get('score_promedio', float('-inf'))
                        if score > best_score:
                            best_score = score
                            best_param = {
                                'parameter': param_name,
                                'valor': param_info.get('valor'),
                                'score_promedio': score,
                                'modelo_origen': folder_name
                            }
                    
                    if best_param:
                        all_avg_values[variable].append(best_param)
                    
            except Exception as e:
                print(f"Error procesando {file_path}: {e}")
                
        return all_best_models, all_avg_values

    def find_best_models(self, all_results: Dict) -> Dict:
        """Encuentra el mejor modelo para cada variable basado en el score."""
        best_models = {}
        
        for variable, models in all_results.items():
            if not models:
                continue
                
            valid_models = [m for m in models if m.get('score') is not None and m.get('score') != 'NaN']
            
            if not valid_models:
                continue
                
            best_model = max(valid_models, key=lambda x: float(x.get('score', float('-inf'))))
            best_models[variable] = best_model
            
        return best_models

    def find_best_avg_values(self, all_avg_values: Dict) -> Dict:
        """Encuentra el mejor valor promedio para cada variable comparando todos los archivos."""
        best_avg_values = {}
        
        for variable, value_list in all_avg_values.items():
            if not value_list:
                continue
                
            # Encontrar el mejor score promedio para esta variable
            valid_values = [v for v in value_list if v.get('score_promedio') is not None]
            
            if valid_values:
                best_value = max(valid_values, 
                               key=lambda x: float(x.get('score_promedio', float('-inf'))))
                best_avg_values[variable] = best_value
                
        return best_avg_values

    def create_dataframe(self, data_dict: Dict, data_type: str = "mejores_modelos") -> pd.DataFrame:
        """Convierte los datos a DataFrame."""
        rows = []
        
        for variable, data in data_dict.items():
            row = {'Variable': variable}
            row.update(data)
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Reordenar columnas para que Variable esté primero
        if 'Variable' in df.columns:
            cols = ['Variable'] + [col for col in df.columns if col != 'Variable']
            df = df[cols]
        
        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Guarda DataFrame a CSV."""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✓ Archivo guardado: {filename}")

def main():
    # Configuración
    BASE_DIRECTORY = "../../entrenamiento_ev/TFM1"
    FILENAME = "resultados_analisis.txt"
    
    extractor = SimpleModelExtractor()
    
    try:
        # Buscar archivos
        print("Buscando archivos de resultados...")
        file_paths = extractor.find_result_files(BASE_DIRECTORY, FILENAME)
        
        if not file_paths:
            print(f"No se encontraron archivos '{FILENAME}' en subdirectorios de '{BASE_DIRECTORY}'")
            return
            
        print(f"Archivos encontrados: {len(file_paths)}")
        for folder, path in file_paths:
            print(f"  - {folder}")
        
        # Cargar resultados
        print("\nCargando resultados...")
        all_best_models, all_avg_values = extractor.load_results(file_paths)
        
        # Encontrar mejores modelos globales
        print("Procesando mejores modelos...")
        best_models = extractor.find_best_models(all_best_models)
        
        # Encontrar mejores valores promedio globales
        print("Procesando valores promedio...")
        best_avg_values = extractor.find_best_avg_values(all_avg_values)
        
        # Crear DataFrames
        df_best_models = extractor.create_dataframe(best_models, "mejores_modelos")
        df_avg_values = extractor.create_dataframe(best_avg_values, "valores_promedio")
        
        # Guardar CSVs
        print("\nGuardando resultados...")
        extractor.save_to_csv(df_best_models, "mejores_modelos_global.csv")
        extractor.save_to_csv(df_avg_values, "mejores_valores_promedio_global.csv")
        
        # Mostrar resumen
        print(f"\n✅ Proceso completado!")
        print(f"- Mejores modelos: {len(df_best_models)} variables")
        print(f"- Valores promedio: {len(df_avg_values)} variables")
        
        # Mostrar primeras filas como preview
        print("\n📋 Preview mejores modelos:")
        print(df_best_models.head())
        
        print("\n📋 Preview valores promedio:")
        print(df_avg_values.head())
        
    except Exception as e:
        print(f"Error en el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()