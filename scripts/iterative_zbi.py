#!/usr/bin/python3

import root_numpy as rnp
import numpy as np
import ROOT as r
import copy

### Expected Signal Calculations ###
#Rate for A' -> 2 Dark Pions (Invisible decay)
def rate_2pi(m_Ap,m_pi,m_V,alpha_D):
    coeff = (2*alpha_D/3) * m_Ap
    pow1 = (1-(4*(m_pi)**2/(m_Ap**2)))**(3/2.)
    pow2 = ((m_V**2)/((m_Ap**2)-(m_V**2)))**2
    return coeff * pow1 * pow2

#Rate for A' -> Dark Vector + Dark Pion (Potentially visible to HPS through Dark Vector -> SM decay) 
def rate_Vpi(m_Ap,m_pi,m_V,alpha_D,f_pi,rho,phi):
    x = m_pi/m_Ap
    y = m_V/m_Ap
    pi = 3.14159
    coeff = alpha_D*Tv(rho,phi)/(192*(pi**4))
    return coeff * (m_Ap/m_pi)**2 * (m_V/m_pi)**2 * (m_pi/f_pi)**4 * m_Ap*(Beta(x,y))**(3./2.)

#Branching ratio for A' -> Dark Vector + Dark Pion
def br_Vpi(m_Ap,m_pi,m_V,alpha_D,f_pi,rho,phi):
    rate = rate_Vpi(m_Ap,m_pi,m_V,alpha_D,f_pi,rho,phi) + rate_2pi(m_Ap,m_pi,m_V,alpha_D)
    if(2*m_V < m_Ap): rate = rate_Vpi(m_Ap,m_pi,m_V,alpha_D,f_pi,rho,phi) + rate_2pi(m_Ap,m_pi,m_V,alpha_D) + rate_2V(m_Ap,m_V,alpha_D)
    return rate_Vpi(m_Ap,m_pi,m_V,alpha_D,f_pi,rho,phi)/rate

#Branching ratio for A' -> 2 Dark Vectors 
def br_2V(m_Ap,m_pi,m_V,alpha_D,f_pi,rho,phi):
    if(2*m_V >= m_Ap): return 0.
    rate = rate_Vpi(m_Ap,m_pi,m_V1,alpha_D,f_pi,rho,phi) + rate_2pi(m_Ap,m_pi,m_V1,alpha_D) + rate_2V(m_Ap,m_V1,alpha_D)
    return rate_2V(m_Ap,m_V1,alpha_D)/rate

# There are 3 categories of Dark Vectors, 2 being Neutral Vectors Rho and Phi, the 3rd category comprised of "charged" Vectors
# HPS is only sensitive to the decay of the 2 Neutral Vectors Rho and Phi to SM particles.
# The A' decay rates to these Dark Vector categories have slightly different coefficients, given by 'Tv'
def Tv(rho,phi):
    if rho:
        return 3/4.
    elif phi:
        return 3/2.
    else:
        return 18

def Beta(x,y):
    return (1+y**2-x**2-2*y)*(1+y**2-x**2+2*y)

#Decay rate for A' -> 2 Dark Vectors
def rate_2V(m_Ap,m_V,alpha_D):
    r = m_V/m_Ap
    return alpha_D/6 * m_Ap * f(r)

def f(r):
    num = 1 + 16*r**2 - 68*r**4 - 48*r**6
    den = (1-r**2) ** 2
    return num/den * (1-4*r**2)**0.5

#Rate of Neutral Dark Vector -> Two Leptons
#Rate is different for Rho or Phi 
def rate_2l(m_Ap,m_pi,m_V,eps,alpha_D,f_pi,m_l,rho):
    alpha = 1/137.
    pi = 3.14159
    coeff = 16*pi*alpha_D*alpha*eps**2*f_pi**2/(3*m_V**2)
    term1 = (m_V**2/(m_Ap**2 - m_V**2))**2
    term2 = (1-(4*m_l**2/m_V**2))**0.5
    term3 = 1+(2*m_l**2/m_V**2)
    const = 1
    if rho:
        const = 2
    return coeff * term1 * term2 * term3 * m_V * const

