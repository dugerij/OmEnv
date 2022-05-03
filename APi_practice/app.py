from asyncio import DatagramTransport
import json, falcon

class ObjRequestClass:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        data = json.loads(req.stream.read())
        output = {
            'msg': 'Hello {0}'.format(data['name'])
        }
      
        resp.body = json.dumps(output)
       
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200
        data = json.loads(req.stream.read())

        equel = int(data['x']) + int(data['y'])
        output = {
            'msg': 'x: {0} + y: {1} is equal to {2}'.format(str(data['x']), str(data['y']), str(equel))
        }
      
        resp.body = json.dumps(output)
    
    def on_put(self, req, resp):
        resp.status = falcon.HTTP_200
        output = {
            'msg': 'put is not supported for now - sorry :('
        }

        resp.body = json.dumps(output)

    def on_delete(self, req, resp):
        resp.status = falcon.HTTP_200
        output = {
            'msg': 'delete is not supported for now - sorry :('
        }

        resp.body = json.dumps(output)

app = application = falcon.App()
repo = ObjRequestClass()
app.add_route('/demo', repo ) 