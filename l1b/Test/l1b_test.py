from l1b.src.initL1b import initL1b
from common.io.writeToa import readToa
import numpy as np
import matplotlib.pyplot as plt
import os

class CompareToa(initL1b):

    def __init__(self, auxdir, output, myoutput, plots):
        """
        :param auxdir: Directorio de ficheros auxiliares
        :param output: Directorio con los TOA originales
        :param myoutput: Directorio con los TOA procesados (myoutput)
        :param plot: Carpeta para guardar plots
        """
        super().__init__(auxdir, output, plots)
        self.output = output
        self.myoutput = myoutput
        self.plots = plots

    def readData(self, band):
        """Lee los dos archivos TOA para una banda específica"""
        fname = self.globalConfig.l1b_toa + band + ".nc"  # mismo patrón que en tu módulo L1B
        toa1 = readToa(self.output, fname)
        toa2 = readToa(self.myoutput, fname)
        return toa1, toa2

    def computeDifference(self, toa1, toa2):
        """Calcula la diferencia punto a punto"""
        return toa1 - toa2

    def plotComparison(self, toa1, toa2, diff, band):
        """Grafica los dos TOA y su diferencia"""
        x = np.arange(toa1.size)  # eje x = índice de píxel

        plt.figure(figsize=(10, 6))
        plt.plot(x, toa1.flatten(), label=f"TOA original {band}")
        plt.plot(x, toa2.flatten(), label=f"TOA procesado {band}")
        plt.plot(x, diff.flatten(), label=f"Diferencia {band}", linestyle="--")

        plt.legend()
        plt.title(f"Comparación TOA vs myTOA - {band}")
        plt.xlabel("Índice de píxel")
        plt.ylabel("Valor TOA")
        plt.grid(True)

        # Guardar en archivo
        os.makedirs(self.plots, exist_ok=True)
        outpath = os.path.join(self.plots, f"comparison_{band}.png")
        plt.savefig(outpath)

        # Mostrar en pantalla
        plt.show()
        plt.close()

    def processModule(self):
        """Orquesta todo el flujo para todas las bandas de self.globalConfig.bands"""
        self.logger.info("Inicio de la comparación TOA")

        for band in self.globalConfig.bands:
            self.logger.info(f"Procesando banda {band}...")
            toa1, toa2 = self.readData(band)
            diff = self.computeDifference(toa1, toa2)
            self.plotComparison(toa1, toa2, diff, band)

        self.logger.info("✅ Comparación terminada para todas las bandas.")



if __name__ == "__main__":
    auxdir = r'C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\TD\PROYECTO\\Proc_Datos_Tierra\\auxiliary'
    output = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\output"
    myoutput = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\myoutput"
    plots = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\plots"

    comp = CompareToa(auxdir, output, myoutput, plots)
    comp.processModule()


