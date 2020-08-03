def trans_map(cint):
    if cint < 10:
        return cint
    elif cint >= 10:
        return chr(cint - 10 + 65)

def tenToAny(n, origin):
    list = []
    while True:
        s = origin // n
        tmp = origin % n
        list.append(trans_map(tmp))
        if s == 0:
            break
        origin = s
    list.reverse()
    list = [str(each) for each in list]
    return ''.join(list)
