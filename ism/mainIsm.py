
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\TD\PROYECTO\\Proc_Datos_Tierra\\auxiliary"
indir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-ISM\\input\\gradient_alt100_act150"
outdir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-ISM\\myoutput_ism"


# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()