#Lifetime of Neutral Dark Vectors
def getCtau(m_Ap,m_pi,m_V,eps,alpha_D,f_pi,m_l,rho):
    c = 3.00e10 #cm/s
    hbar = 6.58e-22 #MeV*sec
    rate = rate_2l(m_Ap,m_pi,m_V,eps,alpha_D,f_pi,m_l,rho)#MeV
    tau = hbar/rate
    ctau = c*tau
    return ctau

def Vdistribution(z,targZ,gammact):
    return np.exp(targZ/gammact-1/gammact*z)/gammact

#gamma factor used to calculate lifetime of Dark Vectors
def gamma(m_V, E_V):
    gamma = E_V/m_V
    return gamma

### ZBi Calculations ###
def calculate_ZBi(n_on, n_off, tau):
   P_Bi = r.TMath.BetaIncomplete(1./(1.+tau),n_on, n_off+1)
   Z_Bi = sqrt(2)*r.TMath.ErfInverse(1-2*P_Bi)
   return Z_Bi

def getRadFrac(tritrig_InvM_h, wab_InvM_h, rad_mcMass622_h, mV_MeV):
    ##MAKE THIS RATIO CONFIGURABLE
    mAp_GeV = (mV_MeV/1000)*(3/1.8)
    tt = ( tritrig_InvM_h.GetBinContent(tritrig_InvM_h.FindBin(mAp_GeV)) + tritrig_InvM_h.GetBinContent(tritrig_InvM_h.FindBin(mAp_GeV)-1) + tritrig_InvM_h.GetBinContent(tritrig_InvM_h.FindBin(mAp_GeV)+1) )/ 3
    wab = ( wab_InvM_h.GetBinContent(wab_InvM_h.FindBin(mAp_GeV)) + wab_InvM_h.GetBinContent(wab_InvM_h.FindBin(mAp_GeV)-1) + wab_InvM_h.GetBinContent(wab_InvM_h.FindBin(mAp_GeV)+1) )/ 3
    rad = ( rad_mcMass622_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_GeV)) + rad_mcMass622_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_GeV)-1) + rad_mcMass622_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_GeV)+1) )/ 3
    radFrac = rad/(wab+tt)

    return radFrac

def getTotalRadiativeAcceptance(rad_mcMass622_h, rad_slic_mc622Mass_h, mV_MeV):
    mAp_MeV = mV_MeV*(3/1.8)
    rad_slic = ( rad_slic_mc622Mass_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_MeV))  + rad_slic_mc622Mass_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_MeV)-1) + rad_slic_mc622Mass_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_MeV)+1) )/3
    rad = ( rad_mcMass622_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_MeV)) + rad_mcMass622_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_MeV)-1) + rad_mcMass622_h.GetBinContent(rad_mcMass622_h.FindBin(mAp_MeV)+1) )/3
    radAcc = rad/rad_slic

    return radAcc


################### SCRIPT ################################

#input files
mV_MeV = 55
mAp_MeV = mV_MeV*(3/1.8)
sigfile = "/sdf/group/hps/users/alspellm/projects/THESIS/ZBi/signal/hadd_mass_%s_simp_recon_KF_ana.root"%(mV_MeV)
ttfile = "/sdf/group/hps/users/alspellm/projects/THESIS/ZBi/tritrig_beam/full_hadd_tritrigv2-beamv6_2500kBunches_HPS-PhysicsRun2016-Pass2_v4_5_0_pairs1_KF_ana_nvtx1.root"
wabfile = "/sdf/group/hps/users/alspellm/projects/THESIS/ZBi/wab_beam/full_hadd_wabv3-beamv6_2500kBunches_HPS-PhysicsRun2016-Pass2_v4_5_0_pairs1_KF_ana_nvtx1.root"
radfile = "/sdf/group/hps/users/alspellm/projects/THESIS/ZBi/rad_beam/full_hadd_RADv3-beamv6_2500kBunches_HPS-PhysicsRun2016-Pass2_v4_5_0_pairs1_KF_ana_nvtx1.root"
rad_slic_file = "/sdf/group/hps/users/alspellm/projects/THESIS/ZBi/rad_slic/hadd_RADv3_MG5_noXchange_HPS-PhysicsRun2016-Pass2_ana.root"

