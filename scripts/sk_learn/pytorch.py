import pandas as pd
import pytorch
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from rich import print

from funciones_pytorch import PytornWrapper

if __name__=="__main__":
    input = pd.read_csv("/home/ulc/cursos/curso342/ecmwf/datasets/modelo/FQXX41MM-2023/cantabria.csv")
    target = pd.read_csv("/home/ulc/cursos/curso342/ecmwf/datasets/boletines/FQXX41MM-2023/cantabria.csv")

    input_columns = ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']
    drop_input_columns = ['dwi', 'mdts']
    columns_to_drop = [] 

    for var in drop_input_columns:
        columns = [col for col in input.columns if pd.Series(col).str.contains(fr'{var}\([^\)]+\)', regex=True).any()]
        columns_to_drop += columns  

    input.drop(['emission_time', 'valid_time'], axis=1, inplace=True)
    if columns_to_drop:
        input.drop(columns=columns_to_drop, axis=1, inplace=True)

    target.drop(['emission_time', 'valid_time', 'dwi', 'mdts'], axis=1, inplace=True)

    input=input.apply(lambda x: x.fillna(x.mean()), axis=0)
    target=target.apply(lambda x: x.fillna(x.mean()), axis=0)

    target = target.wind_max

    # Convertir a numpy arrays
    X = input.values
    y = target.values

    imputer = SimpleImputer()

    X_imputed = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)
    pca = PCA(n_components=0.99)
    X_pca = pca.fit_transform(X_scaled)

    X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.1)

    # Convertir a tensores de PyTorch
    #X_torch = torch.tensor(X_pca, dtype=torch.float32)
    #y_torch = torch.tensor(y, dtype=torch.float32)

    # Definir el dataset
    #dataset = TensorDataset(X_torch, y_torch)

    model = PytornWrapper(X_train.shape[1])
    model.fit(X_train, y_train)
    print(f'RMSE: {model.score(X_test, y_test)}')