from enum import Enum, EnumMeta


class GetItemEnumMeta(EnumMeta):
    def __getitem__(cls, name):
        """
        We override the _getitem_ mecanism in order to have the same result than the
        instantiation method, because some libraries (such as 'dict_to_dataclass')
        are using the getitem approach.

        E.g: AssetClass['spot'] == AssetClass('spot')
        """
        item = cls._missing_(name)
        if item is None:
            return super().__getitem__(name)
        return item


class BaseEnum(Enum, metaclass=GetItemEnumMeta):
    @property
    def ordinal(self):
        return list(self.__class__).index(self) + 1

    @classmethod
    def choices(cls):
        return [(item.value, f"{item.name}") for item in cls]

    @classmethod
    def hidden_values_choices(cls):
        return [(item.value, f"{item.value}") for item in cls]

    @classmethod
    def name_values(cls):
        return [(item.name, f"{item.value}") for item in cls]

    @classmethod
    def values(cls):
        return [item.value for item in cls]

    @classmethod
    def items(cls):
        return (item for item in cls)

    @classmethod
    def ordinals(cls):
        return (item.ordinal for item in cls)

    @classmethod
    def ordinal_choices(cls):
        return [(item.ordinal, item.value) for item in cls]

    @classmethod
    def get(cls, index):
        return list(cls)[index - 1]

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            # Case insensitive string
            if isinstance(value, str) and member.value == value.lower():
                return member
            # Ordinal
            if isinstance(value, int) or isinstance(value, str) and value.isnumeric():
                if member.ordinal == int(value):
                    return member

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.ordinal
