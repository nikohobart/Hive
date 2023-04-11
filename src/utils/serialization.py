import cloudpickle

def serialize(object):
    return cloudpickle.dumps(object)

def deserialize(object):
    return cloudpickle.loads(object)