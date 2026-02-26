import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import mlflow
import mlflow.sklearn

def run_mlops_pipeline():
    print("Iniciar a pipeline de dados: ")

    try:
        df = pd.read_csv('../data/data.csv', sep=";", decimal=",")
    except FileNotFoundError:
        print("Erro: ficheiro não econtrado")
        return
    
    cols_para_checar = [
        'greenhous_temperature_celsius', 'greenhouse_humidity_percentage', 
        'online_temperature_celsius', 'online_humidity_percentage', 
        'greenhouse_equivalent_co2_ppm', 'greenhouse_illuminance_lux'
    ]

    df = df.dropna(subset=cols_para_checar)
    print(f"Dados carregados e limpos")

    print("[3/5] A gerar Rótulos de Risco...")
    cond1 = (df['greenhous_temperature_celsius'] > 32) & (df['greenhouse_humidity_percentage'] < 40)
    cond2 = (df['greenhouse_equivalent_co2_ppm'] > 2000)
    df['stress_risk'] = (cond1 | cond2).astype(int)

    features = [
        'greenhous_temperature_celsius', 
        'greenhouse_humidity_percentage',
        'greenhouse_illuminance_lux', 
        'online_temperature_celsius', 
        'online_humidity_percentage',
        'greenhouse_equivalent_co2_ppm'
    ]

    X = df[features]
    y = df['stress_risk']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("[4/5] A configurar o MLflow...")
   
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    
    experiment_name = "AgroStream_WaterStress_Prediction"
    mlflow.set_experiment(experiment_name)

  
    with mlflow.start_run(run_name="RandomForest_Baseline"):
     
        params = {
            "n_estimators": 50,
            "max_depth": 5,
            "random_state": 42
        }
        
        mlflow.log_params(params)
        
        print(f"      A treinar RandomForest com {params['n_estimators']} árvores...")
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        mlflow.log_metric("accuracy", acc)
        print(f"      Acurácia obtida: {acc * 100:.2f}%")

        mlflow.set_tag("features_list", ", ".join(features))

        print("Guardar o modelo no Model Registry do MLflow...")
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="random_forest_model",
            registered_model_name="AgroStream_Risk_Model" 
        )
    
    print("\n✅ Pipeline de MLOps concluído! Modelo versionado no MLflow com sucesso.")

if __name__ == "__main__":
    run_mlops_pipeline()