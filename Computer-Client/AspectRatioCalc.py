from math import *
Ha = 16
Va = 9
Diagonal_FOV = 68.5

Da = sqrt(Ha*Ha + Va*Va)

Df = radians(Diagonal_FOV)
Hf = atan(tan(Df/2) * (Ha/Da)) * 2
Vf = atan(tan(Df/2) * (Va/Da)) * 2

print(f"Horizontal FOV: {Hf}, Vertical FOV: {Vf}")

