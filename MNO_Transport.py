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
from itertools import product # cross product in iterations (for loop)

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

class Production():
    def __init__(self, geo:list, produit:list):
        self.P1 = pd.DataFrame(np.ones(shape=(6,6))*1, index=geo, columns=geo)
        self.P2 = pd.DataFrame(np.ones(shape=(6,6))*1, index=geo, columns=geo)
        self.P3 = pd.DataFrame(np.ones(shape=(6,6))*1, index=geo, columns=geo)
        
        #. tbd
        self.P1.loc['AFR']=2
        self.P2.loc['AMN']=4
        self.P3.loc['EUR']=6

        self.exportation = pd.DataFrame(np.zeros(shape=(6,3)), index=geo, columns=produit)
        self.production  = pd.DataFrame(np.zeros(shape=(6,3)), index=geo, columns=produit)
        
    def calculateProdExport(self):
        for zone, prod in product(geo, produit):
            if prod=='P1':
                self.exportation.loc[zone, prod] = self.P1[zone].sum()
                self.production.loc[zone, prod] = self.P1.loc[zone].sum()
            elif prod=='P2':
                self.exportation.loc[zone, prod] = self.P2[zone].sum()
                self.production.loc[zone, prod] = self.P2.loc[zone].sum()
            elif prod=='P3':
                self.exportation.loc[zone, prod] = self.P3[zone].sum()
                self.production.loc[zone, prod] = self.P3.loc[zone].sum()
            else:
                raise ValueError('Invalid product name')
                
        print(f'\n{'EXPORTATIONS':^20}\n{self.exportation}')
        print(f'\n{'PRODUCTION':^20}\n{self.production}')
        print(f'\n\n{'--- Total Prod updated ---':^50}')
    
class Stock():
    def __init__(self, geo:list, produit:list):
        self.P1 = pd.DataFrame(np.ones(shape=(6,6))*1, index=geo, columns=geo)
        self.P2 = pd.DataFrame(np.ones(shape=(6,6))*2, index=geo, columns=geo)
        self.P3 = pd.DataFrame(np.ones(shape=(6,6))*3, index=geo, columns=geo)
        
        self.stock = pd.DataFrame(np.zeros(shape=(6,3)), index=geo, columns=produit)
        
    def computeStockVariation(self, Production):
        
        
        return variation
    
    def updateStock(self, Production):
        self.variation = self.computeStockVariation(Production)
        self.stock = pd.DataFrame(np.ones(shape=(6,6))*5, index=geo, columns=geo)
        print(f'{'--- STOCKS updated ---':^50}')

#%% MAIN

root_dir = 'C:/Users/peill/Documents/Sigma_Clermont/MS_ESD/M1/MNO/Transport/'

# Import data
T1, T2, T3, geo, produit = import_PeriodData()

# Calculate prod and export quantities
Prod = Production(geo, produit)
Prod.calculateProdExport()

# Update stocks
Stocks = Stock(geo, produit)
Stocks.updateStock(Prod)
# Stocks.stock


