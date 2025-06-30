import numpy as np

def ratchet_data(a, Kb, positions, bonds, dir, file_name):
    """
    Write a LAMMPS data file for the lattice, including two bond types:
    - Type 1: Regular bonds with distance `a`.
    - Type 2: Bonds involving the middle particle with a different distance.
    """

    with open(dir + file_name, 'w') as f:
        f.write("#LAMMPS data file for cubic lattice with middle particle bonds\n\n")
        f.write(f"{len(positions)} atoms\n")
        f.write(f"{len(bonds)} bonds\n")
        f.write("1 atom types\n")
        f.write("2 bond types\n")  # Two bond types: regular and middle particle bonds
        
        # Box dimensions
        xlo, xhi = -27.0, 27.0  # x-direction size
        ylo, yhi = -27.0, 27.0  # y-direction size
        zlo, zhi = -2.0, 2.0  # z-direction size (if applicable)

        f.write(f"{xlo} {xhi} xlo xhi\n")
        f.write(f"{ylo} {yhi} ylo yhi\n")
        f.write(f"{zlo} {zhi} zlo zhi\n\n")

        f.write("Masses\n\n")
        f.write("1 1.0\n\n")

        # Bond Coeffs
        f.write("Bond Coeffs\n\n")
        f.write(f"1 {Kb} {a}\n")  # Regular bond coefficient
        f.write(f"2 {Kb} {a * np.sqrt(3) / 2}\n\n")  # Middle particle bond coefficient (example value)
        
        # Atom positions
        f.write("Atoms\n\n")
        for i, pos in enumerate(positions):
            f.write(f"{i + 1} 1 {pos[0]} {pos[1]} {pos[2]} 0 0.1 0.0 0 0 0 0.0 0\n")

        # Bond list
        f.write("\nBonds\n\n")
        for i, bond in enumerate(bonds):
            # Check if the bond involves the middle particle
            # Middle particles are those with positions equal to base_pos + reference
            pos1, pos2 = positions[bond[0]], positions[bond[1]]
            reference = np.array([a / 2, a / 2, a / 2])
            is_middle_bond =  np.linalg.norm(pos1 - pos2) == a * np.sqrt(3) / 2 or np.linalg.norm(pos2 - pos1) == a * np.sqrt(3) / 2#np.allclose(pos1, pos2 - reference) or np.allclose(pos2, pos1 - reference)
            
            # Assign bond type
            bond_type = 2 if is_middle_bond else 1
            f.write(f"{i + 1} {bond_type} {bond[0] + 1} {bond[1] + 1}\n")
