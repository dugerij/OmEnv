import json
from predict import predict

def invoke_predict(raw_json):
    input_dict = json.loads(raw_json.decode())

    feature_list = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    mapped_inputs = []

    for feature in feature_list:
        mapped_inputs.append(input_dict[feature][0])
    model_usable_data = [mapped_inputs]

    raw_model_output = predict(model_usable_data)
    #prediction = json.load(str(raw_model_output)) #convert raw model results to json
	prediction = str(raw_model_output)
	return prediction