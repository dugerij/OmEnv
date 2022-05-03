from asyncio import DatagramTransport
import json, falcon

class ObjRequestClass:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        data = json.loads(req.stream.read())
        
        content = {
            'name': 'Paris',
            'age': '31',
            'country': 'Denmark'
        }
        output = {}
        if (data['method'] == 'get-name'):
            output['value'] = content['name']
        else:
            resp.status = falcon.HTTP_404
            output['value'] = None
        resp.body = json.dumps(output)
       

app = application = falcon.App()
repo = ObjRequestClass()
app.add_route('/test', repo ) 