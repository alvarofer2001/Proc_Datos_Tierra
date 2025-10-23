from math import pi
from config.ismConfig import ismConfig
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.special import j1
from numpy.matlib import repmat
from common.io.readMat import writeMat
from common.plot.plotMat2D import plotMat2D
from scipy.interpolate import interp2d
from numpy.fft import fftshift, ifft2
import os

class mtf:
    """
    Class MTF. Collects the analytical modelling of the different contributions
    for the system MTF
    """
    def __init__(self, logger, outdir):
        self.ismConfig = ismConfig()
        self.logger = logger
        self.outdir = outdir

    def system_mtf(self, nlines, ncolumns, D, lambd, focal, pix_size,
                   kLF, wLF, kHF, wHF, defocus, ksmear, kmotion, directory, band):
        """
        System MTF
        :param nlines: Lines of the TOA
        :param ncolumns: Columns of the TOA
        :param D: Telescope diameter [m]
        :param lambd: central wavelength of the band [m]
        :param focal: focal length [m]
        :param pix_size: pixel size in meters [m]
        :param kLF: Empirical coefficient for the aberrations MTF for low-frequency wavefront errors [-]
        :param wLF: RMS of low-frequency wavefront errors [m]
        :param kHF: Empirical coefficient for the aberrations MTF for high-frequency wavefront errors [-]
        :param wHF: RMS of high-frequency wavefront errors [m]
        :param defocus: Defocus coefficient (defocus/(f/N)). 0-2 low defocusing
        :param ksmear: Amplitude of low-frequency component for the motion smear MTF in ALT [pixels]
        :param kmotion: Amplitude of high-frequency component for the motion smear MTF in ALT and ACT
        :param directory: output directory
        :return: mtf
        """

        self.logger.info("Calculation of the System MTF")

        # Calculate the 2D relative frequencies
        self.logger.debug("Calculation of 2D relative frequencies")
        fn2D, fr2D, fnAct, fnAlt = self.freq2d(nlines, ncolumns, D, lambd, focal, pix_size)

        # Diffraction MTF
        self.logger.debug("Calculation of the diffraction MTF")
        Hdiff = self.mtfDiffract(fr2D)

        # Defocus
        Hdefoc = self.mtfDefocus(fr2D, defocus, focal, D)

        # WFE Aberrations
        Hwfe = self.mtfWfeAberrations(fr2D, lambd, kLF, wLF, kHF, wHF)

        # Detector
        Hdet  = self. mtfDetector(fn2D)

        # Smearing MTF
        Hsmear = self.mtfSmearing(fnAlt, ncolumns, ksmear)

        # Motion blur MTF
        Hmotion = self.mtfMotion(fn2D, kmotion)

        # Calculate the System MTF
        self.logger.debug("Calculation of the Sysmtem MTF by multiplying the different contributors")
        Hsys = Hmotion * Hsmear * Hdet * Hwfe * Hdefoc * Hdiff # dummy

        # Plot cuts ACT/ALT of the MTF
        self.plotMtf(Hdiff, Hdefoc, Hwfe, Hdet, Hsmear, Hmotion, Hsys, nlines, ncolumns, fnAct, fnAlt, directory, band)


        return Hsys

    def freq2d(self,nlines, ncolumns, D, lambd, focal, w):
        """
        Calculate the relative frequencies 2D (for the diffraction MTF)
        :param nlines: Lines of the TOA
        :param ncolumns: Columns of the TOA
        :param D: Telescope diameter [m]
        :param lambd: central wavelength of the band [m]
        :param focal: focal length [m]
        :param w: pixel size in meters [m]
        :return fn2D: normalised frequencies 2D (f/(1/w))
        :return fr2D: relative frequencies 2D (f/(1/fc))
        :return fnAct: 1D normalised frequencies 2D ACT (f/(1/w))
        :return fnAlt: 1D normalised frequencies 2D ALT (f/(1/w))
        """
        # DONE
        fstepAlt = 1/nlines/w
        fstepAct = 1/ncolumns/w

        # 1D frequency vectors
        eps = 1e-10
        fAlt = np.arange(-1 / (2*w), 1 / (2*w) - eps, fstepAlt)
        fAct = np.arange(-1 / (2*w), 1 / (2*w) - eps, fstepAct)

        # Normalize the frequencies with the cut-off
        fc = D / (lambd * focal)

        frAct = fAct / fc
        frAlt = fAlt / fc

        fnAct = fAct / (1 / w)
        fnAlt = fAlt / (1 / w)

        # 2D frequency grids
        [fnAltxx,fnActxx] = np.meshgrid(fnAlt, fnAct, indexing='ij') # Please use ‘ij’ indexing or you will get the transpose
        fn2D = np.sqrt(fnAltxx*fnAltxx + fnActxx*fnActxx)

        [frAltxx,frActxx] = np.meshgrid(frAlt, frAct, indexing='ij') # Please use ‘ij’ indexing or you will get the transpose
        fr2D = np.sqrt(frAltxx*frAltxx + frActxx*frActxx)
        return fn2D, fr2D, fnAct, fnAlt

    def mtfDiffract(self,fr2D):
        """
        Optics Diffraction MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :return: diffraction MTF
        """
        #TODO
        Hdiff=2/pi*(np.arccos(fr2D)-fr2D*(1-fr2D**2)**(1/2))
        #Hdiff[fr2D * fr2D > 1] = 0
        return Hdiff


    def mtfDefocus(self, fr2D, defocus, focal, D):
        """
        Defocus MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :param defocus: Defocus coefficient (defocus/(f/N)). 0-2 low defocusing
        :param focal: focal length [m]
        :param D: Telescope diameter [m]
        :return: Defocus MTF
        """
        #TODO
        x =pi* defocus*fr2D*(1-fr2D)
        Hdefoc=(2*j1(x))/x

        return Hdefoc

    def mtfWfeAberrations(self, fr2D, lambd, kLF, wLF, kHF, wHF):
        """
        Wavefront Error Aberrations MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :param lambd: central wavelength of the band [m]
        :param kLF: Empirical coefficient for the aberrations MTF for low-frequency wavefront errors [-]
        :param wLF: RMS of low-frequency wavefront errors [m]
        :param kHF: Empirical coefficient for the aberrations MTF for high-frequency wavefront errors [-]
        :param wHF: RMS of high-frequency wavefront errors [m]
        :return: WFE Aberrations MTF
        """
        #TODO
        Hwfe=np.exp(-fr2D*(1-fr2D)*(kLF*(wLF/lambd)**2+kHF*(wHF/lambd)**2))
        return Hwfe

    def mtfDetector(self,fn2D):
        """
        Detector MTF
        :param fnD: 2D normalised frequencies (f/(1/w))), where w is the pixel width
        :return: detector MTF
        """
        #TODO
        Hdet=np.abs(np.sinc(fn2D))
        return Hdet

    def mtfSmearing(self, fnAlt, ncolumns, ksmear):
        """
        Smearing MTF
        :param ncolumns: Size of the image ACT
        :param fnAlt: 1D normalised frequencies 2D ALT (f/(1/w))
        :param ksmear: Amplitude of low-frequency component for the motion smear MTF in ALT [pixels]
        :return: Smearing MTF
        """
        #TODO
        nlines = len(fnAlt)
        Hsmear_1d=np.sinc(ksmear*fnAlt)
        Hsmear=np.tile(Hsmear_1d.reshape(-1,1), (1, ncolumns))
        return Hsmear

    def mtfMotion(self, fn2D, kmotion):
        """
        Motion blur MTF
        :param fnD: 2D normalised frequencies (f/(1/w))), where w is the pixel width
        :param kmotion: Amplitude of high-frequency component for the motion smear MTF in ALT and ACT
        :return: detector MTF
        """
        #TODO

        Hmotion=np.sinc(kmotion*fn2D)

        return Hmotion

    def plotMtf(self,Hdiff, Hdefoc, Hwfe, Hdet, Hsmear, Hmotion, Hsys, nlines, ncolumns, fnAct, fnAlt, directory, band):
        """
        Plotting the system MTF and all of its contributors
        :param Hdiff: Diffraction MTF
        :param Hdefoc: Defocusing MTF
        :param Hwfe: Wavefront electronics MTF
        :param Hdet: Detector MTF
        :param Hsmear: Smearing MTF
        :param Hmotion: Motion blur MTF
        :param Hsys: System MTF
        :param nlines: Number of lines in the TOA
        :param ncolumns: Number of columns in the TOA
        :param fnAct: normalised frequencies in the ACT direction (f/(1/w))
        :param fnAlt: normalised frequencies in the ALT direction (f/(1/w))
        :param directory: output directory
        :param band: band
        :return: N/A
        """
        # Central pixels
        ic = nlines // 2
        jc = ncolumns // 2

        # Extract 1D cuts for all MTF contributors (ACT direction)
        cut_diff_act = Hdiff[ic, :]
        cut_defoc_act = Hdefoc[ic, :]
        cut_wfe_act = Hwfe[ic, :]
        cut_det_act = Hdet[ic, :]
        cut_smear_act = Hsmear[ic, :]
        cut_motion_act = Hmotion[ic, :]
        cut_sys_act = Hsys[ic, :]

        # Extract 1D cuts for all MTF contributors (ALT direction)
        cut_diff_alt = Hdiff[:, jc]
        cut_defoc_alt = Hdefoc[:, jc]
        cut_wfe_alt = Hwfe[:, jc]
        cut_det_alt = Hdet[:, jc]
        cut_smear_alt = Hsmear[:, jc]
        cut_motion_alt = Hmotion[:, jc]
        cut_sys_alt = Hsys[:, jc]

        # Create two-panel plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

        # Color scheme
        colors = {'Diffraction': '#1f77b4',
                  'Defocus': '#ff7f0e',
                  'WFE': '#2ca02c',
                  'Detector': '#d62728',
                  'Smear': '#9467bd',
                  'Motion': '#8c564b',
                  'System MTF': '#000000'}

        # ACT panel (left)
        axes[0].plot(fnAct, cut_diff_act, color=colors['Diffraction'], label='Diffraction', linewidth=1.5)
        axes[0].plot(fnAct, cut_defoc_act, color=colors['Defocus'], label='Defocus', linewidth=1.5)
        axes[0].plot(fnAct, cut_wfe_act, color=colors['WFE'], label='WFE', linewidth=1.5)
        axes[0].plot(fnAct, cut_det_act, color=colors['Detector'], label='Detector', linewidth=1.5)
        axes[0].plot(fnAct, cut_smear_act, color=colors['Smear'], label='Smear', linewidth=1.5)
        axes[0].plot(fnAct, cut_motion_act, color=colors['Motion'], label='Motion', linewidth=1.5)
        axes[0].plot(fnAct, cut_sys_act, color=colors['System MTF'], label='System', linewidth=2.5, linestyle='-')

        axes[0].axvline(0.5, color='k', linestyle=':', alpha=0.7, label='Nyquist')  # Nyquist line
        axes[0].set_title(f'MTF at ACT Direction')
        axes[0].set_xlabel('Spatial frequency f/(1/w)')
        axes[0].set_ylabel('MTF')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xlim([0.0, 0.55])
        axes[0].set_ylim([0.0, 1.05])
        axes[0].legend(loc='lower left', fontsize=9)

        # ALT panel (right)
        axes[1].plot(fnAlt, cut_diff_alt, color=colors['Diffraction'], label='Diffraction', linewidth=1.5)
        axes[1].plot(fnAlt, cut_defoc_alt, color=colors['Defocus'], label='Defocus', linewidth=1.5)
        axes[1].plot(fnAlt, cut_wfe_alt, color=colors['WFE'], label='WFE', linewidth=1.5)
        axes[1].plot(fnAlt, cut_det_alt, color=colors['Detector'], label='Detector', linewidth=1.5)
        axes[1].plot(fnAlt, cut_smear_alt, color=colors['Smear'], label='Smear', linewidth=1.5)
        axes[1].plot(fnAlt, cut_motion_alt, color=colors['Motion'], label='Motion', linewidth=1.5)
        axes[1].plot(fnAlt, cut_sys_alt, color=colors['System MTF'], label='System', linewidth=2.5, linestyle='-')

        axes[1].axvline(0.5, color='k', linestyle=':', alpha=0.7, label='Nyquist')  # Nyquist line
        axes[1].set_title(f'MTF at ALT Direction')
        axes[1].set_xlabel('Spatial frequency f/(1/w)')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xlim([0.0, 0.55])
        axes[1].set_ylim([0.0, 1.05])

        # Overall title and layout
        fig.suptitle(f'System MTF Analysis for {band}', fontsize=12)
        plt.tight_layout()

        # Save plot
        fig.savefig(os.path.join(directory, f'mtf_{band}.png'), dpi=150, bbox_inches='tight')
        plt.close(fig)

        # Log results
        # self.logger.info(f"MTF plot saved: {os.path.join(directory, f'mtf_{band}.png')}")
        # self.logger.info(f"Band {band} - MTF@Nyquist ACT: {mtf_nyquist_act:.3f}, ALT: {mtf_nyquist_alt:.3f}")
        # self.logger.info(f"Quality assessment: {quality}")
    #TODO