#MC Bkg Scaling
Lumi =10.7 #pb-1
mcScale = {}
mcScale['tritrig'] = 1.416e9*Lumi/(50000*9853)
mcScale['wab'] = 0.1985e12*Lumi/(100000*9966)
mcScale['rad'] = 66.36e6*Lumi/(10000*9959)
mcScale['rad_slic'] = 66.36e6*Lumi/(10000*9959)

#Select cut variables from flat tuple 
variables = ['unc_vtx_mass', 'unc_vtx_z','true_vtx_z', 'unc_vtx_chi2', 'unc_vtx_psum', 'unc_vtx_ele_track_p', 'unc_vtx_pos_track_p']

#Define 1d histograms for each var
signal_histos = {}
signal_histos['unc_vtx_mass'] = r.TH1F('signal_unc_vtx_mass','signal_unc_vtx_mass', 4000, 0, 4)
signal_histos['unc_vtx_z'] = r.TH1F('signal_unc_vtx_z','signal_unc_vtx_z', 1400, -20, 120)
signal_histos['true_vtx_z'] = r.TH1F('signal_true_vtx_z','signal_true_vtx_z', 1400, -20, 120)
signal_histos['unc_vtx_chi2'] = r.TH1F('signal_unc_vtx_chi2','signal_unc_vtx_chi2', 400, 0, 200)
signal_histos['unc_vtx_psum'] = r.TH1F('signal_unc_vtx_psum','signal_unc_vtx_psum', 500, 0, 5)
signal_histos['unc_vtx_ele_track_p'] = r.TH1F('signal_unc_vtx_ele_track_p','signal_unc_vtx_ele_track_p', 500, 0, 5)
signal_histos['unc_vtx_pos_track_p'] = r.TH1F('signal_unc_vtx_pos_track_p','signal_unc_vtx_pos_track_p', 500, 0, 5)

tritrig_histos = {}
tritrig_histos['unc_vtx_mass'] = r.TH1F('tritrig_unc_vtx_mass','tritrig_unc_vtx_mass', 4000, 0, 4)
tritrig_histos['unc_vtx_z'] = r.TH1F('tritrig_unc_vtx_z','tritrig_unc_vtx_z', 1400, -20, 120)
tritrig_histos['true_vtx_z'] = r.TH1F('tritrig_true_vtx_z','tritrig_true_vtx_z', 1400, -20, 120)
tritrig_histos['unc_vtx_chi2'] = r.TH1F('tritrig_unc_vtx_chi2','tritrig_unc_vtx_chi2', 400, 0, 200)
tritrig_histos['unc_vtx_psum'] = r.TH1F('tritrig_unc_vtx_psum','tritrig_unc_vtx_psum', 500, 0, 5)
tritrig_histos['unc_vtx_ele_track_p'] = r.TH1F('tritrig_unc_vtx_ele_track_p','tritrig_unc_vtx_ele_track_p', 500, 0, 5)
tritrig_histos['unc_vtx_pos_track_p'] = r.TH1F('tritrig_unc_vtx_pos_track_p','tritrig_unc_vtx_pos_track_p', 500, 0, 5)


