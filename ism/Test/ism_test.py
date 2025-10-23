from common.io.writeToa import readToa
import numpy as np
import matplotlib.pyplot as plt
import os


class CompareToaISM:

    def __init__(self, output_dir, myoutput_dir, plots_dir):
        self.output_dir = output_dir  # Carpeta con TOA de referencia
        self.myoutput_dir = myoutput_dir  # Carpeta con tu TOA
        self.plots_dir = plots_dir  # Carpeta para guardar gráficas

    def compare_band(self, band, file_type='isrf'):
        """
        Compara los TOA de una banda específica

        Args:
            band: Banda a comparar (ej: 'VNIR-0')
            file_type: Tipo de archivo ('isrf' o 'optical')
        """

        # Construir nombre de archivo según el tipo
        if file_type == 'isrf':
            filename = f"ism_toa_isrf_{band}.nc"
        elif file_type == 'optical':
            filename = f"ism_toa_optical_{band}.nc"
        elif file_type == 'total':
            filename = f"ism_toa_{band}.nc"
        else:
            raise ValueError(f"Tipo de archivo no válido: {file_type}")

        # Leer archivos
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
        x = np.arange(min(150, len(ref_flat)))  # Mostrar solo primeros 150 puntos
        plt.plot(x, ref_flat[:150], 'b-', label=f'TOA Referencia (output)', alpha=0.7)
        plt.plot(x, my_flat[:150], 'r-', label=f'TOA MyOutput', alpha=0.7)
        plt.ylabel('TOA [mW/m²/sr]')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.title(f'Comparación TOA {file_type.upper()} - Banda {band}')

        # Subplot 2: Diferencia
        plt.subplot(2, 1, 2)
        plt.plot(x, diff[:150], 'g-', label='Diferencia (Ref - My)', alpha=0.7)
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
                    bbox=dict(boxstyle="round",
                              facecolor="lightgreen" if criterion_1 and criterion_2 else "lightcoral",
                              alpha=0.8))

        plt.tight_layout()

        # Guardar gráfica
        os.makedirs(self.plots_dir, exist_ok=True)
        plot_filename = f'comparison_{file_type}_{band}.png'
        plt.savefig(os.path.join(self.plots_dir, plot_filename), dpi=150, bbox_inches='tight')
        plt.close()

        # Mostrar resultados en consola
        print(f"\n--- Banda {band} ({file_type.upper()}) ---")
        print(f"Elementos totales: {total_elements}")
        print(f"Elementos con diferencia > 0.01%: {elements_above_001}")
        print(f"Diferencia máxima: {np.max(abs_diff):.2e}")
        print(f"3σ: {three_sigma:.2e}")
        print(f"Criterio 1 (<0.1% elementos >0.01%): {'✅' if criterion_1 else '❌'}")
        print(f"Criterio 2 (max diff ≤ 3σ): {'✅' if criterion_2 else '❌'}")
        print(f"VALIDACIÓN GENERAL: {'APROBADO' if criterion_1 and criterion_2 else 'RECHAZADO'}")

        return criterion_1 and criterion_2

    def compare_all_bands(self, file_types=['isrf', 'optical']):
        """
        Compara todas las bandas para los tipos de archivo especificados

        Args:
            file_types: Lista con tipos de archivo a comparar ('isrf' y/o 'optical')
        """
        bands = ['VNIR-0', 'VNIR-1', 'VNIR-2', 'VNIR-3']

        print("INICIANDO COMPARACIÓN TOA ISM")
        print("=" * 50)

        all_valid = True

        for file_type in file_types:
            print(f"\n{'=' * 50}")
            print(f"PROCESANDO ARCHIVOS: ism_toa_{file_type}")
            print(f"{'=' * 50}")

            for band in bands:
                try:
                    is_valid = self.compare_band(band, file_type)
                    if not is_valid:
                        all_valid = False
                except Exception as e:
                    print(f"Error procesando banda {band} ({file_type}): {e}")
                    all_valid = False

        print("\n" + "=" * 50)
        if all_valid:
            print("TODAS LAS BANDAS Y TIPOS CUMPLEN LOS CRITERIOS ✅")
        else:
            print("Algunas bandas o tipos NO cumplen los criterios ❌")
        print("=" * 50)


# Ejecución
if __name__ == "__main__":
    # Directorios para ISM
    base_dir = r'C:\Users\alvaf\OneDrive\Desktop\Carlos III\Cuatri III\Proc_datos_espacio\EODP_TER_2021\EODP-TS-ISM'
    output_dir = os.path.join(base_dir, 'output')
    myoutput_dir = os.path.join(base_dir, 'myoutput')
    plots_dir = os.path.join(base_dir, 'plots')

    # Crear comparador
    comp = CompareToaISM(output_dir, myoutput_dir, plots_dir)

    # Comparar ambos tipos de archivos (isrf y optical)
    #comp.compare_all_bands(file_types=['isrf', 'optical'])
    comp.compare_all_bands(file_types=['total'])
    # Si solo quieres comparar uno de los tipos, puedes usar:
    # comp.compare_all_bands(file_types=['isrf'])  # Solo ISRF
    # comp.compare_all_bands(file_types=['optical'])  # Solo Optical