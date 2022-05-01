from email.mime import application
import falcon
import json

class InfoResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('\n This is the Predict endpoint \n'
        'Both requests and responses are served in JSON. \n'
        '\n'
        'INPUT: Flower Lengths (in cm) \n'
        '"sepal_length": [num]  \n'
        '"sepal_width":  [num]  \n'
        '"petal_length": [num]  \n'
        '"petal_width":  [num]  \n\n'
            'OUTPUT: Prediction (Species)   \n'
        '"Species": [string]    \n\n')


    def on_post(self, req, resp):
        """
        """
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            result_json = json.loads(raw_json.decode(), encoding='utf-8')
            # For Python 2.x, replace with
            # result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The '
                'JSON was incorrect.'
            )
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(invoke_predict(raw_json))
        resp.body = json.dumps(invoke_predict(raw_json))  
        # For Python 2.x, replace with
        # resp.body = json.dumps(invoke_predict(raw_json), encoding='utf-8') encoding not necessary in python3

app = application = falcon.API()

info = InfoResource()
app.add_route('/info', info)
app.add_route('/predicts', predicts)