#Read flat tuple variables and convert to array
tt_tree = 'vtxana_kf_Tight_2016_simp_reach_dev/vtxana_kf_Tight_2016_simp_reach_dev_tree'
sig_tree = 'vtxana_kf_Tight_2016_simp_reach_dev/vtxana_kf_Tight_2016_simp_reach_dev_tree'
wab_tree = 'vtxana_kf_Tight_2016_simp_reach_dev/vtxana_kf_Tight_2016_simp_reach_dev_tree'
sig_arr = rnp.root2array(sigfile,sig_tree, branches= variables, start=0, stop = 50, step = 1)
tt_array = rnp.root2array(ttfile,tt_tree, branches= variables, start=0, stop = 50, step = 1)
wab_array = rnp.root2array(wabfile,wab_tree, branches= variables, start=0, stop = 50, step = 1)

#Fill 1d signal histograms for each variable 
print("Filling 1D signal histograms for variables: ", variables) 
for event in sig_arr:
    print(event)
    for i,var in enumerate(variables):
        signal_histos['%s'%(var)].Fill(event[i])

#Define map to hold cut values for each variable
iter_cut_map = {key: None for key in variables}

#Iterate through histos, independently for each variable, define cut as value where n% of signal is cut
print("Cutting signal for each variable")
for var,hist in signal_histos.items():
    cut_percentage = 0.1
    xmax = hist.FindLastBinAbove(0.0)
    xmin = hist.FindFirstBinAbove(0.0)
    integral = hist.Integral(xmin,xmax)

    #Find var value that cuts percentage of original
    cutval = hist.GetXaxis().GetBinUpEdge(xmax)
    while hist.Integral(xmin,xmax) > integral*(1.0-cut_percentage):
        xmax = xmax - 1
        cutval = hist.GetXaxis().GetBinUpEdge(xmax)
    iter_cut_map[var] = cutval

#calculate the radFrac for the specified A' mass value (m_VD = (1.8/3)*m_A')
print("Making Radiative Fraction")
invMassHistos = {}
vtx_selection = "vtxana_kf_Tight_2016_simp_reach_dev"
inFile = r.TFile(ttfile,"READ")
invMassHistos['tritrig'] = copy.deepcopy(inFile.Get("%s/%s_vtx_InvM_h"%(vtx_selection,vtx_selection)))
inFile.Close()

inFile = r.TFile(wabfile,"READ")
invMassHistos['wab'] = copy.deepcopy(inFile.Get("%s/%s_vtx_InvM_h"%(vtx_selection,vtx_selection)))
inFile.Close()

radmatch_selection = 'vtxana_kf_radMatchTight_2016_simp_reach_dev'
inFile = r.TFile(radfile,"READ")
invMassHistos['rad'] = copy.deepcopy(inFile.Get("%s/%s_mcMass622_h"%(radmatch_selection,radmatch_selection)))
inFile.Close()

slic_selection = 'mcAna'
inFile = r.TFile(rad_slic_file,"READ")
invMassHistos['rad_slic'] = copy.deepcopy(inFile.Get("%s/%s_mc622Mass_h"%(slic_selection,slic_selection)))
print(invMassHistos['rad_slic'].GetEntries())
inFile.Close()

#Scale invMassHistos
invMassHistos['tritrig'].Scale(mcScale['tritrig'])
invMassHistos['wab'].Scale(mcScale['wab'])
invMassHistos['rad'].Scale(mcScale['rad'])
invMassHistos['rad_slic'].Scale(mcScale['rad_slic'])

radFrac = getRadFrac(invMassHistos['tritrig'], invMassHistos['wab'], invMassHistos['rad'], mV_MeV)
print("radFrac: ", radFrac)

#Get TotalRadiativeAcceptance
#Rad+Beam histogram x-axis here needed to be converted from GeV to MeV 
name = invMassHistos['rad'].GetName()
invMassHistos['rad'].SetName("needs_rescaling")
rad_mev_h = r.TH1F("rescale_rad","rescale_rad",200,0.,200.)
nbins = invMassHistos['rad'].GetXaxis().GetNbins()
for b in range(nbins):
    val = invMassHistos['rad'].GetBinContent(b+1)
    rad_mev_h.SetBinContent(b+1,val)
