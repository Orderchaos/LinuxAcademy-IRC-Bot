#!/usr/bin/python3
import socket
#This first variable is the socket we’ll be using to connect and communicate with the IRC server. Sockets are complicated and can be used for many tasks in many ways. 
#See here if you’d like more information on sockets: https://docs.python.org/3/howto/sockets.html. 
#For now just know that this will be used to establish a continuous connection with the IRC server while the bot is running to send and receive information.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#This is the name of the server and channel we’ll be connecting to. We could hard code these, but having a variable makes a couple of steps easier. 
#For example, if we ever want to connect to a list of channels (instead of just one as in this example) or change to a different server or channel we don’t have to find every instance 
#and can just edit this variable instead.
#I’m using chat.freenode.net for this example. Other IRC networks will have you put in their name here.
server = "chat.freenode.net" # Server
#We don’t want to use and official/established channel while we do our testing. Aside from being rude, many channels have specific rules for bots or don’t allow them at all. 
#Make sure you check with a channel’s moderators before adding your bot to a channel. For our testing, we’re using a custom, unregistered room (Denoted by the ‘##’ before the channel name on Freenode). 
#This way we’ll be the only ones in the channel with the bot while we do our testing.
channel = "##bot-testing" # Channel
#This is what we’ll be naming the bot. It is how other users will see the bot in the channel. 
#Make sure this is an unused and unregistered nick as your bot won’t be able to connect if it’s already in use and it will be assigned a random name after 30s if it’s a registered and protected nick. 
#See here for more information on Nickname registration: https://en.wikipedia.org/wiki/Wikipedia:IRC/Tutorial#Nickname_registration
botnick = "IamaPythonBot" # Your bots nick.
#This will be used in one of our functions. All we’re doing is defining a nickname that can send administrative commands to the bot and an exit code to look for to end the bot. We’ll get to how to do this at the end.
adminname = "OrderChaos" #Your IRC nickname. I go by OrderChaos on IRC (and most other places) so that is what I'm using for this example.
exitcode = "bye " + botnick #Text that we will use
#To connect to IRC we need to use our socket variable (ircsock) and connect to the server. IRC is typically on port 6667 or 6697 (6697 is usually for IRC with SSL which is more secure). 
#We’ll be using 6667 for our example. We need to have the server name (established in our Global Variables) and the port number inside parentheses so it gets passed as a single item to the connection.
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
#Once we’ve established the connection we need to send some information to the server to let the server know who we are. We do this by sending our user information followed by setting the nickname we’d like to go by.
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) # user information
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
#So here we take in the channel name, as part of the function, then send the join command to the IRC network. 
def joinchan(chan): # join channel(s).

  #The ‘bytes’ part and "UTF-8” says to send the message to IRC as UTF-8 encoded bytes. In Python 2 this isn’t necessary, but changes to string encoding in Python 3 makes this a requirement here. 
  #You will see this on all the lines where we send data to the IRC server.
  ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  #Something to note, the "\n” at the end of the line denotes to send a new line character. It lets the server know we’re finished with that command rather than chaining all the commands onto the same line.
  # After sending the join command, we want to start a loop to continually check for and receive new info from server until we get a message with ‘End of /NAMES list.’. 
  #This will indicate we have successfully joined the channel. The details of how each function works is described in the main function section below. 
  #This is necessary so we don't process the joining message as commands.
  ircmsg = ""
  while ircmsg.find("End of /NAMES list.") == -1: 
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)
#This function doesn’t need to take any arguments as the response will always be the same. Just respond with "PONG :pingis" to any PING. 
#Different servers have different requirements for responses to PING so you may need to adjust/update this depending on your server. I’ve used this particular example with Freenode and have never had any issues.
def ping(): # respond to server Pings.
  ircsock.send(bytes("PONG :pingis\n", "UTF-8"))
