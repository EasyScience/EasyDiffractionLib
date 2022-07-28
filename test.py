__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


from typing import ClassVar
from easyCore.Objects.Variable import Parameter
from easyCore.Objects.ObjectClasses import BaseObj


class A(BaseObj):
    alpha: ClassVar[Parameter]

    def __init__(self, alpha=None):
        alpha = Parameter('alpha', alpha)
        super().__init__('A', alpha=alpha)

class B(BaseObj):
    a: ClassVar[Parameter]
    b: ClassVar[Parameter]
    c: ClassVar[A]

    def __init__(self, alpha=1, a=2, b=3):
        _a = Parameter('a', a)
        _b = Parameter('b', b)
        _c = A(alpha=alpha)
        super().__init__('B', a=_a, b=_b, c=_c)

    def _update_bases(self, new_base):
        base_class = getattr(self, '__old_class__', self.__class__)
        old_bases = list(self.__class__.__bases__)
        old_bases.remove(base_class)
        self.__class__.__bases__ = (new_base, *old_bases, base_class)

class C:
    pass


if __name__ == '__main__':
    b =B(alpha=2)
    print(B.__bases__)
    print(b.__class__.__bases__)
    b._update_bases(C)
    print(b.__class__.__bases__)
    print(B.__bases__)
    print(issubclass(b.__class__, C))
