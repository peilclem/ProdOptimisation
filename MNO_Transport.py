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
        data = np.array(pd.read_csv(data_dir + filename, sep=',', encoding='latin-1').dropna(axis=1, how='all').replace(',',''))
        geo = list(data[10:16,0])
        produit = list(data[2,1:4])
        T.append(Periode_T(data, k, geo, produit))
    return T[0], T[1], T[2], geo, produit



class Periode_T():
    def __init__(self, data, period:int, geo:list, produit:list):
        self.period = period
        self.prod = self.get_prod(data, produit).astype(float)
        self.cout_prod = self.get_coutprod(data, geo, produit).astype(float)
        self.expedition  = pd.DataFrame(data[19:25,1:7], index=geo, columns=geo, dtype=float)
        self.taux_impot = pd.DataFrame(data[32:38,1:7], index=geo, columns=geo, dtype=float)
        self.demande = self.get_demand(data, geo, produit).astype(float)
        self.usines = pd.DataFrame(data[51:56,1:4], index=data[51:56,0], columns=data[50,1:4], dtype=float)
        self.trs = pd.Series(data[59:65,0], index=geo)
        self.risque_perte = pd.DataFrame(data[68:74,1:7], index=geo, columns=geo, dtype=float)
        self.stockage = pd.DataFrame((data[78,1:7], data[78,7:13], data[78,13:19]), columns=geo, index=produit, dtype=float).transpose()
        self.co2_conteneur = pd.DataFrame(data[82:88,1:7], index=geo, columns=geo, dtype=float)
        self.mix_energetique = pd.Series(data[91:,1], index=geo, dtype=float)
        
    def get_prod(self, file, produit):
        prod = pd.DataFrame(file[3:7,1:4], columns=produit, index=file[3:7,0])
        prod.loc[file[27,0]]=file[28,1:4]
        return prod

    def get_coutprod(self, file, geo, produit):
        temp_col = ['Taux horaire']
        temp_col.extend(produit)
        cout_prod = pd.DataFrame(file[10:16,1:5], index=geo, columns=temp_col)
        return cout_prod

    def get_demand(self, file, geo, produit):
            temp_lignes=geo.copy()
            temp_lignes.append('Total')
            temp_col=produit.copy()
            temp_col.extend(['Total Zone', 'Capa consommée'])
            demande = pd.DataFrame(file[41:48,1:6], index=temp_lignes, columns=temp_col)
            return demande
            
            
class Production():
    def __init__(self, geo:list, produit:list):
        self.P1 = pd.DataFrame(np.ones(shape=(6,6))*0, index=geo, columns=geo)
        self.P2 = pd.DataFrame(np.ones(shape=(6,6))*0, index=geo, columns=geo)
        self.P3 = pd.DataFrame(np.ones(shape=(6,6))*0, index=geo, columns=geo)
        
        # #. tbd
        # self.P1.loc['AFR']=2
        # self.P2.loc['AMN']=4
        # self.P3.loc['EUR']=6

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
        self.P1 = pd.DataFrame(np.ones(shape=(6,6))*0, index=geo, columns=geo)
        self.P2 = pd.DataFrame(np.ones(shape=(6,6))*0, index=geo, columns=geo)
        self.P3 = pd.DataFrame(np.ones(shape=(6,6))*0, index=geo, columns=geo)
        
        self.total = pd.DataFrame(np.zeros(shape=(6,3)), index=geo, columns=produit)
        
    def computeStockVariation(self, Production, Periode):
        production = Production.exportation
        demande = Periode.demande.loc[geo,produit]
        variation = production - demande
        return variation
    
    def updateStock(self, Production, Periode):
        self.variation = self.computeStockVariation(Production, Periode)
        self.total = self.total + self.variation
        
        # Add total
        self.total.loc['Total'] = self.total.sum(axis=0)
        print(f'{'--- STOCKS updated ---':^50}')

class Company():
    def __init__(self, Periode, Production, Stock, geo:list):
        geo_copy = geo.copy()
        geo_copy.append('Total')
        
        # Composition
        self.initial = pd.DataFrame(np.ones(shape=(7,3))*0, index=geo_copy, columns=['Petite', 'Moyenne', 'Grande'])
        self.achat = pd.DataFrame(np.ones(shape=(7,3))*0, index=geo_copy, columns=['Petite', 'Moyenne', 'Grande'])
        self.vente = pd.DataFrame(np.ones(shape=(7,3))*1, index=geo_copy, columns=['Petite', 'Moyenne', 'Grande'])
        self.etat = pd.DataFrame(np.ones(shape=(7,5))*0, index=geo_copy, columns=['CoutExploit', 'Invest', 'Cession','Capacite','CO2'])
        
        # Finance
        self.CA = self.calculateCA(Production, Periode)
        self.prodExport = pd.Series(np.zeros(5), index=['ProdCoutDirect', 'DistribCoutDirect', 'FraisDouanes', 'StockCout', 'Total'])
        self.usines = pd.Series(np.zeros(4), index=['UsineInvest', 'UsinesFonct', 'UsinesCession', 'Total'])
        self.CoutSolution = self.prodExport + self.usines
        
        # CO2
        self.CO2 = pd.Series(np.zeros(3), index=['ProdCO2', 'DistribCO2', 'Total'])
        
    def calculateCA(self, Production, Periode):
        nb_produit = Production.production.sum(axis=0)
        prixProduit = Periode.prod.loc['Prix de vente Unitaire']
        print(prixProduit)
        return np.dot(nb_produit, prixProduit)
    
    
    
#%% MAIN

root_dir = 'C:/Users/peill/Documents/Sigma_Clermont/MS_ESD/M1/MNO/Transport/'
data_dir = root_dir + 'data/'

# Import data
T1, T2, T3, geo, produit = import_PeriodData()

# Calculate prod and export quantities
MyProd = Production(geo, produit)
MyProd.calculateProdExport()

# Update stocks
MyStocks = Stock(geo, produit)
MyStocks.updateStock(MyProd, T1)

# Company
MyCompany = Company(T1, MyProd, MyStocks, geo)