#All we need for this function is to accept a variable with the message we’ll be sending and who we’re sending it to. We will assume we are sending to the channel by default if no target is defined. 
#Using target=channel in the parameters section says if the function is called without a target defined, example below in the Main Function section, then assume the target is the channel.
def sendmsg(msg, target=channel): # sends messages to the target.
  #With this we are sending a ‘PRIVMSG’ to the channel. The ":” lets the server separate the target and the message.
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
#Main function of the bot. This will call the other functions as necessary and process the information received from IRC and determine what to do with it.
def main():
  # start by joining the channel we defined in the Global Variables section.
  joinchan(channel)
  #Start infinite loop to continually check for and receive new info from server. This ensures our connection stays open. 
  #We don’t want to call main() again because, aside from trying to rejoin the channel continuously, you run into problems when recursively calling a function too many times in a row. 
  #An infinite while loop works better in this case.
  while 1:
    #Here we are receiving information from the IRC server. IRC will send out information encoded in UTF-8 characters so we’re telling our socket connection to receive up to 2048 bytes and decode it as UTF-8 characters. 
    #We then assign it to the ircmsg variable for processing.
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    # This part will remove any line break characters from the string. If someone types in "\n” to the channel, it will still include it in the message just fine. 
    #This only strips out the special characters that can be included and cause problems with processing.
    ircmsg = ircmsg.strip('\n\r')
    #This will print the received information to your terminal. You can skip this if you don’t want to see it, but it helps with debugging and to make sure your bot is working.
    print(ircmsg)
    #Here we check if the information we received was a PRIVMSG. PRIVMSG is how standard messages in the channel (and direct messages to the bot) will come in. 
    #Most of the processing of messages will be in this section.
    if ircmsg.find("PRIVMSG") != -1:
      #First we want to get the nick of the person who sent the message. Messages come in from from IRC in the format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
      #We need to split and parse it to analyze each part individually.
      name = ircmsg.split('!',1)[0][1:]
      #Above we split out the name, here we split out the message.
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      #Now that we have the name information, we check if the name is less than 17 characters. Usernames (at least for Freenode) are limited to 16 characters. 
      #So with this check we make sure we’re not responding to an invalid user or some other message.
      if len(name) < 17:
        #And this is our first detection block! We’ll use things like this to check the message and then perform actions based on what the message is. 
        #With this one, we’re looking to see if someone says Hi to the bot anywhere in their message and replying. Since we don’t define a target, it will get sent to the channel.
        if message.find('Hi ' + botnick) != -1:
          sendmsg("Hello " + name + "!")
        #Here is an example of how you can look for a ‘code’ at the beginning of a message and parse it to do a complex task. 
        #In this case, we’re looking for a message starting with ".tell” and using that as a code to look for a message and a specific target to send to. 
        #The whole message should look like ".tell [target] [message]” to work properly.
        if message[:5].find('.tell') != -1:
          #First we split the command from the rest of the message. We do this by splitting the message on the first space and assigning the target variable to everything after it.
          target = message.split(' ', 1)[1]
          #After that, we make sure the rest of it is in the correct format. If there is not another then we don’t know where the username ends and the message begins!
          if target.find(' ') != -1:
              #If we make it here, it means we found another space to split on. We save everything after the first space (so the message can include spaces as well) to the message variable.
              message = target.split(' ', 1)[1]
              #Make sure to cut the message off from the target so it is only the target now.
              target = target.split(' ')[0]

          #if there is no defined message and target separation, we send a message to the user letting them know they did it wrong.
          else:

            #We do this by setting the target to the name of the user who sent the message (parsed from above)
            target = name
            #and then setting a new message. Note we use single quotes inside double quotes here so we don’t need to escape the inside quotes.
            message = "Could not parse. The message should be in the format of ‘.tell [target] [message]’ to work properly."
          #And finally we send the message to our target.
          sendmsg(message, target)
        #Here we add in some code to help us get the bot to stop. Since we created an infinite loop, there is no normal ‘end’. 
        #Instead, we’re going to check for some text and use that to end the function (which automatically ends the loop).
        #Look to see if the name of the person sending the message matches the admin name we defined earlier. 
        #We make both lower case in case the admin typed their name a little differently when joining. 
        #On IRC, ‘OrderChaos’ and ‘orderchaos’ are the same nickname, but Python will interpret them as different strings unless we convert it to all lower case first. 
        #We also make sure the message matches the exit code above. The exit code and the message must be EXACTLY the same. 
        #This way the admin can still type the exit code with extra text to explain it or talk about it to other users and it won’t cause the bot to quit. 
        #The only adjustment we're making is to trim off any whitespace at the end of the message. So if the message matches, but has an extra space at the end, it will still work.
        if name.lower() == adminname.lower() and message.rstrip() == exitcode:
          #If we do get sent the exit code, then send a message (no target defined, so to the channel) saying we’ll do it, but making clear we’re sad to leave.
          sendmsg("oh...okay. :'(")
          #Send the quit command to the IRC server so it knows we’re disconnecting.
          ircsock.send(bytes("QUIT \n", "UTF-8"))
          #The return command returns to when the function was called (we haven’t gotten there yet, see below) and continues with the rest of the script. 
          #In our case, there is not any more code to run through so it just ends.
          return
    #If the message is not a PRIVMSG it still might need some response.
    else:
      #Check if the information we received was a PING request. If so, we call the ping() function we defined earlier so we respond with a PONG.
      if ircmsg.find("PING :") != -1:
        ping()
#Finally, now that the main function is defined, we need some code to get it started.
main()
 
