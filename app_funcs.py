
def proc_inbound_msg(channel_type, data):
    
    if channel_type == "sms":
        msg_text = data['text']
        logger.debug("sms")
    else:
        msg_text = data['message']['content']['text']
    return (msg_text)