from asyncio import DatagramTransport
import json, falcon

class ObjRequestClass:
    __json_content = {}
    def __validate_json_input(self, req):
        try:
            self.__json_content = json.loads(req.stream.read())
            print('json from client is validated')
            return True

        except ValueError, e:
            self.__json_content = {}
            print('Json from client is not validated')
            return False

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        validated =  self.__validate_json_input(req)

        output = {
            'status': 200,
            'msg': None
        }

        if (validated==True):

            output['msg'] = 'Hello {name}'.format(name=self.__json_content['name'])
    
        else:
            output['status'] = 404
            output['msg'] = 'Json input is not validated'


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