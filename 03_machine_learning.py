import polars as pl
import os
from sklearn.model_selection import train_test_split
from src.utils import load_config, get_logger
from src.model import train_model, evaluate_model, save_model

def main():
    logger = get_logger("Machine Learning")
    config = load_config()
    
    processed_path = config["data"]["processed_path"]
    model_path = config.get("model", {}).get("path", "src/models/maintenance_model.pkl")
    
    # 1. Load Processed Data
    logger.info(f"Loading processed data from {processed_path}")
    if not os.path.exists(processed_path):
        logger.error("Processed data not found! Run 02_analysis_and_features.py first.")
        return

    df = pl.read_csv(processed_path)
    
    # 2. Feature Selection
    features = config.get("features", {}).get("numerical", [])
    target = config.get("features", {}).get("target", "target")
    
    if not features:
        logger.warning("No features defined in config, using defaults.")
        features = ["air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear", "power_factor", "temp_diff"]
        
    X = df.select(features).to_pandas()
    y = df.select(target).to_pandas().values.ravel()
    
    # 3. Split Data
    test_size = config.get("base", {}).get("test_size", 0.2)
    random_state = config.get("base", {}).get("random_state", 42)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    

    # 4. Hiperparametre Optimizasyonu (Optuna)
    import optuna
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import make_scorer, f1_score

    def objective(trial):
        # Denenecek parametre aralıkları
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "max_depth": trial.suggest_int("max_depth", 5, 30),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
            "random_state": random_state
        }
        
        # Modeli oluştur (Log kirliliğini önlemek için direkt sklearn kullanıyoruz)
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(**params)
        
        # Cross Validation skoru
        score = cross_val_score(model, X_train, y_train, cv=3, scoring="f1").mean()
        return score

    logger.info("Optuna optimizasyonu başlıyor...")
    optuna.logging.set_verbosity(optuna.logging.WARNING) # Sadece önemli mesajları göster
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20) # 20 deneme yapacağız

    best_params = study.best_params
    logger.info(f"En iyi parametreler bulundu: {best_params}")
    
    # En iyi parametrelerle final modeli eğit
    logger.info("Final modeli en iyi parametrelerle eğitiliyor...")
    
    # MLflow ile Kayıt Başlat
    import mlflow
    import mlflow.sklearn
    from sklearn.metrics import classification_report
    
    mlflow.set_experiment("Endüstriyel Bakım Modeli")

    with mlflow.start_run(run_name="Optimized_RF_Run"):
        # Parametreleri kaydet
        mlflow.log_params(best_params)
        
        # Modeli eğit
        model = train_model(X_train, y_train, best_params)
        
        # Modeli kaydet (MLflow artifact olarak)
        mlflow.sklearn.log_model(model, "model")
        
        # 5. Evaluate Model ve Metrikleri Kaydet
        report_str = evaluate_model(model, X_test, y_test)
        
        # Classification report string dönüyor, biz ana metrikleri (accuracy, f1) ayrıca hesaplayıp loglayalım
        # evaluate_model log basıyor ama metrik değerlerini sözlük olarak dönmüyor
        # Bu yüzden burada manuel hesaplayıp mlflow'a atalım
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        
        y_pred = model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred)
        }
        
        mlflow.log_metrics(metrics)
        logger.info(f"Metrikler MLflow'a kaydedildi: {metrics}")
    
    # 6. Save Model (Lokal dosya sistemine de kaydedelim ki API kullansın)
    save_model(model, model_path)

if __name__ == "__main__":
    main()