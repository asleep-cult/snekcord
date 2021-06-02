__all__ = ('Bitset',)


class Bitset:
    def __init__(self, value=None):
        if value is not None:
            self.value = value
        else:
            self.value = 0

    def _noamalize_indice(self, indice):
        if not isinstance(indice, int):
            raise TypeError(f'{self.__class__.__name__} indices must be '
                            f'integers, got {indice.__class__.__name__}')

        bit_length = self.value.bit_length()
        indice = bit_length * (indice < 0) - indice - 1

        if 0 > indice or indice >= bit_length:
            raise IndexError(f'{self.__class__.__name__} index out of range')

        return indice

    def __index__(self):
        return self.value

    def __len__(self):
        return self.value.bit_length()

    def __getitem__(self, position):
        return (self.value >> self._noamalize_indice(position)) & 1

    def __setitem__(self, position):
        self.value |= (1 << self._noamalize_indice(position))

    def __delitem__(self, position):
        self.value &= ~(self._noamalize_indice(position))
