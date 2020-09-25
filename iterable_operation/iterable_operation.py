def devide(n):
    """
    divide the list by number of n
    """
    for i in range(0,len(list(range(10))),n):
        yield list(range(10))[i:i+n]

print(list(devide(3)))

def flatten_list(l):
    """
    multiple array -> single one
    """
    for el in l:
        if isinstance(el, (list,range,tuple)):
            yield from flatten_list(el)
        else:
            yield el

l_2d_5 = [[0, 1, {"k" : "v"}]] * 5
print(list(flatten_list(l_2d_5)))



res = []
def search(arg, obj_type):
    """
    extract the specified type of data from the list or dictionary
    """
    if isinstance(arg,obj_type):
        res.append(arg)
    elif isinstance(arg, list):
        for item in arg:
            res.extend(search(item, obj_type))
    elif isinstance(arg, dict):
        for value in arg.values():
            res.extend(search(value, obj_type))
    return res

sample = {
    "a": [{
        "b": "y",
        "c": [{"d": [2,3,None]}],
        "e": {"g": "z"}
    }],
    "f": ["x"],
}
# get string value
print(search(sample,str))
# get int value
print(search(sample,int))