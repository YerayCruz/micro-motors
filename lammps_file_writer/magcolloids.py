import numpy as np
def magcolloids_data(n_of_particles, packing = 0.3, height = 4, radius=1.4):
    """ 
    This function returns an array of initial positions for confined particles, and
    a region where these particles are enclosed with a packing fraction "packing"
    The particles are initially set in a square array, as far from each other as possible.
    """
    part_in_edge = int(np.round(np.sqrt(n_of_particles)))
    n_of_particles = part_in_edge**2

    area_particle = n_of_particles*radius**2*np.pi
    area_region = area_particle/packing

    length_region = np.sqrt(area_region)
    part_separation = length_region/part_in_edge
    
    x_loc = np.linspace(
        -length_region/2+part_separation/2,
        length_region/2-part_separation/2,part_in_edge)
    y_loc = np.linspace(
        -length_region/2+part_separation/2,
        length_region/2-part_separation/2,part_in_edge)

    [X,Y] = np.meshgrid(x_loc,y_loc)
    Z = np.zeros(np.shape(X))

    initial_positions = np.array([[x,y,z] for (x,y,z) in zip(X.flatten(),Y.flatten(),Z.flatten())])
    
    if part_separation<2*radius:
        raise ValueError("packing is too high")

    region = [np.round(length_region),np.round(length_region),height]
    return region, initial_positions