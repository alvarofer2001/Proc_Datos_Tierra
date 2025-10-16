
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\TD\PROYECTO\\Proc_Datos_Tierra\\auxiliary'
indir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-E2E\\myoutput_ism"
outdir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-E2E\\myoutput_l1b"

# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()
