

def _short(s):
    return s[:1021] + "..." if len(s) > 1024 else s


def split_text(text, MAX_LEN=1024):
    """Return list of strings with at most MAX_LEN length, and be nice with formatting"""
    if "```" in text:
        MAX_LEN = max(1, MAX_LEN-3)
    ret = []
    if "--message-split--" in text:
        texts = text.split("--message-split--")
        for t in texts:
            ret += split_text(t)
        return ret
    num_block_markers = 0
    need_block_begin = False
    while len(text):
        msg = text[:MAX_LEN]
        num_block_markers += msg.count("```")
        if len(msg) < MAX_LEN:
            chunk = len(msg)
        else:
            chunk = -1
            for sep in ("\n", " ", ".", ";", ","):
                chunk = msg.rfind(sep)
                if chunk > 0:
                    if sep in ("\n", " "):
                        text = text[:chunk] + text[chunk + 1:]
                    break
            if chunk < 0:
                chunk = MAX_LEN

        msg = text[:chunk]
        if not len(msg):
            break
        if need_block_begin:
            msg = "```" + msg
            need_block_begin = False
        if num_block_markers % 2 == 1:
            msg += "```"
            need_block_begin = True
        ret.append(msg)
        text = text[chunk:]
    return ret
