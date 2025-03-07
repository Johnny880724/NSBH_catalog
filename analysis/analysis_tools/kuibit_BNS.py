import numpy as np
from kuibit import simdir as sd
from kuibit import grid_data as gd
from kuibit import grid_data_utils as gdu
from kuibit import series
import matplotlib.pyplot as plt
import kuibit.visualize_matplotlib as viz
import sys, os, shutil

def get_output_dir(sim_dir, run_dir_list):
    output_dir_list, run_name_list = [], []
    for run_dir in run_dir_list:
        run_dir_full = sim_dir + run_dir
        run_name = run_dir.split("/")[-1]
        print(run_name)
        run_name_list.append(run_name)
        output_dir_it = []
        for root, subdirs, files in os.walk(run_dir_full):
            for subdir in subdirs:
                if(("output" in subdir) and ("active" not in subdir)):
                    output_dir_it.append(subdir)
            break
        output_x_dir = run_dir_full+"/" + output_dir_it[0]
        for file in os.listdir(output_x_dir):
            if(".par" in file):
                parfile = file
                output_dir = output_x_dir + "/" + parfile[:-4] + "/"
        output_dir_list.append(output_dir)
    return output_dir_list

def strlist_to_numarray(strlist):
    numlist = []
    for elem in strlist:
        numlist.append(float(elem))
    numarr = np.array(numlist)
    return numarr

# TODO: make EJP file all the way to. last iteration (it is first iteration now)
def read_EJP_file(filename):
    EJP_file = open(filename,'r')
    lines = [line for line in EJP_file]
    EJP = []
    rdet = ""
    for line in lines[4:]:
        nums = line.split("\t")
        #print(lines[1])
        EJP.append(strlist_to_numarray(nums))
        rdet = lines[1]
        #print(EJP)
    EJP = np.array(EJP)
    return rdet, EJP

def read_vol_int_file(filename):
    volint_file = open(filename,'r')
    lines = [line for line in volint_file]
    vol_col = {}
    volint_data = []
    for line in lines:
        if(line[0] == "#"):
            elem = line.split(" ")
            vol_col[elem[2][:-1]] = elem[3]
        else:
            volint_data.append(strlist_to_numarray(line.split(" ")))

    volint_data = np.array(volint_data)

    print(vol_col)
    print(volint_data.shape)
    return volint_data

zero_vec = np.zeros(3)
class BNS_sim:
    def __init__(self, run_dir):
        self.sim = sd.SimDir(run_dir)
        self.timeseries = self.sim.ts

    def get_ID_from_out(self,out_filename):
        with open(out_filename,'r') as outfile:
            for line in outfile:
                ADM_mass_TP = "INFO (TwoPuncturesSolver): non-puncture ADM mass is"
                if(ADM_mass_TP in line):
                    self.ID_M_ADM = float(line.split(ADM_mass_TP)[-1])
                    break
                else:
                    self.ID_M_ADM = -1

    def get_rho_xy(self, it_norm=1,shape_ = [100,100], x0_ = [-50,-50], x1_=[50,50]):
        self.rho = self.sim.gf.xy["rho"]
        rho_xy_it_avail = self.rho.available_iterations
        it_last, avail_len = rho_xy_it_avail[-1], len(rho_xy_it_avail)-1
        it = rho_xy_it_avail[int(it_norm*avail_len)]
        rho_xy = self.rho[it]
        # if no symmetry
        rho_xy_unif = rho_xy.to_UniformGridData(shape=shape_, x0=x0_, x1=x1_, resample=True)
        # if symmetry
        #rho_xy_unif = rho_xy.to_UniformGridData(shape=[100, 100], x0=[0,-50], x1=[50, 50], resample=True)
        return rho_xy_unif


    def plot_rho_xy(self, it_norm=1):
        self.rho = self.sim.gf.xy["rho"]
        rho_xy_it_avail = self.rho.available_iterations
        it_last, avail_len = rho_xy_it_avail[-1], len(rho_xy_it_avail)-1
        it = rho_xy_it_avail[int(it_norm*avail_len)]
        rho_xy = self.rho[it]
        # if no symmetry
        rho_xy_unif = rho_xy.to_UniformGridData(shape=[100, 100], x0=[-50,-50], x1=[50, 50], resample=True)
        # if symmetry
        #rho_xy_unif = rho_xy.to_UniformGridData(shape=[100, 100], x0=[0,-50], x1=[50, 50], resample=True)
        plt.figure()
        plt_rho = viz.plot_color(rho_xy_unif,logscale=True,colorbar=True,label="rho",xlabel="x",ylabel="y",)
        return plt_rho

    def get_rho_max(self):
        self.rho_max = self.timeseries.maximum['rho']
        #plt.figure()
