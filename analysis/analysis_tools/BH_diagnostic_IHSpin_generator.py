import sys
import os
import numpy as np
import glob
import shutil
def write_to_BH_diagnostic_IHSpin(run_dir_full, simulation_type):
    os.chdir(run_dir_full)
    print("Write to BH_diagnostics and IH_Spin files...")
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
                stored_files_dir       = output_dir + "/" + parfile_name
                BH_diagnostics_filename_0 = stored_files_dir + "/BH_diagnostics.ah1.gp"
                BH_diagnostics_filename_1 = stored_files_dir + "/BH_diagnostics.ah2.gp"

                IHSpin_filename_0 = stored_files_dir + "/ihspin_hn_0.asc"
                IHSpin_filename_1 = stored_files_dir + "/ihspin_hn_1.asc"
                if(simulation_type == "NSBH"):
                    # Check if BH_diagnostics_filename_0 exists and copy it to BH_diagnostics_filename_1
                    if os.path.exists(BH_diagnostics_filename_0):
                        shutil.copy(BH_diagnostics_filename_0, BH_diagnostics_filename_1)
                        print(f"Copied {BH_diagnostics_filename_0} to {BH_diagnostics_filename_1}")
                    if os.path.exists(IHSpin_filename_0):
                        shutil.copy(IHSpin_filename_0, IHSpin_filename_1)
                        print(f"Copied {IHSpin_filename_0} to {IHSpin_filename_1}") 