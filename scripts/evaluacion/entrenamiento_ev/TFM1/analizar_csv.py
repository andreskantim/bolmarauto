import pandas as pd
import numpy as np
from collections import defaultdict
import os
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import matplotlib.patches as patches

class CSVParameterAnalyzer:
    def __init__(self, csv_file_path, regressor_name="regressor", nombres_parametros_personalizados=None):
        """
        Inicializa el analizador con el archivo CSV
        
        Args:
            csv_file_path (str): Ruta al archivo CSV
            regressor_name (str): Nombre del regresor para títulos
            nombres_parametros_personalizados (list): Lista de nombres personalizados para los parámetros
        """
        self.csv_file_path = csv_file_path
        self.regressor_name = regressor_name
        self.df = None
        self.df_original = None  # NUEVO: para mantener copia de datos originales
        self.variables = ['dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 'shww_max', 
                        'shww_med', 'mdts_sin', 'mdts_cos', 'shts_max', 'shts_med']
        self.parametros = []
        self.parametro_especial = None
        self.results = {}
        self.nombres_parametros_personalizados = nombres_parametros_personalizados or []
        self.exclusiones_aplicadas = {}  # NUEVO: para rastrear las exclusiones
        
        # Crear directorio de salida basado en el nombre del regressor
        self.directorio_salida = regressor_name
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
            print(f"✓ Directorio creado: {self.directorio_salida}")
        
        # Definir grupos de variables para colores (5 grupos)
        self.grupos_variables = {
            'dwi': ['dwi_sin', 'dwi_cos'],
            'wind': ['wind_max', 'wind_med'],
            'shww': ['shww_max', 'shww_med'],
            'mdts': ['mdts_sin', 'mdts_cos'],
            'shts': ['shts_max', 'shts_med']
        }
        
        # Definir colores para cada grupo
        self.colores_grupos = {
            'dwi': 'Reds',
            'wind': 'Blues', 
            'shww': 'Greens',
            'mdts': 'Purples',
            'shts': 'Oranges'
        }
        
        # Mapeo de variables a grupos para acceso rápido
        self.variable_a_grupo = {var: grupo for grupo, vars in self.grupos_variables.items() for var in vars}
        
        # Diccionario de mapeo de parámetros originales a personalizados
        self.nombres_parametros = {}

    def get_nombre_parametro(self, param):
        """
        Obtiene el nombre personalizado de un parámetro o devuelve el nombre original
        
        Args:
            param (str): Nombre del parámetro original
            
        Returns:
            str: Nombre personalizado o nombre original
        """
        return self.nombres_parametros.get(param, param)
    
    def cargar_datos(self):
        """Carga y prepara los datos del CSV"""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            self.df_original = self.df.copy()  # NUEVO: guardar copia original
            print(f"✓ Archivo CSV cargado exitosamente: {len(self.df)} filas")
            print(f"✓ Columnas disponibles: {list(self.df.columns)}")
            return True
        except Exception as e:
            print(f"✗ Error al cargar el archivo CSV: {e}")
            return False

    def aplicar_exclusiones(self, exclusiones):
        """
        FUNCIÓN CORREGIDA: Aplica exclusiones de datos basándose en valores de parámetros
        
        Args:
            exclusiones (dict): Diccionario con formato {parametro: [lista_valores_a_excluir]}
                            Ejemplo: {'regressor': ['SDG'], 'scaler': ['StandardScaler']}
        """
        if not exclusiones:
            print("✓ No se aplicaron exclusiones")
            return True
        
        print("\n" + "="*50)
        print("APLICANDO EXCLUSIONES DE DATOS")
        print("="*50)
        
        # Restaurar datos originales antes de aplicar exclusiones
        self.df = self.df_original.copy()
        filas_originales = len(self.df)
        
        self.exclusiones_aplicadas = exclusiones.copy()
        
        # NUEVA: Mostrar información de debug antes de aplicar exclusiones
        print(f"📋 Datos originales: {filas_originales} filas")
        
        for parametro, valores_excluir in exclusiones.items():
            if parametro not in self.df.columns:
                print(f"⚠ Advertencia: El parámetro '{parametro}' no existe en el CSV")
                continue
            
            # NUEVO: Mostrar información de debug
            print(f"\n🔍 Procesando parámetro: {parametro}")
            valores_unicos_antes = self.df[parametro].value_counts()
            print(f"   Valores únicos antes: {list(valores_unicos_antes.index)}")
            print(f"   Valores a excluir: {valores_excluir}")
            
            # Contar filas antes de la exclusión
            filas_antes = len(self.df)
            
            # CORRECCIÓN: Convertir valores a string para comparación consistente
            # Esto evita problemas con tipos de datos mixtos
            valores_excluir_str = [str(v) for v in valores_excluir]
            
            # Crear máscara de exclusión comparando como strings
            mascara_exclusion = self.df[parametro].astype(str).isin(valores_excluir_str)
            
            # NUEVO: Mostrar cuántas filas coinciden
            filas_coincidentes = mascara_exclusion.sum()
            print(f"   Filas que coinciden para exclusión: {filas_coincidentes}")
            
            # Aplicar exclusión (mantener las filas que NO están en la lista de exclusión)
            self.df = self.df[~mascara_exclusion]
            
            # Contar filas después de la exclusión
            filas_despues = len(self.df)
            filas_excluidas = filas_antes - filas_despues
            
            print(f"✓ Parametro '{parametro}': Excluidos valores {valores_excluir}")
            print(f"  - Filas excluidas: {filas_excluidas}")
            print(f"  - Filas restantes: {filas_despues}")
            
            # NUEVO: Verificar valores únicos después de la exclusión
            if filas_excluidas > 0:
                valores_unicos_despues = self.df[parametro].value_counts()
                print(f"   Valores únicos después: {list(valores_unicos_despues.index)}")
            else:
                print(f"   ⚠️ No se excluyeron filas para este parámetro")
        
        filas_finales = len(self.df)
        total_excluidas = filas_originales - filas_finales
        porcentaje_excluido = (total_excluidas / filas_originales) * 100
        
        print(f"\n📊 RESUMEN DE EXCLUSIONES:")
        print(f"  - Filas originales: {filas_originales}")
        print(f"  - Filas excluidas: {total_excluidas}")
        print(f"  - Filas finales: {filas_finales}")
        print(f"  - Porcentaje excluido: {porcentaje_excluido:.2f}%")
        
        # Verificar que aún hay datos suficientes
        if filas_finales == 0:
            print("❌ ERROR: No quedan datos después de aplicar las exclusiones")
            return False
        elif filas_finales < 10:
            print("⚠ ADVERTENCIA: Quedan muy pocos datos después de las exclusiones")
        
        return True
    
    def configurar_parametros(self, parametros, parametro_especial=None):
        """
        Configura los parámetros a analizar
        
        Args:
            parametros (list): Lista de nombres de parámetros a analizar
            parametro_especial (str): Parámetro especial para análisis adicional
        """
        self.parametros = parametros
        self.parametro_especial = parametro_especial
        
        # Crear mapeo de nombres personalizados
        if self.nombres_parametros_personalizados:
            for i, param in enumerate(self.parametros):
                if i < len(self.nombres_parametros_personalizados):
                    self.nombres_parametros[param] = self.nombres_parametros_personalizados[i]
        
        # Verificar que los parámetros existen en el DataFrame
        missing_params = [p for p in parametros if p not in self.df.columns]
        if missing_params:
            print(f"⚠ Advertencia: Los siguientes parámetros no se encontraron en el CSV: {missing_params}")
            self.parametros = [p for p in parametros if p in self.df.columns]
        
        print(f"✓ Parámetros configurados: {self.parametros}")
        if self.nombres_parametros_personalizados:
            print(f"✓ Nombres personalizados configurados: {self.nombres_parametros}")
        if parametro_especial:
            print(f"✓ Parámetro especial: {parametro_especial}")
    
    def analizar_rango_parametros(self):
        """1. Análisis del rango de parámetros"""
        print("\n" + "="*50)
        print("1. ANÁLISIS DEL RANGO DE PARÁMETROS")
        print("="*50)
        
        rangos = {}
        for param in self.parametros:
            valores = self.df[param].dropna()
            valores_numericos = pd.to_numeric(valores, errors='coerce').dropna()
            
            if len(valores_numericos) > 0:
                rangos[param] = {
                    'min': valores_numericos.min(),
                    'max': valores_numericos.max(),
                    'valores_unicos': sorted(valores_numericos.unique())
                }
            else:
                # Para parámetros categóricos
                rangos[param] = {
                    'min': 'N/A',
                    'max': 'N/A',
                    'valores_unicos': sorted(valores.unique())
                }
        
        self.results['rangos_parametros'] = rangos
        
        # Mostrar tabla de rangos
        tabla_rangos = []
        for param, rango in rangos.items():
            tabla_rangos.append([
                param,
                rango['min'],
                rango['max'],
                ', '.join(map(str, rango['valores_unicos'][:10]))  # Mostrar solo primeros 10
            ])
        
        print(tabulate(tabla_rangos, 
                      headers=['Parámetro', 'Mínimo', 'Máximo', 'Valores Únicos (primeros 10)'],
                      tablefmt='grid'))
        
        return rangos
    
    def encontrar_mejor_modelo(self):
        """2. Encontrar el mejor modelo por variable"""
        print("\n" + "="*50)
        print("2. MEJOR MODELO POR VARIABLE")
        print("="*50)
        
        mejores_modelos = {}
        tabla_mejores = []
        
        for variable in self.variables:
            datos_var = self.df[self.df['variable'] == variable]
            if len(datos_var) > 0:
                # Convertir score a numérico
                datos_var = datos_var.copy()
                datos_var['score'] = pd.to_numeric(datos_var['score'], errors='coerce')
                
                # Encontrar el mejor modelo (score menos negativo = más alto)
                mejor_idx = datos_var['score'].idxmax()
                mejor_modelo = datos_var.loc[mejor_idx]
                
                mejores_modelos[variable] = mejor_modelo
                
                # Preparar fila para la tabla
                params_str = ', '.join([f"{p}={mejor_modelo[p]}" for p in self.parametros if p in mejor_modelo])
                tabla_mejores.append([
                    variable,
                    f"{mejor_modelo['score']:.6f}",
                    params_str
                ])
        
        self.results['mejores_modelos'] = mejores_modelos
        
        print(tabulate(tabla_mejores,
                      headers=['Variable', 'Mejor Score', 'Parámetros'],
                      tablefmt='grid'))
        
        return mejores_modelos
    
    def calcular_mejores_valores_promedio(self):
        """3. Mejores valores promedio por parámetro"""
        print("\n" + "="*50)
        print("3. MEJORES VALORES PROMEDIO POR PARÁMETRO")
        print("="*50)
        
        mejores_valores = {}
        
        for variable in self.variables:
            datos_var = self.df[self.df['variable'] == variable].copy()
            if len(datos_var) == 0:
                continue
                
            datos_var['score'] = pd.to_numeric(datos_var['score'], errors='coerce')
            mejores_valores[variable] = {}
            
            for param in self.parametros:
                if param in datos_var.columns:
                    # Agrupar por el parámetro y calcular promedio de score
                    grupos = datos_var.groupby(param)['score'].mean()
                    mejor_valor = grupos.idxmax()
                    mejor_score = grupos.max()
                    
                    # Formatear especialmente para PCA
                    if param == 'pca' and isinstance(mejor_valor, str) and 'n_components' in mejor_valor:
                        mejor_valor = mejor_valor.replace('n_components=', '').replace('PCA(', 'PCA(')
                    
                    mejores_valores[variable][param] = {
                        'valor': mejor_valor,
                        'score_promedio': mejor_score
                    }
        
        self.results['mejores_valores_promedio'] = mejores_valores
        
        # Crear tabla para mostrar
        tabla_valores = []
        for variable in self.variables:
            if variable in mejores_valores:
                fila = [variable]
                for param in self.parametros:
                    if param in mejores_valores[variable]:
                        valor = mejores_valores[variable][param]['valor']
                        score = mejores_valores[variable][param]['score_promedio']
                        fila.append(f"{valor} ({score:.4f})")  # Paréntesis correctamente cerrado
                    else:
                        fila.append('N/A')
                tabla_valores.append(fila)
        
        headers = ['Variable'] + self.parametros
        print(tabulate(tabla_valores, headers=headers, tablefmt='grid'))
        
        return mejores_valores
    
    def calcular_variabilidad_interna(self):
        """4. Calcular variabilidad interna (desviación típica) - VERSIÓN CORREGIDA PARA NONE"""
        print("\n" + "="*50)
        print("4. VARIABILIDAD INTERNA (DESVIACIÓN TÍPICA)")
        print("="*50)
        
        variabilidad = {}
        variabilidad_global = {}
        
        for variable in self.variables:
            datos_var = self.df[self.df['variable'] == variable].copy()
            if len(datos_var) == 0:
                continue
                
            datos_var['score'] = pd.to_numeric(datos_var['score'], errors='coerce')
            variabilidad[variable] = {}
            
            for param in self.parametros:
                if param not in datos_var.columns:
                    continue
                
                # CORRECCIÓN: Manejar None explícitamente
                # Convertir None a string 'None' para el groupby
                datos_var_temp = datos_var.copy()
                datos_var_temp[param] = datos_var_temp[param].fillna('None')
                
                # Verificar valores únicos después de convertir None
                valores_param_unicos = datos_var_temp[param].unique()
                print(f"🔍 {variable} - {param}: {len(valores_param_unicos)} valores únicos: {valores_param_unicos}")
                
                if len(valores_param_unicos) <= 1:
                    # Si hay 1 o menos valores únicos, la variabilidad es 0
                    print(f"   ⚠️  Solo 1 valor único para {param}, variabilidad = 0")
                    std_promedio = 0.0
                else:
                    # Calcular desviación estándar de los promedios por valor del parámetro
                    grupos = datos_var_temp.groupby(param)['score'].mean()
                    
                    # Debug: mostrar los grupos
                    print(f"   📊 Grupos encontrados: {len(grupos)} grupos")
                    for valor_param, score_promedio in grupos.items():
                        print(f"      {valor_param}: {score_promedio:.6f}")
                    
                    # Obtener los valores como array de numpy
                    valores_array = grupos.values
                    
                    # Calcular desviación estándar
                    if len(valores_array) <= 1:
                        std_promedio = 0.0
                        print(f"   ⚠️  Solo 1 grupo después del groupby, variabilidad = 0")
                    else:
                        # Usar numpy directamente para evitar problemas con pandas
                        try:
                            std_promedio = np.std(valores_array, ddof=1)
                            
                            # Si da NaN (puede pasar con ddof=1 y pocos valores), usar ddof=0
                            if np.isnan(std_promedio):
                                std_promedio = np.std(valores_array, ddof=0)
                            
                            # Si aún da NaN, calcular manualmente
                            if np.isnan(std_promedio):
                                if len(valores_array) == 2:
                                    # Para exactamente 2 valores, usar la fórmula simple
                                    std_promedio = abs(valores_array[0] - valores_array[1]) / np.sqrt(2)
                                else:
                                    # Para más valores, usar la fórmula estándar
                                    media = np.mean(valores_array)
                                    std_promedio = np.sqrt(np.sum((valores_array - media)**2) / (len(valores_array) - 1))
                            
                            # Asegurar que no sea NaN ni negativo
                            if np.isnan(std_promedio) or std_promedio < 0:
                                std_promedio = 0.0
                                
                        except Exception as e:
                            print(f"   ❌ Error calculando desviación estándar: {e}")
                            std_promedio = 0.0
                        
                        print(f"   ✓ Desviación estándar calculada: {std_promedio:.6f}")
                
                variabilidad[variable][param] = std_promedio
                
                # Acumular para variabilidad global
                if param not in variabilidad_global:
                    variabilidad_global[param] = []
                variabilidad_global[param].append(std_promedio)
        
        # Calcular variabilidad global promedio
        print(f"\n📈 RESUMEN DE VARIABILIDAD GLOBAL:")
        for param in variabilidad_global:
            # Filtrar valores NaN antes de calcular la media
            valores_validos = [v for v in variabilidad_global[param] if not np.isnan(v)]
            if valores_validos:
                variabilidad_global[param] = np.mean(valores_validos)
                print(f"   {param}: {variabilidad_global[param]:.6f}")
            else:
                variabilidad_global[param] = 0.0
                print(f"   {param}: 0.000000 (sin valores válidos)")
        
        # Ordenar por variabilidad global
        variabilidad_ordenada = sorted(variabilidad_global.items(), 
                                    key=lambda x: x[1], reverse=True)
        
        self.results['variabilidad'] = variabilidad
        self.results['variabilidad_global'] = variabilidad_global
        self.results['variabilidad_ordenada'] = variabilidad_ordenada
        
        # Mostrar tabla de variabilidad
        tabla_var = []
        for variable in self.variables:
            if variable in variabilidad:
                fila = [variable]
                for param in self.parametros:
                    if param in variabilidad[variable]:
                        fila.append(f"{variabilidad[variable][param]:.6f}")
                    else:
                        fila.append('N/A')
                tabla_var.append(fila)
        
        headers = ['Variable'] + self.parametros
        print(f"\n📊 TABLA DE VARIABILIDAD:")
        print(tabulate(tabla_var, headers=headers, tablefmt='grid'))
        
        # Mostrar ranking de variabilidad global
        print(f"\n📊 RANKING DE VARIABILIDAD GLOBAL:")
        for i, (param, var_val) in enumerate(variabilidad_ordenada, 1):
            print(f"{i}. {param}: {var_val:.6f}")
        
        return variabilidad, variabilidad_global, variabilidad_ordenada

    def crear_tabla_especial_vs_mayor_variabilidad(self):
        """5. Tabla de valores score: parámetro especial vs mayor variabilidad"""
        if not self.parametro_especial:
            print("\n⚠ No se especificó parámetro especial. Saltando análisis 5.")
            return None
        
        print("\n" + "="*50)
        print("5. TABLA: PARÁMETRO ESPECIAL VS MAYOR VARIABILIDAD")
        print("="*50)
        
        if 'variabilidad_ordenada' not in self.results:
            print("⚠ Debe ejecutar el análisis de variabilidad primero")
            return None
        
        param_mayor_var = self.results['variabilidad_ordenada'][0][0]
        print(f"Parámetro especial: {self.parametro_especial}")
        print(f"Parámetro con mayor variabilidad: {param_mayor_var}")
        
        tablas_especiales = {}
        
        for variable in self.variables:
            datos_var = self.df[self.df['variable'] == variable].copy()
            if len(datos_var) == 0:
                continue
            
            datos_var['score'] = pd.to_numeric(datos_var['score'], errors='coerce')
            
            # Crear tabla cruzada manejando None/NaN
            try:
                # Llenar valores NaN del parámetro especial con 'None'
                datos_var[self.parametro_especial] = datos_var[self.parametro_especial].fillna('None')
                
                tabla_cruzada = datos_var.groupby([self.parametro_especial, param_mayor_var])['score'].mean().unstack()
                
                # Reordenar filas: 'None' primero, luego el resto ordenado
                filas = tabla_cruzada.index.tolist()
                filas_none = [f for f in filas if str(f).lower() == 'none']
                filas_normales = [f for f in filas if str(f).lower() != 'none']
                
                # Ordenar filas normales
                try:
                    filas_normales = sorted(filas_normales, key=lambda x: float(x) if str(x).replace('.', '').replace('-', '').isdigit() else float('inf'))
                except:
                    filas_normales = sorted(filas_normales, key=str)
                
                # Reordenar tabla
                orden_filas = filas_none + filas_normales
                tabla_cruzada = tabla_cruzada.reindex(orden_filas)
                
                # Ordenar las columnas si es posible
                try:
                    tabla_cruzada = tabla_cruzada.reindex(sorted(tabla_cruzada.columns, key=lambda x: float(x) if str(x).replace('.', '').replace('-', '').isdigit() else float('inf')), axis=1)
                except:
                    pass  # Mantener orden original si no se puede ordenar
                
                tablas_especiales[variable] = tabla_cruzada
                
                print(f"\n📋 {variable.upper()}:")
                print(tabulate(tabla_cruzada.fillna('N/A'), 
                            headers=tabla_cruzada.columns,
                            tablefmt='grid',
                            floatfmt='.6f'))
            except Exception as e:
                print(f"⚠ Error al crear tabla cruzada para {variable}: {e}")
        
        self.results['tablas_especiales'] = tablas_especiales
        return tablas_especiales
    
    def crear_tabla_dos_mayor_variabilidad(self):
        """6. Tabla de los 2 parámetros con mayor variabilidad"""
        print("\n" + "="*50)
        print("6. TABLA: DOS PARÁMETROS CON MAYOR VARIABILIDAD")
        print("="*50)
        
        if 'variabilidad_ordenada' not in self.results or len(self.results['variabilidad_ordenada']) < 2:
            print("⚠ Se necesitan al menos 2 parámetros para este análisis")
            return None
        
        param1 = self.results['variabilidad_ordenada'][0][0]
        param2 = self.results['variabilidad_ordenada'][1][0]
        
        print(f"Parámetro 1 (mayor variabilidad): {param1}")
        print(f"Parámetro 2 (segunda mayor variabilidad): {param2}")
        
        tablas_dos_var = {}
        
        for variable in self.variables:
            datos_var = self.df[self.df['variable'] == variable].copy()
            if len(datos_var) == 0:
                continue
            
            datos_var['score'] = pd.to_numeric(datos_var['score'], errors='coerce')
            
            # Crear tabla cruzada
            tabla_cruzada = datos_var.groupby([param1, param2])['score'].mean().unstack()
            tablas_dos_var[variable] = tabla_cruzada
            
            print(f"\n📋 {variable.upper()}:")
            print(tabulate(tabla_cruzada.fillna('N/A'), 
                          headers=tabla_cruzada.columns,
                          tablefmt='grid',
                          floatfmt='.6f'))
        
        self.results['tablas_dos_var'] = tablas_dos_var
        return tablas_dos_var
    
    
    def crear_tabla_mejores_modelos_grafico(self):
        """1. Tabla gráfica con mejores valores y scores - CORREGIDA PARA PCA"""
        print("\n" + "="*50)
        print("GENERANDO TABLA GRÁFICA: MEJORES MODELOS")
        print("="*50)
        
        if 'mejores_modelos' not in self.results:
            print("⚠ Debe ejecutar el análisis de mejores modelos primero")
            return
        
        # Crear matriz de datos
        variables_con_datos = []
        matriz_valores = []
        matriz_scores = []
        
        for variable in self.variables:
            if variable in self.results['mejores_modelos']:
                variables_con_datos.append(variable)
                fila_valores = []
                modelo = self.results['mejores_modelos'][variable]
                
                for param in self.parametros:
                    if param in modelo:
                        valor = str(modelo[param])
                        
                        # Reemplazar 'nan' por 'Ninguno'
                        if valor.lower() == 'nan':
                            valor = 'Ninguno'
                        
                        # CORRECCIÓN PARA PCA: Extraer solo el valor numérico
                        elif param == 'pca' and 'PCA(' in valor:
                            # Buscar el patrón PCA(n_components=X) o PCA(X)
                            import re
                            # Buscar número después de = o después de PCA(
                            match = re.search(r'PCA\((?:n_components=)?([0-9.]+)', valor)
                            if match:
                                valor = match.group(1)
                            else:
                                valor = 'PCA'
                        
                        fila_valores.append(valor)
                    else:
                        fila_valores.append('N/A')
                
                matriz_valores.append(fila_valores)
                matriz_scores.append(float(modelo['score']))
        
        # Crear la figura con tamaño exacto para la tabla
        fig_width = max(12, len(self.parametros) * 2)
        fig_height = len(variables_con_datos) * 0.4 + 1.5  # Altura exacta para tabla + título
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Crear tabla con valores usando nombres personalizados
        tabla_data = []
        for i, variable in enumerate(variables_con_datos):
            fila = matriz_valores[i] + [f"{matriz_scores[i]:.6f}"]
            tabla_data.append(fila)
        
        # Usar nombres personalizados en las columnas
        nombres_columnas = [self.get_nombre_parametro(p) for p in self.parametros] + ['Mejor Score']
        
        # Crear tabla ocupando todo el espacio disponible
        table = ax.table(cellText=tabla_data,
                        rowLabels=variables_con_datos,
                        colLabels=nombres_columnas,
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 0.85])  # Especificar bbox para ocupar más espacio
        
        # Personalizar tabla
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.0, 1.8)  # Hacer las celdas más altas
        
        # Colorear filas según grupo de variables
        for i, variable in enumerate(variables_con_datos):
            grupo = self.variable_a_grupo.get(variable, 'otras')
            color = plt.cm.get_cmap(self.colores_grupos.get(grupo, 'Greys'))(0.3)
            
            for j in range(len(self.parametros) + 1):
                table[(i+1, j)].set_facecolor(color)
        
        # Título modificado
        ax.set_title(f'{self.regressor_name} - Mejores modelos\n(Mejores scores y parámetros asociados)', 
                    fontsize=14, fontweight='bold', pad=10, y=0.95)
        ax.axis('off')
        
        # Añadir márgenes pequeños en las 4 direcciones
        plt.subplots_adjust(top=0.92, bottom=0.08, left=0.05, right=0.95)
        
        # Guardar con configuración específica
        archivo_tabla = f"{self.regressor_name}_mejores_modelos.png"
        ruta_archivo = os.path.join(self.directorio_salida, archivo_tabla)
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor='white')
        print(f"✓ Tabla gráfica guardada: {ruta_archivo}")
        plt.show()

    def crear_heatmap_unificado(self, tipo_analisis):
        """
        Crea un heatmap unificado con leyendas individuales no superpuestas - CORREGIDA PARA PCA
        Args:
            tipo_analisis (str): 'valores_promedio', 'variabilidad' o 'parametro_especial'
        """
        if tipo_analisis not in ['valores_promedio', 'variabilidad', 'parametro_especial']:
            print(f"⚠ Tipo de análisis no válido: {tipo_analisis}")
            return
        
        print("\n" + "="*50)
        print(f"GENERANDO HEATMAP UNIFICADO: {tipo_analisis.upper()}")
        print("="*50)
        
        # Configuración específica para cada tipo de análisis
        if tipo_analisis == 'valores_promedio':
            if 'mejores_valores_promedio' not in self.results:
                print("⚠ Debe ejecutar el análisis de valores promedio primero")
                return
            
            datos = self.results['mejores_valores_promedio']
            titulo = f"{self.regressor_name} - Mejores valores promedio (score promedio)"
            archivo = f"{self.regressor_name}_mejores_valores.png"
            parametros_actuales = self.parametros
            
        elif tipo_analisis == 'variabilidad':
            if 'variabilidad' not in self.results:
                print("⚠ Debe ejecutar el análisis de variabilidad primero")
                return
            
            datos = self.results['variabilidad']
            titulo = f"{self.regressor_name} - Variabilidad (Desviación estándar)"
            archivo = f"{self.regressor_name}_variabilidad.png"
            parametros_actuales = self.parametros
            
        elif tipo_analisis == 'parametro_especial':
            if not self.parametro_especial:
                print("⚠ No se especificó parámetro especial")
                return
            
            # Obtener valores únicos del parámetro especial incluyendo None/NaN
            valores_especial = self.df[self.parametro_especial].unique()  # No usar dropna()
            
            # Convertir a lista y manejar None/NaN
            valores_especial = list(valores_especial)
            
            # Separar None/NaN del resto
            valores_none = []
            valores_normales = []
            
            for valor in valores_especial:
                if pd.isna(valor) or valor is None or str(valor).lower() in ['none', 'nan']:
                    valores_none.append(valor)
                else:
                    valores_normales.append(valor)
            
            # Ordenar valores normales
            try:
                # Intentar ordenar numéricamente
                valores_normales = sorted(valores_normales, key=lambda x: float(x) if str(x).replace('.', '').replace('-', '').isdigit() else float('inf'))
            except:
                # Si no se puede ordenar numéricamente, ordenar como strings
                valores_normales = sorted(valores_normales, key=str)
            
            # Combinar: None/NaN primero, luego el resto ordenado
            valores_especial = valores_none + valores_normales
            
            parametros_actuales = [str(v) if not pd.isna(v) else 'None' for v in valores_especial]
            nombre_param_especial = self.get_nombre_parametro(self.parametro_especial)
            titulo = f"{self.regressor_name} - Scores promedio por {nombre_param_especial}"
            archivo = f"{self.regressor_name}_especial.png"
        
        # Preparar datos y calcular rangos por grupo
        matriz_datos = []
        variables_con_datos = []
        rangos_grupos = {grupo: {'min': float('inf'), 'max': float('-inf')} for grupo in self.grupos_variables}
        
        for variable in self.variables:
            grupo = self.variable_a_grupo.get(variable)
            if grupo is None:
                continue
                
            if tipo_analisis == 'parametro_especial':
                datos_var = self.df[self.df['variable'] == variable].copy()
                if len(datos_var) == 0:
                    continue
                    
                datos_var['score'] = pd.to_numeric(datos_var['score'], errors='coerce')
                fila = []
                
                for valor_especial in valores_especial:
                    # Manejar comparación con None/NaN
                    if pd.isna(valor_especial) or valor_especial is None:
                        datos_filtrados = datos_var[datos_var[self.parametro_especial].isna()]
                    else:
                        datos_filtrados = datos_var[datos_var[self.parametro_especial] == valor_especial]
                    
                    score = datos_filtrados['score'].mean() if len(datos_filtrados) > 0 else np.nan
                    fila.append(score)
                    if not np.isnan(score):
                        rangos_grupos[grupo]['min'] = min(rangos_grupos[grupo]['min'], score)
                        rangos_grupos[grupo]['max'] = max(rangos_grupos[grupo]['max'], score)
            else:
                if variable not in datos:
                    continue
                    
                fila = []
                for param in parametros_actuales:
                    if param in datos[variable]:
                        valor = datos[variable][param]['score_promedio'] if tipo_analisis == 'valores_promedio' else datos[variable][param]
                        fila.append(valor)
                        if not np.isnan(valor):
                            rangos_grupos[grupo]['min'] = min(rangos_grupos[grupo]['min'], valor)
                            rangos_grupos[grupo]['max'] = max(rangos_grupos[grupo]['max'], valor)
                    else:
                        fila.append(np.nan)
            
            variables_con_datos.append(variable)
            matriz_datos.append(fila)
        
        if len(variables_con_datos) == 0:
            print("⚠ No hay datos para mostrar")
            return
        
        matriz_datos = np.array(matriz_datos)
        
        # Crear figura con tamaño proporcional y espacio para leyendas
        fig_width = max(8, min(20, len(parametros_actuales) * 0.8)) + 3
        fig_height = max(6, min(15, len(variables_con_datos) * 0.6))
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Crear heatmap manualmente con colores por grupo
        for i, variable in enumerate(variables_con_datos):
            grupo = self.variable_a_grupo[variable]
            cmap = plt.cm.get_cmap(self.colores_grupos[grupo])
            
            # Verificar si hay datos válidos para este grupo
            if np.isinf(rangos_grupos[grupo]['min']) or np.isinf(rangos_grupos[grupo]['max']):
                continue
                
            vmin, vmax = rangos_grupos[grupo]['min'], rangos_grupos[grupo]['max']
            if vmin == vmax:
                vmin, vmax = vmin - 0.001, vmax + 0.001  # Evitar división por cero
            
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            
            for j in range(len(parametros_actuales)):
                if j < len(matriz_datos[i]) and not np.isnan(matriz_datos[i, j]):
                    color = cmap(norm(matriz_datos[i, j]) * 0.7)
                    rect = patches.Rectangle((j-0.5, i-0.5), 1, 1, linewidth=1,
                                        edgecolor='white', facecolor=color)
                    ax.add_patch(rect)
                    
                    # Añadir texto
                    if tipo_analisis == 'valores_promedio':
                        if parametros_actuales[j] in datos[variable]:
                            valor = datos[variable][parametros_actuales[j]]['valor']
                            
                            # CORRECCIÓN PARA PCA: Extraer solo el valor numérico
                            if parametros_actuales[j] == 'pca' and isinstance(valor, str):
                                if valor.lower() == 'nan':
                                    valor = 'Ninguno'
                                elif 'PCA(' in valor:
                                    import re
                                    match = re.search(r'PCA\((?:n_components=)?([0-9.]+)', valor)
                                    if match:
                                        valor = match.group(1)
                                    else:
                                        valor = 'PCA'
                            
                            ax.text(j, i, f'{valor}\n({matriz_datos[i, j]:.4f})',
                                ha='center', va='center', fontsize=8, weight='bold')
                    else:
                        ax.text(j, i, f'{matriz_datos[i, j]:.4f}',
                            ha='center', va='center', fontsize=8, weight='bold')
        
        # Configurar ejes con nombres personalizados
        ax.set_xticks(range(len(parametros_actuales)))
        if tipo_analisis == 'parametro_especial':
            ax.set_xticklabels(parametros_actuales, rotation=45, ha='right')
        else:
            nombres_mostrar = [self.get_nombre_parametro(p) for p in parametros_actuales]
            ax.set_xticklabels(nombres_mostrar, rotation=45, ha='right')
        
        ax.set_yticks(range(len(variables_con_datos)))
        ax.set_yticklabels(variables_con_datos)
        
        # Ajustar límites
        ax.set_xlim(-0.5, len(parametros_actuales)-0.5)
        ax.set_ylim(len(variables_con_datos)-0.5, -0.5)
        
        # Crear leyendas individuales
        grupos_con_datos = []
        for grupo in sorted(self.grupos_variables.keys()):
            if grupo not in rangos_grupos or np.isinf(rangos_grupos[grupo]['min']):
                continue
            grupos_con_datos.append(grupo)
        
        # Crear leyendas verticales en el lado derecho
        for i, grupo in enumerate(grupos_con_datos):
            cmap = plt.cm.get_cmap(self.colores_grupos[grupo])
            vmin, vmax = rangos_grupos[grupo]['min'], rangos_grupos[grupo]['max']
            if vmin == vmax:
                vmin, vmax = vmin - 0.001, vmax + 0.001
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            
            # Posición para cada leyenda
            left = 1.02 + i * 0.08
            bottom = 0.2
            width = 0.02
            height = 0.6
            
            # Crear el eje para la leyenda
            cax = fig.add_axes([left, bottom, width, height])
            
            # Crear la leyenda
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, cax=cax)
            
            # Configurar ticks
            n_ticks = 5
            tick_values = np.linspace(vmin, vmax, n_ticks)
            cbar.set_ticks(tick_values)
            cbar.set_ticklabels([f"{val:.3f}" for val in tick_values])
            
            # Configurar etiquetas
            cbar.ax.yaxis.set_ticks_position('right')
            cbar.ax.tick_params(labelsize=7)
            cbar.set_label(grupo.upper(), rotation=90, labelpad=10, fontsize=9)
        
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        ax.grid(False)
        
        plt.tight_layout()
        ruta_archivo = os.path.join(self.directorio_salida, archivo)
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        print(f"✓ Heatmap unificado guardado: {ruta_archivo}")
        plt.show()

    def generar_visualizaciones(self, guardar_figuras=True):
        """Genera todas las visualizaciones solicitadas"""
        print("\n" + "="*50)
        print("GENERANDO TODAS LAS VISUALIZACIONES")
        print("="*50)
        
        plt.style.use('seaborn-v0_8')
        
        # 1. Tabla gráfica de mejores modelos
        self.crear_tabla_mejores_modelos_grafico()
        
        # 2. Heatmap unificado de valores promedio
        self.crear_heatmap_unificado('valores_promedio')
        
        # 3. Heatmap unificado de variabilidad
        self.crear_heatmap_unificado('variabilidad')
        
        # 4. Heatmap unificado del parámetro especial
        if self.parametro_especial:
            self.crear_heatmap_unificado('parametro_especial')
        
        # 5. Gráfico original de mejores scores
        if 'mejores_modelos' in self.results:
            plt.figure(figsize=(12, 6))
            variables = list(self.results['mejores_modelos'].keys())
            scores = [self.results['mejores_modelos'][var]['score'] for var in variables]
            
            # Colorear según grupo
            colors = [plt.cm.get_cmap(self.colores_grupos[self.variable_a_grupo[var]])(0.6) for var in variables]
            
            bars = plt.bar(variables, scores, color=colors, alpha=0.7)
            plt.title(f'{self.regressor_name} - Mejores scores por variable')
            plt.xlabel('Variables')
            plt.ylabel('Score')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if guardar_figuras:
                archivo_scores = 'figura_mejores_scores.png'
                ruta_archivo = os.path.join(self.directorio_salida, archivo_scores)
                plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
                print(f"✓ Figura guardada: {ruta_archivo}")
            plt.show()
    
    def exportar_resultados(self, nombre_archivo='resultados_analisis.txt'):
        """Exporta todos los resultados a un archivo de texto (MODIFICADA)"""
        ruta_archivo = os.path.join(self.directorio_salida, nombre_archivo)
        print(f"\n💾 Exportando resultados a {ruta_archivo}...")
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write("ANÁLISIS DE PARÁMETROS CSV\n")
            f.write("="*50 + "\n\n")
            
            # Escribir configuración
            f.write("CONFIGURACIÓN:\n")
            f.write(f"- Archivo CSV: {self.csv_file_path}\n")
            f.write(f"- Regressor: {self.regressor_name}\n")
            f.write(f"- Parámetros analizados: {', '.join(str(p) for p in self.parametros)}\n")
            f.write(f"- Parámetro especial: {self.parametro_especial}\n")
            f.write(f"- Variables: {', '.join(self.variables)}\n")
            
            # NUEVO: Escribir exclusiones aplicadas
            if self.exclusiones_aplicadas:
                f.write(f"\nEXCLUSIONES APLICADAS:\n")
                for parametro, valores in self.exclusiones_aplicadas.items():
                    f.write(f"- {parametro}: {', '.join(map(str, valores))}\n")
            f.write("\n")
            
            # Escribir nombres personalizados de parámetros
            if self.nombres_parametros:
                f.write("NOMBRES PERSONALIZADOS DE PARÁMETROS:\n")
                for param_orig, param_nombre in self.nombres_parametros.items():
                    f.write(f"- {param_orig}: {param_nombre}\n")
                f.write("\n")
            
            # Escribir grupos de variables
            f.write("GRUPOS DE VARIABLES Y COLORES:\n")
            for grupo, variables in self.grupos_variables.items():
                f.write(f"- {grupo.upper()} ({self.colores_grupos[grupo]}): {', '.join(variables)}\n")
            f.write("\n")
            
            # Escribir todos los resultados
            for key, value in self.results.items():
                f.write(f"{key.upper().replace('_', ' ')}:\n")
                f.write(str(value))
                f.write("\n\n")
        
        print(f"✓ Resultados exportados a {ruta_archivo}")
    
    def ejecutar_analisis_completo(self, parametros, parametro_especial=None, 
                              exclusiones=None, generar_graficos=True, exportar=True):
        """Ejecuta todo el análisis completo (MODIFICADA)"""
        print("🚀 INICIANDO ANÁLISIS COMPLETO")
        print("="*50)
        
        # Cargar datos
        if not self.cargar_datos():
            return False
        
        # NUEVO: Aplicar exclusiones si se especificaron
        if exclusiones:
            if not self.aplicar_exclusiones(exclusiones):
                return False
        
        # Configurar parámetros
        self.configurar_parametros(parametros, parametro_especial)
        
        # Ejecutar todos los análisis
        self.analizar_rango_parametros()
        self.encontrar_mejor_modelo()
        self.calcular_mejores_valores_promedio()
        self.calcular_variabilidad_interna()
        self.crear_tabla_especial_vs_mayor_variabilidad()
        self.crear_tabla_dos_mayor_variabilidad()
        
        # Generar visualizaciones
        if generar_graficos:
            self.generar_visualizaciones()
        
        # Exportar resultados
        if exportar:
            self.exportar_resultados()
        
        print("\n🎉 ANÁLISIS COMPLETO TERMINADO")
        print(f"\n📁 Archivos generados en la carpeta '{self.directorio_salida}':")
        print("   - resultados_analisis.txt (resultados completos)")
        print(f"   - {self.regressor_name}_mejores_modelos.png (tabla con mejores valores y scores)")
        print(f"   - {self.regressor_name}_mejores_valores.png (heatmap unificado de valores promedio)")
        print(f"   - {self.regressor_name}_variabilidad.png (heatmap unificado de variabilidad)")
        if self.parametro_especial:
            print(f"   - {self.regressor_name}_especial.png (heatmap del parámetro especial)")
        print("   - figura_mejores_scores.png (gráfico de barras original)")
        
        # NUEVO: Mostrar resumen de exclusiones si las hubo
        if exclusiones:
            print(f"\n🚫 EXCLUSIONES APLICADAS:")
            for parametro, valores in exclusiones.items():
                print(f"   - {parametro}: {', '.join(map(str, valores))}")
        
        return True

