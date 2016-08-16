from fits2hdf.unit_conversion import fits_to_units,units_to_fits

a = fits_to_units("DEGREES/DAY")
b = fits_to_units("METERS/SEC")

c = fits_to_units("Y")

print(a)
print(b)
print(units_to_fits(a))
print(units_to_fits(b))
