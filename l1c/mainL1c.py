
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c

# Directory - this is the common directory for the execution of the E2E, all modules
# GM dir + L1B dir
auxdir = r'C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\TD\PROYECTO\\Proc_Datos_Tierra\\auxiliary'
indir = r"C:\\Users\\alvaf\\OneDrive\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-L1C\\input\\gm_alt100_act_150,C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-L1B\\myoutput"
outdir = r"C:\\Users\\alvaf\\OneDrive\\Desktop\\Carlos III\\Cuatri III\\Proc_datos_espacio\\EODP_TER_2021\\EODP-TS-L1C\\myoutput"

# Initialise the ISM
myL1c = l1c(auxdir, indir, outdir)
myL1c.processModule()
