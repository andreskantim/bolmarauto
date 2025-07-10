import os
import re
import ast
import numpy as np
import pandas as pd
from itertools import product

variables = [
    'dwi_sin', 'dwi_cos', 'wind_max', 'wind_med', 'shww_max', 'shww_med',
    'mdts_sin', 'mdts_cos', 'shts_max', 'shts_med'
]

param_grid = {
    'regressor': ['KNeighborsRegressor'],
    'regressor__n_neighbors': [1, 3, 5, 7, 10, 15, 20, 25],
    'pca': ['None', 'PCA(0.95)'],
    'scaler': ['None', 'StandardScaler', 'RobustScaler'],
    'regressor__weights': ['uniform', 'distance'],
    'regressor__metric': ['euclidean', 'manhattan', 'chebyshev']
}

param_combinations = list(product(*param_grid.values()))

# Tus datos proporcionados
scores_data = np.array([
    -0.47595495, -0.48203297, -0.49171448, -0.47446575, -0.48096407, -0.49016274,
    -0.47142882, -0.47856504, -0.48827827, -0.46969003, -0.47707044, -0.48622118,
    -0.47579681, -0.48249501, -0.48641211, -0.4747512,  -0.48169298, -0.4853662,
    -0.46959326, -0.47584796, -0.48091316, -0.4684207,  -0.47479505, -0.47933004,
    -0.54858422, -0.50911885, -0.52569507, -0.54365423, -0.50679608, -0.52263904,
    -0.55875244, -0.50645162, -0.5258634,  -0.55278992, -0.50416235, -0.5221631,
    -0.47559461, -0.47952479, -0.4929801,  -0.47414938, -0.47863103, -0.49112431,
    -0.47256216, -0.47606528, -0.48861372, -0.47059537, -0.474548,   -0.48640624,
    -0.4759856,  -0.47848542, -0.48360475, -0.47449075, -0.4773874,  -0.48224407,
    -0.47046881, -0.47519162, -0.47925313, -0.46883788, -0.47361422, -0.47732106,
    -0.47573025, -0.48086744, -0.50894431, -0.47401779, -0.48015185, -0.50584788,
    -0.47366563, -0.47843526, -0.50866888, -0.4712198,  -0.47680416, -0.50494847
])

stds_data = np.array([
    0.05453745, 0.06365307, 0.0641681,  0.05412514, 0.06354461, 0.0644519,
    0.05590821, 0.06576123, 0.06427481, 0.05560923, 0.06552676, 0.06453599,
    0.05804494, 0.06184439, 0.0609571,  0.05733673, 0.06194909, 0.06155531,
    0.05957822, 0.0637378,  0.06281459, 0.05908885, 0.06380239, 0.06322342,
    0.04376851, 0.06163324, 0.06702936, 0.04383388, 0.06157597, 0.06767479,
    0.0423924,  0.06130046, 0.06504529, 0.04247933, 0.06135921, 0.06615023,
    0.05541557, 0.06339528, 0.06235705, 0.05549701, 0.06324394, 0.06300164,
    0.05551255, 0.06466813, 0.06245679, 0.0557594,  0.06450463, 0.06291098,
    0.05645391, 0.06410051, 0.06234803, 0.05644141, 0.06396213, 0.06299518,
    0.05669284, 0.06560154, 0.06496862, 0.05696476, 0.06552242, 0.06524587,
    0.05180984, 0.06370742, 0.0579331,  0.05204124, 0.06360864, 0.0592892,
    0.05463036, 0.06293928, 0.0566461,  0.05457,    0.06307579, 0.05788803
])

rows = []

# Para cada variable
for var_idx, variable in enumerate(variables):
    # Para cada combinación de parámetros
    for comb_idx, combination in enumerate(param_combinations):
        # Calcular índices para scores y stds
        score_idx = var_idx * len(param_combinations) + comb_idx
        std_idx = var_idx * len(param_combinations) + comb_idx
        
        # Crear fila de datos
        row = {
            'variable': variable,
            'regressor': combination[0],
            'regressor__n_neighbors': combination[1],
            'pca': combination[2],
            'scaler': combination[3],
            'regressor__weights': combination[4],
            'regressor__metric': combination[5],
            'score': scores_data[score_idx],
            'std': stds_data[std_idx]
        }
        rows.append(row)

# Crear DataFrame
df = pd.DataFrame(rows)

print(df.head())
print(f"\nTotal de filas: {len(df)}")

df.to_csv('resultados_modelos.csv', index=False)