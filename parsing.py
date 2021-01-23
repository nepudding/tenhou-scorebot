
def parsing(x):
    if not x.startswith('-'):
        return None
    x = x.split()
    command = x[0][1:]
    option = ''
    args = []
    for i in x[1:]:
        if i.startswith('-'):
            option += i[1:]
        else:
            args.append(i)
    return {'command':command, 'option':option, 'args':args}