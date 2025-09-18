
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\TD\PROYECTO\\Proc_Datos_Tierra\\auxiliary'
indir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\input"
outdir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP-TS-L1B-20250911T170833Z-1-001\\EODP-TS-L1B\\myoutput"

# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()
