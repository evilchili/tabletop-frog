from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass
class AttributeMap(Mapping):
    """
    AttributeMap is a data class that is also a mapping, converting a dict
    into an object with attributes. Example:

        >>> amap = AttributeMap(attributes={'foo': True, 'bar': False})
        >>> amap.foo
        True
        >>> amap.bar
        False

    Instantiating an AttributeMap using the from_dict() class method will
    recursively transform dictionary members sinto AttributeMaps:

        >>> nested_dict = {'foo': {'bar': {'baz': True}, 'boz': False}}
        >>> amap = AttributeMap.from_dict(nested_dict)
        >>> amap.foo.bar.baz
        True
        >>> amap.foo.boz
        False

    The dictionary can be accessed directly via 'attributes':

        >>> amap = AttributeMap(attributes={'foo': True, 'bar': False})
        >>> list(amap.attributes.keys()):
        >>>['foo', 'bar']

    Because AttributeMap is a mapping, you can use it anywhere you would use
    a regular mapping, like a dict:

        >>> amap = AttributeMap(attributes={'foo': True, 'bar': False})
        >>> 'foo' in amap
        True
        >>> "{foo}, {bar}".format(**amap)
        True, False


    """
    attributes: field(default_factory=dict)

    def __getattr__(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]
        return self.__getattribute__(attr)

    def __len__(self):
        return len(self.attributes)

    def __getitem__(self, key):
        return self.attributes[key]

    def __iter__(self):
        return iter(self.attributes)

    @classmethod
    def from_dict(cls, kwargs: dict):
        """
        Create a new AttributeMap object using keyword arguments. Dicts are
        recursively converted to AttributeMap objects; everything else is
        passed as-is.
        """
        attrs = {}
        for k, v in sorted(kwargs.items()):
            attrs[k] = AttributeMap.from_dict(v) if type(v) is dict else v
        return cls(attributes=attrs)
