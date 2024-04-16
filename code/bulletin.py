import Base
import socket             
import json
import pprint

participant_count = Base.participant_count
bulletin_port = Base.bulletin_port
bulletin_board = Base.Bulletin(participant_count, "bulletin", bulletin_port)
      
 
while True: 
    connection, addr = bulletin_board.socket.accept()     
    connection_string = connection.recv(2048)
    data = json.loads(connection_string)
    if data['action'] == "put":
        ret_code = bulletin_board.put(data["id"], data["key"], data["value"])
        connection.send(str(ret_code).encode())
        pprint.pp(bulletin_board.stored_values)
    elif data['action'] == "get":
        ret_data = bulletin_board.get(data["type"], data["id"])
        connection.send(json.dumps(ret_data).encode())
    elif data['action'] == "done":
        bulletin_board.stored_values["done"].append(data["id"])
    # print("executed action: ", data['action'], " for id: ", data["id"], "with type: ", data["key"])
    print("executed action: ", data)

    connection.close()
    if bulletin_board.done():
        bulletin_board.socket.close()
        break

print("Bulletin Shutting down.")