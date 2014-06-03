import os
import shutil
import traceback
import multiprocessing
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.reflection import GeneratedProtocolMessageType
from distributions.io.stream import protobuf_stream_write, protobuf_stream_read


def mkdir_p(dirname):
    'like mkdir -p'
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def rm_rf(dirname):
    'like rm -rf'
    if os.path.exists(dirname):
        shutil.rmtree(dirname)


def print_trace((fun, arg)):
    try:
        return fun(arg)
    except Exception, e:
        print e
        traceback.print_exc()
        raise


POOL = None


def parallel_map(fun, args):
    if not isinstance(args, list):
        args = list(args)
    THREADS = int(os.environ.get('THREADS', multiprocessing.cpu_count()))
    if THREADS == 1 or len(args) < 2:
        print 'Running {} in this thread'.format(fun.__name__)
        return map(fun, args)
    else:
        print 'Running {} in {:d} threads'.format(fun.__name__, THREADS)
        global POOL
        if POOL is None:
            POOL = multiprocessing.Pool(THREADS)
        fun_args = [(fun, arg) for arg in args]
        return POOL.map(print_trace, fun_args, chunksize=1)


def protobuf_to_dict(message):
    assert message.IsInitialized()
    raw = {}
    for field in message.DESCRIPTOR.fields:
        value = getattr(message, field.name)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            if field.type == FieldDescriptor.TYPE_MESSAGE:
                value = map(protobuf_to_dict, value)
            else:
                value = list(value)
            if len(value) == 0:
                value = None
        else:
            if field.type == FieldDescriptor.TYPE_MESSAGE:
                if value.IsInitialized():
                    value = protobuf_to_dict(value)
                else:
                    value = None
        if value is not None:
            raw[field.name] = value
    return raw


def dict_to_protobuf(raw, message):
    assert isinstance(raw, dict)
    for key, raw_value in raw.iteritems():
        if isinstance(raw_value, dict):
            value = getattr(message, key)
            dict_to_protobuf(raw_value, value)
        elif isinstance(raw_value, list):
            value = getattr(message, key)
            list_to_protobuf(raw_value, value)
        else:
            setattr(message, key, raw_value)


def list_to_protobuf(raw, message):
    assert isinstance(raw, list)
    if raw:
        if isinstance(raw[0], dict):
            for value in raw:
                dict_to_protobuf(value, message.add())
        elif isinstance(raw[0], list):
            for value in raw:
                list_to_protobuf(value, message.add())
        else:
            message[:] = raw


def protobuf_server(fun, Query, Result):
    assert isinstance(Query, GeneratedProtocolMessageType), Query
    assert isinstance(Result, GeneratedProtocolMessageType), Result

    class Server(object):
        def __init__(self, *args, **kwargs):
            kwargs['block'] = False
            self.proc = fun(*args, **kwargs)

        def call_string(self, query_string):
            protobuf_stream_write(query_string, self.proc.stdin)
            return protobuf_stream_read(self.proc.stdout)

        def call_protobuf(self, query):
            assert isinstance(query, Query)
            query_string = query.SerializeToString()
            result_string = self.call_string(query_string)
            result = Result()
            result.ParseFromString(result_string)
            return result

        def call_dict(self, query_dict):
            query = Query()
            dict_to_protobuf(query_dict, query)
            result = self.call_protobuf(query)
            return protobuf_to_dict(result)

        __call__ = call_protobuf

        def close(self):
            self.proc.stdin.close()
            self.proc.wait()

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()

    Server.__name__ = fun.__name__.capitalize() + 'Server'
    return Server


def protobuf_serving(Query, Result):

    def decorator(fun):
        fun.serve = protobuf_server(fun, Query, Result)
        return fun

    return decorator