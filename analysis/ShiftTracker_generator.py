def write_to_ShiftTracker(run_dir_full, simulation_type):
#     VolumeIntegrals_out_every, ShiftTracker_out_every    = out_every_tuple
    import sys
    import os
    import numpy as np
    import glob

    def strlist_to_numarray(strlist):
        numlist = []
        for elem in strlist:
            numlist.append(float(elem))
        numarr = np.array(numlist)
        return numarr



    ## Write shifttracker python file
    os.chdir(run_dir_full)
    print("Write to ShiftTracker ...")
    raw_directory = run_dir_full
    print("Current working directory" , os.getcwd())
    output_directories = glob.glob(
        os.path.join(raw_directory, "output-[0-9][0-9][0-9][0-9]"))
    output_directories.sort()
    for output_dir in output_directories:
        for file in os.listdir(output_dir):
            if(".par" in file):
                parfile = file
                parfile_name = parfile[:-4]
                #output_dir = output_x_dir_full + "/" + parfile[:-4] + "/"
                stored_files_dir       = output_dir + "/" + parfile_name
                volint_filename        = stored_files_dir + "/volume_integrals-GRMHD.asc"
                shiftTracker0_filename = stored_files_dir + "/ShiftTracker0.asc"

        if(simulation_type == "NSBH"):
            ## get data from volume integral (NS)
            with open(volint_filename,'r') as volint_file:
                volint_data = np.genfromtxt(volint_filename)
            t_vol  = volint_data[:,0]
            m_ns   = volint_data[:,4] * 2 #rest mass multiply by 2 for symmetry
            pos_ns  = volint_data[:,1:4] / (m_ns[:,np.newaxis]/2)
            
            # get data from shiftTracker0 (BH)
            with open(shiftTracker0_filename,'r') as shiftTracker0_file:
                shift0_data = np.genfromtxt(shiftTracker0_filename)
            itt_shi  = np.array(shift0_data[:,0],dtype = int)
            t_shi    = np.array(shift0_data[:,1],dtype = float)
            ## somehow for neutron star you need to add itt = 0
            if(itt_shi[0] == 1):
                itt_shi  = np.concatenate((np.array([0],dtype = int),itt_shi))
                t_shi    = np.concatenate((np.array([0.0]),t_shi))
            pos_shi  = np.zeros((len(t_shi),3))
            
            from scipy.interpolate import CubicSpline
            for j in range(3):
                pos_shi[:,j] = CubicSpline(t_vol,pos_ns[:,j])(t_shi)
            
            with open(stored_files_dir + "/ShiftTracker1.asc","w+") as ShiftTracker_outfile:
                header1 = "# ShiftTracker1.asc: \n# itt   time    x       y       z       vx      vy      vz      ax      ay      az \n#======================================================================= \n"
                ShiftTracker_outfile.write(header1)
                for line_idx in range(len(itt_shi)):
                    #itt_0 = itt_0 + ShiftTracker_out_every
                    line = "{: <9}\t{:9f}\t".format(itt_shi[line_idx], t_shi[line_idx])
                    for j in range(3):
                        line = line+"{:9e}\t".format(pos_shi[line_idx,j])
                    for j in range(6):
                        line = line+"{:9e}\t".format(0.0)
                    line = line + "\n"
                    ShiftTracker_outfile.write(line)
                print(stored_files_dir + ("/ShiftTracker1.asc stores %d lines" % len(t_vol)))
 
        elif(simulation_type == "BNS"):
            ## get data from volume integral
            with open(volint_filename,'r') as volint_file:
                volint_data = np.genfromtxt(volint_filename)
            t_vol  = volint_data[:,0]
            m0_1   = volint_data[:,4] * 2 #rest mass multiply by 2 for symmetry
            m0_2   = volint_data[:,8] * 2 #rest mass
            pos_1  = volint_data[:,1:4] / (m0_1[:,np.newaxis]/2)
            pos_2  = volint_data[:,5:8] / (m0_2[:,np.newaxis]/2)
            itt_arr = np.arange(len(t_vol))

            ## write to ShiftTracker
            header1 = "# ShiftTracker0.asc: \n# itt   time    x       y       z       vx      vy      vz      ax      ay      az \n#======================================================================= \n"
            header2 = "# ShiftTracker1.asc: \n# itt   time    x       y       z       vx      vy      vz      ax      ay      az \n#======================================================================= \n"
            with open(stored_files_dir + "/ShiftTracker0.asc","w+") as ShiftTracker_outfile:
                ShiftTracker_outfile.write(header1)
                for line_idx in range(len(t_vol)):
                    #itt_0 = itt_0 + ShiftTracker_out_every
                    line = "{: <9}\t{:9f}\t".format(itt_arr[line_idx], t_vol[line_idx])
                    for j in range(3):
                        line = line+"{:9e}\t".format(pos_1[line_idx,j])
                    for j in range(6):
                        line = line+"{:9e}\t".format(0.0)
                    line = line + "\n"
                    ShiftTracker_outfile.write(line)
                print(stored_files_dir + ("/ShiftTracker0.asc stores %d lines" % len(t_vol)))
            with open(stored_files_dir + "/ShiftTracker1.asc","w+") as ShiftTracker_outfile:
                ShiftTracker_outfile.write(header2)
                for line_idx in range(len(t_vol)):
                    #itt_1 = itt_1 + ShiftTracker_out_every
                    line = "{: <9}\t{:9f}\t".format(itt_arr[line_idx], t_vol[line_idx])
                    for j in range(3):
                        line = line+"{:9e}\t".format(pos_2[line_idx,j])
                    for j in range(6):
                        line = line+"{:9e}\t".format(0.0)
                    line = line + "\n"
                    ShiftTracker_outfile.write(line)
                print(stored_files_dir + ("/ShiftTracker1.asc stores %d lines" % len(t_vol)))
        else:
            print("Wrong simulation type")

