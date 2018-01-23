from scipy import constants, math

from .comp_factor import CompFactorInterpolator


class cached_property:
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res

    @staticmethod
    def invalidate_cache(instance):
        for property_name in dir(instance):
            if isinstance(getattr(instance, property_name), cached_property):
                instance.__dict__.pop(property_name, None)


class PropertySet:
    def __init__(self, z_calculator=None):
        self.z_calculator = z_calculator if z_calculator is not None else CompFactorInterpolator()
        self.P = 1   # unit is pa
        self.T = 0   # unit is kelvin
        self.M = 16  # unit is g/mol

    def __set__(self, instance, value):
        self.__dict__[instance] = value
        cached_property.invalidate_cache(self)

    @cached_property
    def Z(self):
        # in the given correlation p is in bar gauge and T is in centigrade but in our model every thing is in SI
        return self.z_calculator.get_z(self.P / 10 ** 5, self.T - 273.15)

    @cached_property
    def dz_dp(self):
        # in the given correlation p is in bar gauge and T is in centigrade but in our model every thing is in SI
        return self.z_calculator.get_z(self.P / 10 ** 5, self.T - 273.15, dp=True) / 10**5

    @cached_property
    def dz_dt(self):
        # in the given correlation p is in bar gauge and T is in centigrade but in our model every thing is in SI
        return self.z_calculator.get_z(self.P / 10 ** 5, self.T - 273.15, dt=True)

    @cached_property
    def c_p(self):
        # TODO: add specific heat from correlation.
        return 2314

    @cached_property
    def v_w(self):
        return math.sqrt(
            self.Z * constants.R * self.T / self.M /
            (1 - self.P / self.Z * self.dz_dp - self.P / (self.ro * self.c_p * self.T) * (1 + self.T / self.Z * self.dz_dt)**2)
        )