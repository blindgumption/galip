

import json 


def is_json(tstr):

    ret = None

    try:
        ret = json.loads(tstr)
    except ValueError:
        pass
    
    return ret

##
# I was getting an error when processing a request with garbage characters    
#     UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 95: invalid start byte
# found this post helpful: https://stackoverflow.com/questions/22216076/unicodedecodeerror-utf8-codec-cant-decode-byte-0xa5-in-position-0-invalid-s
# most of the comments are about trying to figure out what the character is supposed to be.  
# I just wanted to ignore the character as it was from some hacking URL
# what worked was opening the file as binary, read each line, decode and ignore errors.
# I don't think legit URLs to blindgumption.com will have garbage in the parameters. 
## 
with open('/var/log/nginx/access.log', 'rb') as logs:
    for blog in logs:
        print('=-=-=-=-=-=-')
        log = blog.decode(errors='ignore')
        lobj = is_json(log)
        if lobj != None:
            print(f"remote address: {lobj['remote_addr']}")
        else: 
            print('NO, it is NOT JSON!!')


        