rad_mev_h.SetName(name)
invMassHistos['rad'] = rad_mev_h


#Make N bins the same 
invMassHistos['rad_slic'].GetXaxis().SetRange(1,200)
invMassHistos['rad'].GetXaxis().SetRange(1,200)
invMassHistos['rad_slic'].SetBins(200,0.0,200.0)
invMassHistos['rad'].SetBins(200,0.0,200.0)

radAcc = getTotalRadiativeAcceptance(invMassHistos['rad'], invMassHistos['rad_slic'], mV_MeV)
print("Tot Rad Acceptance is ", radAcc)
 
#Hardcode mass resolution for now
massRes_MeV = 3.0 #Found using 2016 simp mass res plot for mV = 55

#Count background rate
dNdm = 0.0
Mbin = 30.0
for ev in tt_array:
    if 1000.0*ev[variables.index('unc_vtx_mass')] > mAp_MeV + (Mbin/2): continue
    if 1000.0*ev[variables.index('unc_vtx_mass')] < mAp_MeV - (Mbin/2): continue
    dNdm += mcScale['tritrig']
    pass
for ev in wab_array:
    if 1000.0*ev[variables.index('unc_vtx_mass')] > mAp_MeV + (Mbin/2): continue
    if 1000.0*ev[variables.index('unc_vtx_mass')] < mAp_MeV - (Mbin/2): continue
    dNdm += mcScale['wab']
    pass
print("Background rate: ", dNdm)

#Get the pretrigger vtx distribution ONLY NEED TO DO THIS ONCE!
vdSimFilename = "/sdf/group/hps/users/alspellm/projects/THESIS/mc/2016/simps/slic_ana/hadd_mass_%s_simp_mcAna.root"%(mV_MeV)
vdSimFile = r.TFile(vdSimFilename)
vdSimZ_hcp = copy.deepcopy(vdSimFile.Get("mcAna/mcAna_mc625Z_h") )
vdSimFile.Close()
vdSimZ_hcp.SetName("vdSimZ_hcp")
vdSimZ_h = r.TH1F("vdSimZ_h", ";true z_{vtx} [mm];MC Events", 200, -50.3, 149.7)
for i in range(201):
    vdSimZ_h.SetBinContent(i, vdSimZ_hcp.GetBinContent(i))
    pass

zCut = 999.
lowMass = float(mV_MeV) - 2.8*massRes_MeV/2.0
highMass = float(mV_MeV) + 2.8*massRes_MeV/2.0
vdSelZ_h = r.TH1F("vdSelZ_h", ";true z_{vtx} [mm];MC Events", 200, -50.3, 149.7)
vdSelNoZ_h = r.TH1F("vdSelNoZ_h", ";true z_{vtx} [mm];MC Events", 200, -50.3, 149.7)
for ev in sig_arr:
    if 1000.0*ev[variables.index('unc_vtx_mass')] > highMass: continue
    if 1000.0*ev[variables.index('unc_vtx_mass')] > highMass: continue
    if ev[variables.index('unc_vtx_z')] < zCut: continue 
    vdSelZ_h.Fill(ev[variables.index('true_vtx_z')])

#Make efficiencies to get F(z)
vdEffVtxZ_e = r.TEfficiency(vdSelZ_h, vdSimZ_h)
vdEffVtxZ_e.SetName("vdEffVtxZ_e")
effCalc_h = vdEffVtxZ_e


best_zbi = 0
best_var = None
best_cut = None
#for var,cut in iter_cut_map.items():
#    zbi = 


outfile = r.TFile("testout.root","RECREATE")
outfile.cd()
#for histo in signal_histos.values():
#    histo.Write()
#outfile.Close()
#
