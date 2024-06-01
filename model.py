import pickle
import os
from dataloader import load_pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from utils import convert_params
import neptune #pip install neptune
import joblib
import yaml
from dotenv import load_dotenv

def main():
    load_dotenv()

    project_name = os.getenv('NEPTUNE_PROJECT_NAME')
    api_key = os.getenv('NEPTUNE_API_TOKEN')

    run = neptune.init_run(project=project_name)

    train_data = load_pickle("train_data.pickle")
    test_data = load_pickle("test_data.pickle")

    train_x = train_data['x']
    train_y = train_data['y']

    test_x = test_data['x']
    test_y = test_data['y']

    print(train_x)

    with open("config.yaml","r") as file:
        config = yaml.safe_load(file)

    model_version = config["model_versions"]

    model_mapping = {
        "Random Forest" : RandomForestClassifier,
        "Decision Tree" : DecisionTreeClassifier,
        "Gradient Boosting" : GradientBoostingClassifier
    }

    for method in config["methods"]:
        model_name = method["name"]
        model_config = convert_params(method["config"])
        
        # Model namespace including version
        model_namespace = f"models/{model_name}/{model_version}"
        
        # Log model parameters to Neptune
        for param_name, param_value in model_config.items():
            run[f"{model_namespace}/parameters/{param_name}"] = param_value
        
        # Instantiate and train the model
        ModelClass = model_mapping[model_name]
        model = ModelClass(**model_config)
        model.fit(train_x, train_y)

        # Save the model to a file
        model_filename = f"{model_name}_{model_version}.joblib"
        joblib.dump(model, model_filename)

        # Log model artifact to Neptune
        run[f"{model_namespace}/artifact"].upload(model_filename)
        
        # Predict and evaluate
        predicted_y = model.predict(test_x)
        report = classification_report(test_y, predicted_y)
        
        # Log classification report to Neptune
        run[f"{model_namespace}/classification_report"] = report
        
        print(f"Classification Report for {model_name} (Version {model_version}):\n{report}\n")
    # Stop the Neptune run once all models are logged
    run.stop()

if __name__ == "__main__":
    main()



