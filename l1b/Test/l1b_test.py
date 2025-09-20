from common.io.writeToa import readToa
import numpy as np
import matplotlib.pyplot as plt
import os


class CompareToaSimple:

    def __init__(self, output_dir, myoutput_dir, plots_dir):
        self.output_dir = output_dir  # Carpeta con TOA de referencia
        self.myoutput_dir = myoutput_dir  # Carpeta con tu TOA
        self.plots_dir = plots_dir  # Carpeta para guardar gráficas

    def compare_band(self, band):
        """Compara los TOA de una banda específica"""

        # Leer archivos
        filename = f"l1b_toa_{band}.nc"
        toa_ref = readToa(self.output_dir, filename)
        toa_my = readToa(self.myoutput_dir, filename)

        # Convertir a arrays 1D
        ref_flat = toa_ref.flatten()
        my_flat = toa_my.flatten()

        # Calcular diferencia
        diff = ref_flat - my_flat
        abs_diff = np.abs(diff)
        rel_diff = abs_diff / (np.abs(ref_flat) + 1e-12)  # Diferencia relativa

        # Calcular estadísticas para validación
        std = np.std(abs_diff)
        three_sigma = 3 * std
        elements_above_001 = np.sum(rel_diff > 0.0001)  # Elementos > 0.01%
        total_elements = len(ref_flat)

        # Validar criterios
        criterion_1 = (elements_above_001 / total_elements) <= 0.001  # < 0.1% elementos > 0.01%
        criterion_2 = np.max(abs_diff) <= three_sigma  # Máxima diferencia dentro de 3-sigma

        # Crear gráfica
        plt.figure(figsize=(12, 8))

        # Subplot 1: Valores TOA
        plt.subplot(2, 1, 1)
        x = np.arange(min(1000, len(ref_flat)))  # Mostrar solo primeros 1000 puntos
        plt.plot(x, ref_flat[:1000], 'b-', label=f'TOA Referencia {band}', alpha=0.7)
        plt.plot(x, my_flat[:1000], 'r-', label=f'TOA MyOutput {band}', alpha=0.7)
        plt.ylabel('TOA [mW/m²/sr]')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.title(f'Comparación TOA - Banda {band}')

        # Subplot 2: Diferencia
        plt.subplot(2, 1, 2)
        plt.plot(x, diff[:1000], 'g-', label='Diferencia (Ref - My)', alpha=0.7)
        plt.axhline(y=three_sigma, color='r', linestyle='--', label=f'Límite 3σ = {three_sigma:.2e}')
        plt.axhline(y=-three_sigma, color='r', linestyle='--')
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        plt.ylabel('Diferencia Absoluta')
        plt.xlabel('Índice del Elemento')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Añadir texto de validación
        validation_text = (f"Validación: {'✅' if criterion_1 and criterion_2 else '❌'}\n"
                           f"Elementos >0.01%: {elements_above_001}/{total_elements}\n"
                           f"Diferencia máxima: {np.max(abs_diff):.2e}\n"
                           f"3σ: {three_sigma:.2e}")
        plt.figtext(0.02, 0.02, validation_text, fontsize=10,
                    bbox=dict(boxstyle="round", facecolor="lightgreen" if criterion_1 and criterion_2 else "lightcoral",
                              alpha=0.8))

        plt.tight_layout()

        # Guardar gráfica
        os.makedirs(self.plots_dir, exist_ok=True)
        plt.savefig(os.path.join(self.plots_dir, f'comparison_{band}.png'), dpi=150, bbox_inches='tight')
        plt.close()

        # Mostrar resultados en consola
        print(f"\n--- Banda {band} ---")
        print(f"Elementos totales: {total_elements}")
        print(f"Elementos con diferencia > 0.01%: {elements_above_001}")
        print(f"Diferencia máxima: {np.max(abs_diff):.2e}")
        print(f"3σ: {three_sigma:.2e}")
        print(f"Criterio 1 (<0.1% elementos >0.01%): {'✅' if criterion_1 else '❌'}")
        print(f"Criterio 2 (max diff ≤ 3σ): {'✅' if criterion_2 else '❌'}")
        print(f"VALIDACIÓN GENERAL: {'✅ APROBADO' if criterion_1 and criterion_2 else '❌ RECHAZADO'}")

        return criterion_1 and criterion_2

    def compare_all_bands(self):
        """Compara todas las bandas"""
        bands = ['VNIR-0', 'VNIR-1', 'VNIR-2', 'VNIR-3']  # Ajusta según tus bandas

        print("INICIANDO COMPARACIÓN TOA")
        print("=" * 50)

        all_valid = True

        for band in bands:
            try:
                is_valid = self.compare_band(band)
                if not is_valid:
                    all_valid = False
            except Exception as e:
                print(f"Error procesando banda {band}: {e}")
                all_valid = False

        print("\n" + "=" * 50)
        if all_valid:
            print("🎉 ¡TODAS LAS BANDAS CUMPLEN LOS CRITERIOS!")
        else:
            print("⚠️  Algunas bandas NO cumplen los criterios")
        print("=" * 50)


# Ejecución

if __name__ == "__main__":
    auxdir = r'C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\TD\PROYECTO\\Proc_Datos_Tierra\\auxiliary'
    output_dir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\output"
    myoutput_dir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\myoutput"
    plots_dir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\plots"

    comp = CompareToaSimple(output_dir, myoutput_dir, plots_dir)
    comp.compare_all_bands()


