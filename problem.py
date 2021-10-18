from ufl import *

degree = 4
family = "Lagrange"
cell_type = tetrahedron
element = FiniteElement(family, cell_type, degree)
coord_element = VectorElement("Lagrange", cell_type, 1)
mesh = Mesh(coord_element)
V = FunctionSpace(mesh, element)
u = TrialFunction(V)
v = TestFunction(V)

W = FunctionSpace(mesh, FiniteElement(family, cell_type, 1))
k = Coefficient(W)

a = k*inner(grad(u), grad(v))*dx