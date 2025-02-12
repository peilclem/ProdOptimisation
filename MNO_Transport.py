# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:36:17 2025

@author: peill

Non linearité:
    - Conteneurs
    - Ouverturre et fermeture d'usine
    
(Utiliser toute la capa et stocker)(ouvrir une grande = interssant)


1 modele financier pour ouverture et fermeture
1 modele technique avec les prods

cout prod t0 --> 27M€ sinon 40M€
Difficulté: Estimer les ruptures d'approvisionnement'

best 2025 107M€ benef & 1726 CO2


Utiliser Optuna pour optimisation du modèle
"""
import pandas as pd
import numpy as np

def import_PeriodData():
    T = []
    filenames = [f'MNO_Transport_DataT{k}.csv' for k in range(3)]
    
    for k, filename in enumerate(filenames):
        data = np.array(pd.read_csv(root_dir + filename, sep=',', encoding='latin-1').dropna(axis=1, how='all').replace(',',''))
        geo = list(data[10:16,0])
        produit = list(data[2,1:4])
        T.append(Periode_T(data, k, geo, produit))
    return T[0], T[1], T[2], geo, produit

def get_prod(file, produit):
    prod = pd.DataFrame(file[3:7,1:4], columns=produit, index=file[3:7,0])
    prod.loc[file[27,0]]=file[28,1:4]
    return prod

def get_coutprod(file, geo, produit):
    temp_col = ['Taux horaire']
    temp_col.extend(produit)
    cout_prod = pd.DataFrame(file[10:16,1:5], index=geo, columns=temp_col)
    return cout_prod

def get_demand(file, geo, produit):
        temp_lignes=geo.copy()
        temp_lignes.append('Total')
        temp_col=produit.copy()
        temp_col.extend(['Total Zone', 'Capa consommée'])
        demande = pd.DataFrame(file[41:48,1:6], index=temp_lignes, columns=temp_col)
        return demande

class Periode_T():
    def __init__(self, data, period:int, geo:list, produit:list):
        self.period = period
        self.prod = get_prod(data, produit)
        self.cout_prod = get_coutprod(data, geo, produit)
        self.expedition  = pd.DataFrame(data[19:25,1:7], index=geo, columns=geo)
        self.taux_impot = pd.DataFrame(data[32:38,1:7], index=geo, columns=geo)
        self.demande = get_demand(data, geo, produit)
        self.usines = pd.DataFrame(data[51:56,1:4], index=data[51:56,0], columns=data[50,1:4])
        self.trs = pd.Series(data[59:65,0], index=geo)
        self.risque_perte = pd.DataFrame(data[68:74,1:7], index=geo, columns=geo)
        self.stockage = pd.DataFrame((data[78,1:7], data[78,7:13], data[78,13:19]), columns=geo, index=produit).transpose()
        self.co2_conteneur = pd.DataFrame(data[82:88,1:7], index=geo, columns=geo)
        self.mix_energetique = pd.Series(data[91:,1], index=geo)

def calculateExport(prodP1, prodP2, prodP3, geo, produit):
    export = pd.DataFrame(np.zeros(shape=(6,3)), index=geo, columns=produit)
    from itertools import product
    for zone, prod in product(geo, produit):
        if prod=='P1':
            export.loc[zone, prod]=prodP1[zone].sum()
        elif prod=='P2':
            export.loc[zone, prod]=prodP2[zone].sum()
        elif prod=='P3':
            export.loc[zone, prod]=prodP3[zone].sum()
        else:
            raise ValueError('Invalid product name')
        
    print(export)
    return export


#%% MAIN

root_dir = 'C:/Users/peill/Documents/Sigma_Clermont/MS_ESD/M1/MNO/Transport/'

# Import data
T1, T2, T3, geo, produit = import_PeriodData()

# Create decision tables
prodP1 = pd.DataFrame(np.ones(shape=(6,6))*1, index=geo, columns=geo)
prodP2 = pd.DataFrame(np.ones(shape=(6,6))*2, index=geo, columns=geo)
prodP3 = pd.DataFrame(np.ones(shape=(6,6))*3, index=geo, columns=geo)

export = calculateExport(prodP1, prodP2, prodP3, geo, produit)