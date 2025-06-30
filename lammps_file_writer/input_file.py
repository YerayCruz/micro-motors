def input_file_data(dir, input_file_name, mag_file_name, ratch_file_name, void_radius, mag_r, ratch_r, 
                    c_eps, cr_eps, field, seed, run):
    """
    Write a LAMMPS data file for the the whole system of ratchet and magnetic colloids.
    - Type 1: These are the magnetic colloids.
    - Type 2: These are the particles of the ratchet.

    """
    Bmag = field["H_magnitude"].magnitude
    freq = field["frequency"].magnitude
    theta = field["angle"].magnitude
    phi = field["phase"].magnitude

    with open(dir + input_file_name, 'w') as f:
        f.write("### ---preamble--- ###\n")
        f.write(f"log {input_file_name.split('.')[0]}.log\n")
        f.write("units micro\n")
        f.write("atom_style hybrid sphere paramagnet bond\n")
        f.write("boundary p p f\n\n")

        f.write("neighbor 2.0 nsq\n")
        f.write("pair_style lj/cut/dipole/cut 20\n")
        f.write("bond_style harmonic\n\n")

        f.write("### ---Create particle and Region--- ###\n")
        f.write(f"read_data {mag_file_name} extra/atom/types 1 extra/bond/types 2 extra/bond/per/atom 10\n")
        f.write(f"mass 1 1\n")
        f.write(f"mass 2 1\n\n")

        f.write(f"region void cylinder z 0 0 {void_radius} EDGE EDGE\n")
        f.write("delete_atoms region void\n\n")

        f.write(f"read_data {ratch_file_name} add append offset 1 0 0 0 0\n\n")

        f.write(f"pair_coeff 1 1 {c_eps} {(mag_r + mag_r)} {(mag_r + mag_r) * 2 ** (1/6)} 20.0\n") ##c_eps stands for colloid epsilon The value of the cuttof is give by multliplying the radius of the particle by 2 ** (1/6)
        f.write(f"pair_coeff 1 2 {cr_eps} {mag_r + ratch_r} {(mag_r + ratch_r) * 2 ** (1/6)} 1.0\n\n") ##cr_eps stands for colloids_ratchet_epsilin
        f.write(f"pair_coeff 2 2 0 0 0 0\n\n")

        f.write(f"group Atoms type 1\n")
        f.write(f"group Ratchet type 2\n")
        f.write(f"group System type 1 2\n\n")
        ### ---Variables--- ###
        ## magnetic field
        f.write(f"variable Bmag atom {Bmag}\n")
        f.write(f"variable freq atom {freq}\n")
        f.write(f"variable theta atom {theta}\n")
        f.write(f"variable phi atom {phi}\n\n")

        f.write(f"variable fieldx atom v_Bmag*sin(v_freq*time*2*PI)*sin(v_theta)\n")
        f.write(f"variable fieldy atom v_Bmag*cos(v_freq*time*2*PI)*sin(v_theta)\n")
        f.write(f"variable fieldz atom v_Bmag*cos(v_theta)\n\n")

        f.write(f"fix 1 Atoms setdipole v_fieldx v_fieldy v_fieldz 0\n")
        f.write(f"fix 2 System bd 300 0.001 {seed}\n\n")

        f.write(f"fix 3 System addforce 0 0 -0.00011264159515495175\n")
        f.write(f"fix 4 Atoms wall/lj126 zlo EDGE {c_eps} {(mag_r)} {(mag_r) * 2 ** (1/6)} zhi EDGE {c_eps} {(mag_r)} {(mag_r) * 2 ** (1/6)}\n")
        f.write(f"fix 5 Ratchet wall/lj126 zlo EDGE {c_eps} {(ratch_r)} {(ratch_r) * 2 ** (1/6)} zhi EDGE {c_eps} {ratch_r} {(ratch_r) * 2 ** (1/6)}\n\n")

        f.write(f"### ---Run Commands--- ###\n")
        f.write(f"timestep 10.0\n")
        f.write(f"dump 1 all custom 1000 {input_file_name.split('.lmpin')[0]}.lammpstrj id type x y z\n")
        f.write(f"thermo_style custom step atoms\n")
        f.write(f"thermo 100\n")
        f.write(f"run {run}")



