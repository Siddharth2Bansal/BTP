import Base
import socket             
 
s = socket.socket()         
port = 12345               
 

participant_count = 4

bulletin_board = Base.Bulletin(participant_count, "bulletin")

s.bind(('', port))         
 
s.listen(5)     
 
while True: 
# Establish connection with client. 
  c, addr = s.accept()     
  print(addr, " connected")

  c.close()
   
  # Breaking once connection closed
  break