import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


'''CODE FÜR PRAKTIKUMSTAG 3 CYCLOVOLTAMETRIE'''
'''HIER DATEIPFAD WO DIE DATEN LIEGEN EINTRAGEN'''
'''REINIGUNGSDATEIN MÜSSEN ENTFERNT WERDEN, SONST WERDEN SIE MITGEPLOTTED'''
folder = Path(r"C:\Beispiel\Ablageort")
file_paths = sorted(folder.glob("*.csv"))

usecols = ["E__V", "I__A"]
na_values = ["", " ", ",,", ",,,,"]

encoding = "latin1"

all_forward = []
all_reverse = []
verarbeitete_dateien = []

for file_path in file_paths:
    try:
        verarbeitete_dateien.append(file_path.name)
        df = pd.read_csv(file_path, usecols=usecols, na_values=na_values, encoding=encoding)
        df_clean = df.dropna().astype({"E__V": float, "I__A": float})

        e_values = df_clean['E__V'].values
        diffs = np.diff(e_values)
        turn_idx = np.argmax(diffs < 0)

        forward = df_clean.iloc[:turn_idx + 1]
        reverse = df_clean.iloc[turn_idx + 1:]

        all_forward.append(forward)
        all_reverse.append(reverse)

    except Exception as e:
        print(f"Fehler in Datei {file_path.name}: {e}")
        continue

e_values_forward = all_forward[0]['E__V'].values
e_values_reverse = all_reverse[0]['E__V'].values

mean_forward = np.zeros_like(e_values_forward)
mean_reverse = np.zeros_like(e_values_reverse)

for i in range(len(e_values_forward)):
    mean_forward[i] = np.mean([f['I__A'].iloc[i] for f in all_forward])

for i in range(len(e_values_reverse)):
    mean_reverse[i] = np.mean([r['I__A'].iloc[i] for r in all_reverse])

'''HIER WERTE FÜR INTEGRATION EINTRAGEN'''
E_start = -0.07
E_end   =  0.20
y0      = -0.000515


x_forward = all_forward[0]['E__V'].values

x_grid = np.linspace(E_start, E_end, 500)

y_grid = np.interp(x_grid, x_forward, mean_forward)

diff_pos = np.clip(y0 - y_grid, a_min=0, a_max=None)

area_forward = np.trapz(diff_pos, x_grid)

plt.plot(e_values_reverse, mean_reverse, color='red', linewidth=2)

'''INTEGRATIONS HILFSGRAPHEN wenn man die Integration benötigt müssen die "#" entfernt werden'''
#plt.axhline(y=y0, color='green', linestyle='--', label='Integrationsuntergrenze')
#plt.axvline(x=E_start, color='blue', linestyle='--', label='Integrationsanfang')
#plt.axvline(x=E_end, color='purple', linestyle='--', label='Integrationsende')

'''HIER PUNKTE FÜR STEIGUNG EINTRAGEN'''
I1 = 0.2
E1 = -0.000513
I2 = 0.8
E2 = -0.000375
m = (E2-E1)/(I2-I1)

'''STEIGUNGS GRAPH auch hier wenn benötigt, dass # entfernen'''
#plt.plot([I1, I2], [E1, E2], color='black', label='Hilfslinie')

plt.title('Cyclic Voltammetry: "Dein Titel hier"')
plt.xlabel('Potential (V)')
plt.ylabel('Current (A)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='best')
plt.tight_layout()
plt.show()

def finde_min_strom_und_ev(all_datasets, dateinamen):
    min_wert = np.inf
    min_datei = ""
    min_ev    = None

    for df, name in zip(all_datasets, dateinamen * 2):
        aktuelles_min = df['I__A'].min()
        if aktuelles_min < min_wert:
            min_wert  = aktuelles_min
            min_datei = name
            idx_min   = df['I__A'].idxmin()
            min_ev    = df.loc[idx_min, 'E__V']

    return min_wert, min_ev, min_datei

min_stromwert, zugehoeriger_ev, zugehoerige_datei = \
    finde_min_strom_und_ev(all_forward + all_reverse, verarbeitete_dateien)

'''die Prints werden aktuell immer in die Konsole geschrieben, da es fürs plotten keinen unterschied macht. Falls sie stören oder verwirren ein # davor setzen'''
print(f"Fläche (Forward) von {E_start}V bis {E_end}V bis y0={y0}: {area_forward:.6e} C")

print(f"Steigung ist {m}")

print(f"Der niedrigste Stromwert ist {min_stromwert:.6e} A")
print(f"Zugehöriger EV-Wert: {zugehoeriger_ev:.6f} V")
print(f"In Datei: {zugehoerige_datei}")
