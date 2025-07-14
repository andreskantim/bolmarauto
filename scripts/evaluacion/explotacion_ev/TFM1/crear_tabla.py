import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import csv

class TableGenerator:
    def __init__(self):
        # Grupos de variables como en tu código original
        self.grupos_variables = {
            'dwi': ['dwi_sin', 'dwi_cos'],
            'wind': ['wind_max', 'wind_med'],
            'shww': ['shww_max', 'shww_med'],
            'mdts': ['mdts_sin', 'mdts_cos'],
            'shts': ['shts_max', 'shts_med']
        }
        
        # Colores para cada grupo (igual que tu código)
        self.colores_grupos = {
            'dwi': 'Reds',
            'wind': 'Blues', 
            'shww': 'Greens',
            'mdts': 'Purples',
            'shts': 'Oranges'
        }
        
        # Mapeo de variable a grupo
        self.variable_a_grupo = {}
        for grupo, variables in self.grupos_variables.items():
            for variable in variables:
                self.variable_a_grupo[variable] = grupo
        
        # Datos por defecto exactos
        self.title = "Primera iteración - Mejores modelos promedio"
        self.subtitle = "(Mejores scores promedio y parametro asociado)"

        self.columns = [
            "Variable",
            "Modelo",
            "Parámetro",
            "Score promedio"
        ]

        self.data = {
            'dwi_sin': ['dwi_sin', 'Random Forest', 'Número de árboles: 600', -0.467793176875],
            'dwi_cos': ['dwi_cos', 'Random Forest', 'Número de árboles: 400', -0.405128555],
            'wind_max': ['wind_max', 'Random Forest', 'Número de árboles: 600', -2.3237240675],
            'wind_med': ['wind_med', 'Random Forest', 'Número de árboles: 600', -2.019381899375],
            'shww_max': ['shww_max', 'Random Forest', 'Número de árboles: 600', -0.9078172275],
            'shww_med': ['shww_med', 'Random Forest', 'Número de árboles: 600', -0.6909454675],
            'mdts_sin': ['mdts_sin', 'Random Forest', 'Número de árboles: 600', -0.08481796625],
            'mdts_cos': ['mdts_cos', 'KNeighborsRegressor', 'Número vecinos: 100', -0.098115265],
            'shts_max': ['shts_max', 'Random Forest', 'Número de árboles: 600', -0.545075005],
            'shts_med': ['shts_med', 'Random Forest', 'Mínimo muestras hoja: 4', -0.484790345]
        }
        
        # self.columns = [
        #     "RMSE",
        #     "Media (μ)",
        #     "Des. típica (σ)",
        #     "NRMSE μ",
        #     "R²"
        # ]

        # self.data = {
        #     'dwi_sin': [0.458977, -0.105, 0.778, 4.37, 0.652],
        #     'dwi_cos': [0.404174, 0.075, 0.615, 5.39, 0.568],
        #     'wind_max': [2.262005, 9.112, 4.062, 0.25, 0.690],
        #     'wind_med': [1.973359, 6.093, 3.611, 0.32, 0.704],
        #     'shww_max': [0.893987, 1.515, 1.755, 0.59, 0.741],
        #     'shww_med': [0.673985, 0.968, 1.393, 0.70, 0.766],
        #     'mdts_sin': [0.084395, -0.713, 0.117, 0.12, 0.481],
        #     'mdts_cos': [0.093883, 0.681, 0.124, 0.14, 0.426],
        #     'shts_max': [0.537733, 2.347, 1.228, 0.23, 0.808],
        #     'shts_med': [0.478289, 1.780, 1.060, 0.27, 0.796]
        # }

        # self.columns = [
        #     "Modelo",
        #     "Parametro 1", 
        #     "Parametro 2",
        #     "Parametro 3",
        #     "Parametro 4",
        #     "Parametro 5",
        #     "Score"
        # ]
        
        # self.data = {
        #     'dwi_sin': ['SVR Gaussiano', 'Algoritmo: SVR', 'Reesc.: StandartScaler', 'PCA: 0.95', 'Penalización error: 1.0', 'Tolerancia error: 0.2', -0.458977],
        #     'dwi_cos': ['Random Forest', 'Número de árboles: 100', 'Profundidad máx: No', 'Mín hojas división: 10', 'Mín muestras hoja: 4', 'Nº características: log2', -0.404174],
        #     'wind_max': ['SVR Gaussiano', 'Algoritmo: SVR', 'Reesc.: Ninguno', 'PCA: 0.95', 'Penalización error: 0.1', 'Tolerancia error: 0.2', -2.262005],
        #     'wind_med': ['SVR Gaussiano', 'Algoritmo: SVR', 'Reesc.: Ninguno', 'PCA: 0.95', 'Penalización error: 1.0', 'Tolerancia error: 0.1', -1.973359],
        #     'shww_max': ['GradientBoosting', 'Número de árboles: 100', 'Learning rate: 0.1', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: log2', -0.893987],
        #     'shww_med': ['GradientBoosting', 'Número de árboles: 100', 'Learning rate: 0.1', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: log2', -0.673985],
        #     'mdts_sin': ['GradientBoosting', 'Número de árboles: 200', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -0.084395],
        #     'mdts_cos': ['SVR Gaussiano', 'Algoritmo: SVR', 'Reesc.: StandartScaler', 'PCA: 0.95', 'Penalización error: 0.1', 'Tolerancia error: 0.1', -0.093883],
        #     'shts_max': ['GradientBoosting', 'Número de árboles: 200', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -0.537733],
        #     'shts_med': ['GradientBoosting', 'Número de árboles: 100', 'Learning rate: 0.1', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: log2', -0.478289]
        # }
        
        # Directorio de salida
        self.directorio_salida = "."
    
    def set_output_directory(self, directorio):
        """Cambiar directorio de salida"""
        self.directorio_salida = directorio
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def generate_table(self, filename="Mejores_modelos_promedio_primera_iteracion.png"):
        """Generar tabla exactamente como en tu código original"""
        print("\n" + "="*50)
        print("GENERANDO TABLA GRÁFICA: MEJORES MODELOS")
        print("="*50)
        
        # Preparar datos para la tabla
        variables_con_datos = list(self.data.keys())
        tabla_data = []
        
        for variable in variables_con_datos:
            valores = self.data[variable]
            # Convertir valores a string, formateando el último (score) con 6 decimales
            fila = []
            # for i, valor in enumerate(valores):
            #     if i == len(valores) - 1:  # Es el score (última columna)
            #         fila.append(f"{valor:.6f}")
            #     else:
            #         fila.append(str(valor))
            for i, valor in enumerate(valores):
               fila.append(str(valor))
            tabla_data.append(fila)
        
        # Crear la figura con tamaño exacto para la tabla
        fig_width = max(12, len(self.columns) * 2)
        fig_height = len(variables_con_datos) * 0.4 + 1.5  # Altura exacta para tabla + título
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Crear tabla ocupando todo el espacio disponible
        table = ax.table(cellText=tabla_data,
                        rowLabels=variables_con_datos,
                        colLabels=self.columns,
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
            
            for j in range(len(self.columns)):
                table[(i+1, j)].set_facecolor(color)
        
        # Título
        titulo_completo = f'{self.title}\n{self.subtitle}' if self.subtitle else self.title
        ax.set_title(titulo_completo, fontsize=14, fontweight='bold', pad=10, y=0.95)
        ax.axis('off')
        
        # Añadir márgenes pequeños en las 4 direcciones
        plt.subplots_adjust(top=0.92, bottom=0.08, left=0.05, right=0.95)
        
        # Guardar con configuración específica
        ruta_archivo = os.path.join(self.directorio_salida, filename)
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor='white')
        print(f"✓ Tabla gráfica guardada: {ruta_archivo}")
        plt.show()
        
        return ruta_archivo
    
    def export_to_csv(self, filename="Mejores_modelos_promedio_primera_iteracion.csv"):
        """Exportar datos a CSV"""
        # Crear DataFrame
        df = pd.DataFrame.from_dict(self.data, orient='index', columns=self.columns)
        df.index.name = 'Variable'
        
        # Guardar CSV
        ruta_archivo = os.path.join(self.directorio_salida, filename)
        df.to_csv(ruta_archivo, encoding='utf-8')
        print(f"✓ Datos exportados a: {ruta_archivo}")
        
        # Mostrar preview
        print("\nPreview del CSV:")
        print(df)
        
        return df

# Ejecutar directamente
if __name__ == "__main__":
    print("Generando tabla Decision Tree...")
    
    generator = TableGenerator()
    generator.generate_table("Mejores_modelos_promedio_primera_iteracion.png")
    generator.export_to_csv("Mejores_modelos_promedio_primera_iteracion.csv")
    
    print("\n✅ Tabla Decision Tree generada exitosamente!")
    print("Archivos creados:")
    print("- Decision_Tree_mejores_modelos.png")
    print("- datos_decision_tree.csv")