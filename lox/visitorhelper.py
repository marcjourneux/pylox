#
#  Visitor helper functions to mimic interface implementation
#


def _qualname(obj):
    """Get the fully-qualified name of an object (including module)."""
    return obj.__module__ + '.' + obj.__qualname__


def _declaring_class(obj):
    """Get the name of the class that declared an object."""
    name = _qualname(obj)
    return name[:name.rfind('.')]


# Mapping table between class and visitor method
_methods = {}

# Returning the method based on the class of the visitor and the visited object


def _visitor_impl(self, arg):
    """Actual visitor method implementation."""
    # let's return the correct visit method based on visitor and visited class
    if (_qualname(type(self)), type(arg)) in _methods:
        # we have the right key (visitor class, item class)
        method = _methods[(_qualname(type(self)), type(arg))]
    else:
        # we search through visitor hierarchy first as visitor has priority over item
        t = type(self)
        while t is not object and not ((_qualname(t), type(arg)) in _methods):
            t = t.__bases__[0]
        if (t is not object):
            method = _methods[(_qualname(t), type(arg))]
        else:
            raise ValueError("No visitor is implementing visit method for {0}, {1}".format(
                type(self), type(arg)))
    return method(self, arg)
#
# The actual @visitor decorator
#


def visitor(arg_type):
    """Decorator that creates a visitor method."""
    # The decorator is ran at start time, this creates the mapping table
    def decorator(fn):
        # this the class of the visitor declaring the visit method
        declaring_class = _declaring_class(fn)
        # associate this method with the declaring class
        _methods[(declaring_class, arg_type)] = fn
        # Replace all decorated methods with _visitor_impl
        return _visitor_impl

    return decorator