# FUNCIÓN PRINCIPAL MODIFICADA
def main():
    """Función principal para ejecutar el análisis (MODIFICADA)"""
    print("="*60)
    print("        ANALIZADOR DE PARÁMETROS CSV MEJORADO")
    print("="*60)
    
    # Configuración - MODIFICA ESTAS VARIABLES SEGÚN TUS NECESIDADES
    archivo_csv = "svr_poly.csv"  # Cambia por la ruta de tu archivo
    nombre_regressor = "SVR Polinómico"  # Nombre del regresor para títulos
    
    # Lista de parámetros a analizar
    parametros = [
        "regressor",
        "scaler",
        "pca",
        "regressor_C",
        "regressor_epsilon",
    ]
    
    # NUEVA CONFIGURACIÓN: Nombres personalizados para los parámetros
    # Cada nombre en esta lista corresponde al parámetro en la misma posición
    nombres_personalizados = [
        "Algoritmo",
        "Reescalador",
        "PCA",
        "Penalización error",
        "Tolerancia error",    
    ]
    
    # Parámetro especial (opcional)
    parametro_especial = "regressor"
    
    # ========== NUEVA CONFIGURACIÓN: EXCLUSIONES ==========
    # Diccionario para especificar qué datos excluir del análisis
    # Formato: {parametro: [lista_de_valores_a_excluir]}
    exclusiones = {
        # "regressor": ["SGD"],  # Excluir filas donde regressor sea "SDG"
        # Puedes agregar más exclusiones aquí:
        # "scaler": ["StandardScaler"],  # Ejemplo: excluir StandardScaler
        # "pca": ["PCA(n_components=5)"],  # Ejemplo: excluir PCA con 5 componentes
    }
    
    # Si no quieres excluir nada, simplemente cambia a:
    # exclusiones = None
    # o
    # exclusiones = {}
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: El archivo '{archivo_csv}' no existe.")
        print("Por favor, actualiza la variable 'archivo_csv' con la ruta correcta.")
        return
    
    # Crear analizador con nombres personalizados
    analizador = CSVParameterAnalyzer(
        archivo_csv, 
        nombre_regressor, 
        nombres_personalizados
    )
    
    # NUEVO: Pasar exclusiones al análisis
    exito = analizador.ejecutar_analisis_completo(
        parametros=parametros,
        parametro_especial=parametro_especial,
        exclusiones=exclusiones,  # NUEVO parámetro
        generar_graficos=True,
        exportar=True
    )
    
    if exito:
        print("\n✅ Análisis completado exitosamente!")
        print(f"\n📂 Todos los archivos se han guardado en la carpeta: {nombre_regressor}")
        print("\n📊 VISUALIZACIONES MEJORADAS:")
        print("   1. Tabla gráfica con mejores modelos (coloreada por grupos)")
        print("   2. Heatmaps unificados con colores por grupos de variables")
        print("   3. Nombres personalizados en títulos y leyendas")
        print("   4. Archivos organizados en carpeta específica del regresor")
        print("   5. Exclusiones de datos aplicadas según configuración")
        print("\n🎨 ESQUEMA DE COLORES POR GRUPOS:")
        print("   - dwi (dwi_sin, dwi_cos): Escala de rojos")
        print("   - wind (wind_max, wind_med): Escala de azules")
        print("   - shww (shww_max, shww_med): Escala de verdes")
        print("   - mdts (mdts_sin, mdts_cos): Escala de morados")
        print("   - shts (shts_max, shts_med): Escala de naranjas")
        print(f"\n📋 NOMBRES PERSONALIZADOS APLICADOS:")
        for i, param in enumerate(parametros):
            if i < len(nombres_personalizados):
                print(f"   - {param} → {nombres_personalizados[i]}")
        
        # NUEVO: Mostrar configuración de exclusiones
        if exclusiones:
            print(f"\n🚫 CONFIGURACIÓN DE EXCLUSIONES:")
            for parametro, valores in exclusiones.items():
                print(f"   - {parametro}: Se excluyen valores {valores}")
        else:
            print(f"\n✓ No se aplicaron exclusiones de datos")
            
    else:
        print("\n❌ El análisis no pudo completarse.")

# NUEVA FUNCIÓN AUXILIAR PARA EXPLORAR DATOS
def explorar_valores_parametros(archivo_csv, parametro):
    """
    Función auxiliar para explorar los valores únicos de un parámetro
    Útil para decidir qué valores excluir
    """
    try:
        df = pd.read_csv(archivo_csv)
        if parametro not in df.columns:
            print(f"❌ El parámetro '{parametro}' no existe en el archivo")
            return
        
        valores_unicos = df[parametro].value_counts()
        print(f"\n📊 Valores únicos para el parámetro '{parametro}':")
        print(valores_unicos)
        print(f"\nTotal de valores únicos: {len(valores_unicos)}")
        
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")


if __name__ == "__main__":
    main()