#         rho_plot = plt.plot(self.rho_max)
#         plt.xlabel("time (M)")
#         plt.ylabel(r"$\rho_{max}$")
#         return rho_plot


    def getVolumeIntegral(self, volint_filename):
        volint_data = read_vol_int_file(volint_filename)
        self.t_vol  = volint_data[:,0]
        self.pos_1  = volint_data[:,1:4]
        self.pos_2  = volint_data[:,5:8]
        self.m0_1   = volint_data[:,4] * 2 #rest mass multiply by 2 for symmetry
        self.m0_2   = volint_data[:,8] * 2 #rest mass

    def getADM_EJP(self, output_dir, det_num):

        self.t_ejp_arr  = []
        self.E_ejp_arr  = []
        self.P_ejp_arr  = []
        self.J_ejp_arr  = []
        self.rad_ejp    = []

        adm_ejp_filenames = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if "adm_ejp_det" in file:
                    adm_ejp_filename = output_dir + "/" + file
                    adm_ejp_filenames.append(adm_ejp_filename)
        det_num = len(adm_ejp_filenames)
        for adm_ejp_filename in adm_ejp_filenames:
            rdet, adm_ejp_data = read_EJP_file(adm_ejp_filename)
            #print(adm_ejp_data)
            self.rad_ejp.append(float((rdet.split('rdet=')[-1]).strip()))
            self.t_ejp_arr.append(adm_ejp_data[:,0]) # t remains the same from different detectors
            self.E_ejp_arr.append(adm_ejp_data[:,1])
            self.P_ejp_arr.append(adm_ejp_data[:,2:5])
            self.J_ejp_arr.append(adm_ejp_data[:,5:8])
        self.t_ejp_arr = np.array(self.t_ejp_arr)
        self.E_ejp_arr = np.array(self.E_ejp_arr)
        self.J_ejp_arr = np.array(self.J_ejp_arr)
        self.P_ejp_arr = np.array(self.P_ejp_arr)

        self.t_ejp     = np.array(self.t_ejp_arr[0])
        self.rad_ejp   = np.array(self.rad_ejp)
        N_ejp          = len(self.t_ejp)

        print("(ADM_EJP) data pulled from %d detectors" % det_num)

        # extrapolation helper function
        def extrapolate_to_inf(rad, val):
            import scipy
            from scipy import interpolate
            x = 1.0/rad
            f = interpolate.interp1d(x, val.flatten(), fill_value='extrapolate')
            return f(0)

        ## TODO: customize this

        self.E_ejp = np.zeros((N_ejp,1))
        self.J_ejp = np.zeros((N_ejp,3))
        self.P_ejp = np.zeros((N_ejp,3))
        for i in range(N_ejp):
            self.E_ejp[i,0] = extrapolate_to_inf(self.rad_ejp, self.E_ejp_arr[:,i])
            for j in range(3):
                self.P_ejp[i,j] = extrapolate_to_inf(self.rad_ejp, self.P_ejp_arr[:,i,j])
                self.J_ejp[i,j] = extrapolate_to_inf(self.rad_ejp, self.J_ejp_arr[:,i,j])


        print("(ADM_EJP) Initial E and Jz: E = %f, Jz = %f" % (self.E_ejp[0,0], self.J_ejp[0,2]))

    def plotTrajectory_xy(self):
        plt.figure(figsize=(5,5))
        plt.plot(self.pos_1[:,0],self.pos_1[:,1])
        plt.plot(self.pos_2[:,0],self.pos_2[:,1])

    def get_psi4_22(self, det_num):
        psi4 = self.sim.gws
        radius = psi4.radii[det_num]
        print(psi4.radii, "choose radius = ", radius)
        psi4_l2m2 = (psi4[radius])[(2,2)]
        print(psi4_l2m2)
        self.psi4 = psi4_l2m2

    def get_psi4(self, det_num, lm_dup):
        psi4 = self.sim.gws
        radius = psi4.radii[det_num]
        l,m = lm_dup
        print(psi4.radii, "choose radius = ", radius)
        psi4_lm = (psi4[radius])[(l,m)]
        print("mode ", l, m, psi4_lm)
        self.psi4 = psi4_lm

    def plot_psi4(self, psi4_option = "real"):
        psi4_t = self.psi4.t
        psi4_real, psi4_imag = np.real(self.psi4.y), np.imag(self.psi4.y)
        plt.figure()
        if(psi4_option == "real"):
            plt.plot(psi4_t, psi4_real)
        elif(psi4_option == "imag"):
            plt.plot(psi4_t, psi4_imag)

    def get_var_init_x(self, var_name, N_uni=100):
        var_xy = self.sim.gf.xy[var_name]
        var_xy_init = var_xy[0]
        var_xy_uni = var_xy_init.to_UniformGridData(shape=[N_uni, N_uni], x0=[-50,-50], x1=[50, 50], resample=True)
        var_x = var_xy_uni[:,int(N_uni/2)]
        return var_x


    def plot_var_xy(self,var_name, it_norm=1):
        self.var = self.sim.gf.xy[var_name]
        var_xy_it_avail = self.var.available_iterations
        it_last, avail_len = var_xy_it_avail[-1], len(var_xy_it_avail)-1
        it = var_xy_it_avail[int(it_norm*avail_len)]
        var_xy = self.var[it]
        # if no symmetry
        var_xy_unif = var_xy.to_UniformGridData(shape=[100, 100], x0=[-50,-50], x1=[50, 50], resample=True)
        # if symmetry
        #rho_xy_unif = rho_xy.to_UniformGridData(shape=[100, 100], x0=[0,-50], x1=[50, 50], resample=True)
        plt.figure()
        plt_var = viz.plot_color(var_xy_unif,logscale=True,colorbar=True,label=var_name,xlabel="x",ylabel="y",)
        return plt_var