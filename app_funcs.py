
def proc_inbound_msg(channel_type, data):
    
    if channel_type == "sms":
        msg_text = data['text']
        print(msg_text+": sms")
    else:
        msg_text = data['message']['content']['text']
        
    return (msg_text)

