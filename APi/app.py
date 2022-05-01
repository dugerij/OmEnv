import falcon

# from timestamp import Timestamp

# api = application = falcon.API()

# timestamp = Timestamp

# api.add_route('/timestamp', timestamp)

from hello_world_api import HelloWorldResource


app = application =falcon.App()

app.add_route("/hello_world", HelloWorldResource())