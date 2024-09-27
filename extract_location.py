def extracting_location(City,state):
    if City != None and state != None: 
        Location = City + ', ' + state + ', ' + 'USA'
        
    elif City != None and state == None:
        Location = City + ', ' + 'USA'
    elif City == None and state != None:
        Location = state + ', ' + 'USA'   
    else:
        Location = 'USA'  
    return Location    