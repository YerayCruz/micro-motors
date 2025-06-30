import numpy as np
from scipy.spatial import Delaunay
import itertools

def generate_lattice(a, nx, ny, nz, circle_radius):
    """
    Generate a cubic lattice with a centered particle in each unit cell, excluding particles within a circle in the middle.
    
    Parameters:
        a (float): Lattice constant.
        nx, ny, nz (int): Number of unit cells in each direction.
        circle_radius (float): Radius of the circle in the middle where particles are excluded.
    
    Returns:
        np.ndarray: Array of lattice points.
    """
    # Define lattice vectors
    a1 = np.array([a, 0, 0])  # x vector
    a2 = np.array([0, a, 0])  # y vector
    a3 = np.array([0, 0, a])  # z vector
    
    # Position of centered particle
    reference = np.array([a / 2, a / 2, a / 2])
    
    # Calculate the center of the lattice
    center = np.array([nx * a / 2, ny * a / 2, nz * a / 2])
    
    # Generate lattice points
    positions = []
    ranges = [
        range(-nx + 1, nx) if nx >= 2 else range(-nx, nx + 1),
        range(-ny + 1, ny) if ny >= 2 else range(-ny, ny + 1),
        range(nz) if nz >= 2 else range(nz)
    ]
    
    for i, j, k in itertools.product(*ranges):
        base_pos = i * a1 + j * a2 + k * a3

        # Calculate the distance from the center
        distance_from_center = np.linalg.norm(base_pos - [0.0,0.0, 0.0])#center)
        
        # Exclude particles within the circle radius
        if distance_from_center >= circle_radius:
            positions.append(base_pos - [0.0, 0.0, a * (nz - 1) / 2])
            
            # Add the centered particle
            if i < max(ranges[0]) and j < max(ranges[1]) and k < max(ranges[2]):
                centered_pos = base_pos + reference
                if np.linalg.norm(centered_pos - center) > circle_radius:
                    positions.append(centered_pos - [0.0, 0.0, a * (nz - 1) / 2])

    
    return np.array(positions)


def apply_ratchet_boundary(positions, radius, saw_amp, saw_freq, N, specular):
    """
    Filter lattice points to retain only those within a ratchet-like boundary.
    
    Parameters:
        positions (np.ndarray): Array of lattice points.
        radius (float): Average radius of the ratchet.
        saw_amp (float): Amplitude of the sawtooth modulation.
        saw_freq (int): Frequency of the sawtooth pattern.
        N (int): Number of points for the ratchet boundary.
    
    Returns:
        np.ndarray: Filtered lattice points.
    """
    center = np.array([0.0, 0.0, 0.0])
    filtered_positions = []
    
    for pos in positions:
        angle = np.arctan2(pos[1], pos[0])
        if angle < 0:
            angle += 2 * np.pi  # Normalize angle to [0, 2π]
        
        # Calculate the sawtooth-modulated radius

        if not specular:
            
            sawtooth_mod = saw_amp * (1 - ((angle * N / (2 * np.pi)) % (N // saw_freq)) / (N // saw_freq)) ## with no specular rotation

        else:
            
            sawtooth_mod = saw_amp * ((angle * N / (2 * np.pi)) % (N // saw_freq)) / (N // saw_freq) ## with specular rotation
            
        R_mod = radius + sawtooth_mod - (saw_amp / 2)  # Offset to center sawtooth
        
        # Check if the point is within the boundary
        distance_from_center = np.linalg.norm(pos[:2] - center[:2])
        if distance_from_center <= R_mod:
            filtered_positions.append(pos)
    
    return np.array(filtered_positions)

def create_bonds(positions, a):
    """
    Create bonds between lattice points using Delaunay triangulation.
    
    Parameters:
        positions (np.ndarray): Array of lattice points.
        a (float): Lattice constant (maximum bond length).
    
    Returns:
        np.ndarray: Array of bonds (pairs of indices).
    """
    # Perform Delaunay triangulation
    tri = Delaunay(positions)
    
    # Extract edges from the Delaunay triangulation
    edges = set()
    for simplex in tri.simplices:
        for i in range(4):
            for j in range(i + 1, 4):
                edge = tuple(sorted((simplex[i], simplex[j])))
                edges.add(edge)
    
    # Filter edges to retain only those with length <= a
    bonds = []
    for edge in edges:
        p1, p2 = positions[edge[0]], positions[edge[1]]
        distance = np.linalg.norm(p1 - p2)
        if distance <= a * 1.1:  # Slightly larger than `a` to account for numerical precision
            bonds.append(edge)
    
    return np.array(bonds)

def read_timesteps(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    timesteps = {}
    i = 0
    while i < len(lines):
        if lines[i].startswith("ITEM: TIMESTEP"):
            timestep = int(lines[i+1].strip())
            i += 2
        elif lines[i].startswith("ITEM: NUMBER OF ATOMS"):
            num_atoms = int(lines[i+1].strip())
            i += 2
        elif lines[i].startswith("ITEM: BOX BOUNDS"):
            i += 4  # Skip the box bounds lines
        elif lines[i].startswith("ITEM: ATOMS"):
            i += 1
            atoms = []
            for _ in range(num_atoms):
                data = lines[i].strip().split()
                id, type, x, y = int(data[0]), int(data[1]), float(data[2]), float(data[3])
                atoms.append((id, type, x, y))
                i += 1
            timesteps[timestep] = np.array(atoms)
        else:
            i += 1
    
    return timesteps

def read_seeds(filename):
    seeds = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            seeds.append(lines[i].strip())
            i += 1

        return seeds