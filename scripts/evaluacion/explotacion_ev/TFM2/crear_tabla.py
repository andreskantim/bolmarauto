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
        # self.title = "Segunda iteración - Mejores modelos"
        self.title = "Segunda iteración - Resultados mejores modelos"
        self.subtitle = "(Metricas NRMSE y R²)"
        # self.subtitle = "(Mejores modelos y parametros asociados)"
        
        self.columns = [
            "RMSE",
            "Media (μ)",
            "Des. típica (σ)",
            "NRMSE μ",
            "R²"
        ]

        self.data = {
            'dwi_sin': [-0.473637, -0.0817, 0.8047, 5.797271, 0.653564],
            'dwi_cos': [-0.378441, 0.1253, 0.5745, 3.020279, 0.566073],
            'wind_max': [-2.184056, 9.0465, 3.7988, 0.241426, 0.669452],
            'wind_med': [-1.907909, 6.2004, 3.3841, 0.307707, 0.682145],
            'shww_max': [-0.797851, 1.3277, 1.3476, 0.600927, 0.649473],
            'shww_med': [-0.584145, 0.9176, 1.1160, 0.636601, 0.726024],
            'mdts_sin': [-0.122349, -0.6892, 0.1723, 0.177523, 0.495768],
            'mdts_cos': [-0.105635, 0.6902, 0.1376, 0.153050, 0.410643],
            'shts_max': [-0.539651, 2.2324, 1.1292, 0.241736, 0.771606],
            'shts_med': [-0.482846, 1.7451, 1.0175, 0.276687, 0.774810]
        }

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
        #     'dwi_sin': ['Random Forest', 'Número de árboles: 400', 'Profundidad máx: 20', 'Mín hojas división: 6', 'Mín muestras hoja: 12', 'Nº características: log2', -0.473637],
        #     'dwi_cos': ['GradientBoosting', 'Número de árboles: 400', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -0.378441],
        #     'wind_max': ['GradientBoosting', 'Número de árboles: 400', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -2.184056],
        #     'wind_med': ['GradientBoosting', 'Número de árboles: 400', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -1.907909],
        #     'shww_max': ['Random Forest', 'Número de árboles: 400', 'Profundidad máx: 20', 'Mín hojas división: 6', 'Mín muestras hoja: 8', 'Nº características: log2', -0.797851],
        #     'shww_med': ['GradientBoosting', 'Número de árboles: 200', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -0.584145],
        #     'mdts_sin': ['Random Forest', 'Número de árboles: 400', 'Profundidad máx: 20', 'Mín hojas división: 6', 'Mín muestras hoja: 12', 'Nº características: log2', -0.122349],
        #     'mdts_cos': ['GradientBoosting', 'Número de árboles: 200', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -0.105635],
        #     'shts_max': ['GradientBoosting', 'Número de árboles: 200', 'Learning rate: 0.05', 'Profundidad máx: 5.0', 'Fracc. datos usados: 0.8', 'Nº características: sqrt', -0.539651],
        #     'shts_med': ['Random Forest', 'Número de árboles: 200', 'Profundidad máx: 20', 'Mín hojas división: 2', 'Mín muestras hoja: 12', 'Nº características: log2', -0.482846]
        # }
        
        # Directorio de salida
        self.directorio_salida = "."
    
    def set_output_directory(self, directorio):
        """Cambiar directorio de salida"""
        self.directorio_salida = directorio
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def generate_table(self, filename="Mejores_modelos_primera_iteracion.png"):
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
    
    def export_to_csv(self, filename="Mejores_modelos_primera_iteracion.csv"):
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

    # generator.generate_table("Mejores_modelos_segunda_iteracion.png")
    # generator.export_to_csv("Mejores_modelos_segunda_iteracion.csv")

    generator.generate_table("Resultados_segunda_iteracion.png")
    generator.export_to_csv("Resultados_segunda_iteracion.csv")
    
    
    print("\n✅ Tabla Decision Tree generada exitosamente!")
    print("Archivos creados:")
    print("- Decision_Tree_mejores_modelos.png")
    print("- datos_decision_tree.csv")