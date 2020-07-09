from flask import url_for
import swisseph as swe
import datetime
from datetime import timedelta
import calendar
import pandas as pd
import csv
import os
from collections import defaultdict
import random


signes = ['Bélier','Taureau','Gémeaux','Cancer','Lion','Vierge','Balance','Scorpion','Sagittaire','Capricorne','Verseau','Poissons']
domiciles = [['Lion'],['Cancer'],['Gémeaux','Vierge'],['Balance','Taureau'],['Bélier','Scorpion'],['Sagittaire','Poissons'],['Capricorne','Verseau'],['Verseau'],['Poissons'],['Scorpion']]
df2 = pd.DataFrame(columns=['maison','signe','deg','pos1','pos2','pos3'])
df = pd.DataFrame(columns=['astre','jour','mois','annee','heure_naissance','min_ut','signe','deg','pos1','pos2','pos3','etat'])
df_points = pd.DataFrame(columns=['criteres','soleil','lune','mercure','venus','mars','jupiter','saturne','uranus','neptune','pluton'])
maitrises = [['Mars'],['Vénus'],['Mercure'],['Lune'],['Soleil'],['Mercure'],['Vénus'],['Pluton', 'Mars'],['Jupiter'],['Saturne'],['Uranus','Saturne'],['Neptune','Jupiter']]
points_ = 0
idx_planetes_rapidite = [1,2,3,0,4,5,6,7,8,9]
rapidite_planetes = [['Soleil',3],['Lune',0],['Mercure',1],['Vénus',2],['Mars',4],['Jupiter',5],['Saturne',6],['Uranus',7],['Neptune',8],['Pluton',9]]




def generateData(jour_naissance,mois_naissance,annee_naissance,heure_naissance,min_naissance,latitude,longitude):
    
    swe.set_ephe_path('/ephe')
    SE_GREG_CAL = 1
    gregflag = SE_GREG_CAL
    SEFLG_SPEED = int(256)
    iflag = SEFLG_SPEED

    JD = swe.utc_to_jd(annee_naissance,mois_naissance,jour_naissance,heure_naissance,min_naissance,0,1)
    natalUT = JD[1]

    # calcul des maisons
    houses = swe.houses(natalUT,latitude,longitude)

    for i in range (len(houses[0])):
        j = i+1;
        df2.loc[i,'maison'] = j
        df2.loc[i,'signe'] = get_sign(houses[0][i])
        df2.loc[i,'deg'] = houses[0][i]
        df2.loc[i,'pos1'] = get_sign_pos(swe.split_deg(houses[0][i],iflag)[0])
        df2.loc[i,'pos2'] = swe.split_deg(houses[0][i],1)[1]
        df2.loc[i,'pos3'] = swe.split_deg(houses[0][i],1)[2]
    
    # Mettre les astres
    
    astres = [0,1,2,3,4,5,6,7,8,9,11,12,13]
    idx=0
    for j in range(len(astres)):
        star = astres[j]
        coords = swe.calc_ut(natalUT,star,iflag)
        df.loc[idx,'astre'] = swe.get_planet_name(star)
        df.loc[idx,'jour'] = jour_naissance
        df.loc[idx,'mois'] = mois_naissance
        df.loc[idx,'annee'] = annee_naissance
        df.loc[idx,'heure_naissance'] = heure_naissance
        df.loc[idx,'min_ut'] = min_naissance
        df.loc[idx,'signe'] = get_sign(coords[0][0])
        df.loc[idx,'deg'] = coords[0][0]
        df.loc[idx,'pos1'] = get_sign_pos(swe.split_deg(coords[0][0],iflag)[0])
        df.loc[idx,'pos2'] = swe.split_deg(coords[0][0],iflag)[1]
        df.loc[idx,'pos3'] = swe.split_deg(coords[0][0],iflag)[2]


        if (coords[0][3] > 0):
            df.loc[idx,'etat'] = 'direct'
        elif (coords[0][3] < 0):
            df.loc[idx,'etat'] = 'retrograde'
        
        idx+= 1
    # ajout manuel du noeud sud
    signe_nn = df.loc[10]['signe']
    signe_ns = get_opp_sign(signe_nn)
    deg = get_pos_rev(signe_ns) + df.loc[10]['pos1'] + df.loc[10]['pos2']
    pos1 = df.loc[10]['pos1']
    pos2 = df.loc[10]['pos2']
    pos3 = df.loc[10]['pos3']
    etat = df.loc[10]['etat']

    df.loc[13] = ['desc. node', jour_naissance,mois_naissance,annee_naissance,heure_naissance,min_naissance,signe_ns,deg,pos1,pos2,pos3,etat]


    angle_max = 5
    points = 12
    posAsc = df2['deg'].loc[0]
    pos1 = posAsc
    df_points.loc[0] = ''
    df_points.iloc[0,0] = 'Conj. AC max 5°'
    for i in range(10):
        posPlanete = df['deg'].loc[i]
        points_ = trouve_points(pos1,posPlanete,points,angle_max)
        col = i+1
        df_points.iloc[0,col] = points_

    angle_max = 5
    points = 10
    posMC = df2['deg'].loc[9]
    pos1 = posMC
    df_points.loc[1] = ''
    df_points.iloc[1,0] = 'Conj. MC max 5°'

    for i in range(10):
        posPlanete = df['deg'].loc[i]
        points_ = trouve_points(pos1,posPlanete,points,angle_max)
        col = i+1
        df_points.iloc[1,col] = points_
    
    angle_max = 10
    points = 6
    posFC = df2['deg'].loc[3]
    pos1 = posFC
    df_points.loc[2] = ''
    df_points.iloc[2,0] = 'Conj. FC max 10°'

    for i in range(10):
        posPlanete = df['deg'].loc[i]
        points_ = trouve_points(pos1,posPlanete,points,angle_max)
        col = i+1
        df_points.iloc[2,col] = points_

    angle_max = 10
    points = 6
    posDS = df2['deg'].loc[6]
    pos1 = posDS
    df_points.loc[3] = ''
    df_points.iloc[3,0] = 'Conj. DS max 10°'

    for i in range(10):
        posPlanete = df['deg'].loc[i]
        points_ = trouve_points(pos1,posPlanete,points,angle_max)
        col = i+1
        df_points.iloc[3,col] = points_
    
    posM2 = df2.iloc[1,2]

    posMs = posM2
    points = 5
    df_points.loc[4] = ''
    df_points.iloc[4,0] = 'M1 | 5° - 10° AC'

    for i in range(10):
        posPlanete = df['deg'].loc[i]
        points_ = incl_maison(posAsc,posPlanete,posMs,points)
        col = i+1
        df_points.iloc[4,col] = points_
    
    posM11 = df2.iloc[10,2]

    posMs = posM11
    points = 5
    df_points.loc[5] = ''
    df_points.iloc[5,0] = 'M10 | 5° - 10° MC'

    for i in range(10):
        posPlanete = df['deg'].loc[i]
        points_ = incl_maison(posMC,posPlanete,posMs,points)
        col = i+1
        df_points.iloc[5,col] = points_
    
    points = 3
    df_points.loc[6] = ''
    df_points.iloc[6,0] = 'En domicile'

    for i in range(10):
        id_planete = i
        reponse_ = planete_domicile(id_planete)
        if (reponse_ == 'oui'):
            points_ = points
        else:
            points_ = 0
        col = i+1
        df_points.iloc[6,col] = points_
    
    df_points.loc[7] = ''
    df_points.iloc[7,0] = 'Aspect soleil'
    posSoleil = df['deg'].loc[0]
    pos1 = posSoleil
    for i in range(10):
        if (i != 0):
            posPlanete = df['deg'].loc[i]
            points_ = trouve_aspects_luminaires(pos1,posPlanete,2)
        else:
            points_ = 0
        col = i+1
        df_points.iloc[7,col] = points_

    df_points.loc[8] = ''
    df_points.iloc[8,0] = 'Aspect lune'
    posLune = df['deg'].loc[1]
    pos1 = posLune
    for i in range(10):
        if (i != 1):
            posPlanete = df['deg'].loc[i]
            points_ = trouve_aspects_luminaires(pos1,posPlanete,2)
        else:
            points_ = 0
        col = i+1
        df_points.iloc[8,col] = points_
    
    df_points.loc[9] = 0
    df_points.iloc[9,0] = 'Maître AC'
    pts = 3
    signeM1 = df2['signe'].loc[0]
    signeM2 = df2['signe'].loc[1]
    nombreAsc(signeM1,signeM2,9,pts)

    df_points.loc[10] = 0
    df_points.iloc[10,0] = 'Maître soleil'
    pts = 2
    signeSoleil = df['signe'].loc[0]
    maitreAsc(signeSoleil,1,10,pts)

    df_points.loc[11] = 0
    df_points.iloc[11,0] = 'Maître lune'
    pts = 2
    signeLune = df['signe'].loc[1]
    maitreAsc(signeLune,1,11,pts)

    df_points.loc[12] = 0
    df_points.iloc[12,0] = 'Maître gouverneur'
    pts = 2
    signeM1 = df2['signe'].loc[0]
    signeM2 = df2['signe'].loc[1]
    # qui sont le/les gouverneurs
    # signes ascendant
    signes_asc = signeAsc(signeM1,signeM2)
    
    maitres = []
    for i in range(len(signes_asc)):
        idxsigne = get_sign_idx(signes_asc[i])
        mtr_signe = maitrises[idxsigne]
        maitres.append(mtr_signe)
    for i in range(len(maitres)):
        for j in range(len(maitres[i])):
            astre = maitres[i][j]
            idx_astre = get_astre_idx(astre)
            signe_astre = df['signe'].loc[idx_astre]
            maitreGouv(signe_astre,1,12,pts)
    
    nb_aspects = ['Aspects majeurs']
    for i in range(10):
        nb_aspects.append(0)
        for j in range(10):
            points_astre = 0
            if j != i:
                planete1 = df['deg'].loc[i]
                planete2 = df['deg'].loc[j]
                
                if (0 <= i <= 1 or 0 <= j <= 1):
                    points = 0
                    points = trouve_aspects_luminaires(planete1,planete2,1)
                    points_astre += points
                else:
                    points = 0
                    points = trouve_aspects_planetes(planete1,planete2,1)
                    points_astre += points
                nb_aspects[i+1] += points_astre
    
    df_points.loc[13] = nb_aspects

    df_points.loc[14] = 0
    df_points.iloc[14,0] = 'Plusieurs maîtrises'
    points_ = 2
    # y a-t-il plusieurs planètes dans un signe
    df_cut = df[0:10].copy()

    for i in range(len(signes)):
        df_filtresigne = df_cut[df_cut['signe'] == signes[i]]

        nb_planetes = len(df_filtresigne)
        if (nb_planetes >= 2):
            points_ = nb_planetes * 2
            maitreGouv(signes[i],1,14,points_)
    
    df_points.loc[15] = 0
    df_points.iloc[15,0] = 'Aspect maître AC'
    points_ = 3
    i=0
    j=0

    for i in range(len(maitres)):
        for j in range(len(maitres[i])):
            maitre_s = maitres[i][j]
            id_maitre = get_astre_idx(maitre_s)
            posMaitre = df['deg'].loc[id_maitre]
            for k in range(10):
                if id_maitre != k:
                    planete2 = df['deg'].loc[k]
                    if (0 <= i <= 1 or 0 <= k <= 1):
                        points = trouve_aspects_luminaires(posMaitre,planete2,points_)
                        col = k + 1
                        df_points.iloc[15,col] = df_points.iloc[15,col] + points
                    else:
                        points = trouve_aspects_planetes(posMaitre,planete2,points_)
                        col = k + 1
                        df_points.iloc[15,col] = df_points.iloc[15,col] + points
    
    planete_moins_40 = []

    for i in range(10):
        posPlan1 = df['deg'].loc[i]
        astres_orbe = []
        for j in range(10):
            posPlan2 = df['deg'].loc[j]
            if (i != j):
                orbe_a = trouve_orbe(posPlan1,posPlan2)[0]
                orbe = orbe_a
                if (orbe <= 10):
                    astres_orbe.append(j)
        if(len(astres_orbe) >= 2):
            planete_moins_40.append(astres_orbe)

    planete_moins_40_rap = []
    for i in range(len(planete_moins_40)):
        interm = []
        for j in range(len(planete_moins_40[i])):
            idx = planete_moins_40[i][j]
            interm.append(rapidite_planetes[idx][1])
        planete_moins_40_rap.append(interm)
    
    amas = list(connected_components(planete_moins_40_rap))
    planetes_lentes_amas = []

    if len(amas) > 0:
      tab_val_max = []

      for i in range(len(amas)):
          val_max = max(amas[i])
          tab_val_max.append(val_max)

      if (len(tab_val_max)) > 1:
        val_max = max(tab_val_max)
      

      planetes_lentes_amas.append(idx_planetes_rapidite[val_max])
    
    df_points.loc[16] = 0
    df_points.iloc[16,0] = 'Planète lente amas'
    points_ = 3

    if (len(planetes_lentes_amas) > 0):

      for i in range(len(planetes_lentes_amas)):
          idx = planetes_lentes_amas[i] + 1
          df_points.iloc[16,idx] = points_

    df_points.loc[17] = 0
    df_points.iloc[17,0] = 'Maître Noeud Sud'
    points_ = 3
    signeNS = df['signe'].loc[13]
    maitreGouv(signeNS,1,17,points_)

    df_points.loc[18] = 0
    df_points.iloc[18,0] = 'Singleton'
    points_ = 6

    for i in range(10):
      signePlanete = df['signe'].loc[i]
      filtredf = df[0:10].copy()
      resultat = filtredf[filtredf['signe'] == signePlanete].copy()

      if(len(resultat) == 1):
        signesAdj = trouveSignesAdj(signePlanete)
        resultat2 = filtredf[(filtredf['signe'] == signesAdj[0]) | (filtredf['signe'] == signesAdj[1]) | (filtredf['signe'] == signesAdj[2]) | (filtredf['signe'] == signesAdj[3])].copy()
        
        if(len(resultat2)==0):
          df_points.iloc[18,i+1] = points_


    df_points.loc[19] = 0
    df_points.iloc[19,0] = "Total"
    df_points.iloc[19,1:11] = df_points.iloc[0:19,1:11].sum()
    df_points.iloc[19,1:11] = df_points.iloc[19,1:11].apply(lambda x: round(x))

    total = df_points.loc[19].copy()
    total = total[1:]
    total = total.sum()

    df_points.loc[20] = 0
    df_points.iloc[20,0] = "Pourcentage"
    df_points.iloc[20,1:11] = df_points.iloc[19,1:11].apply(lambda x: round((x/total*100),1))

    file_name = random.randint(0, 10000)
    path_name = 'static/temp/{}.csv'.format(file_name)

    df_points.to_csv(path_name)

    return [path_name]

def get_sign(degrees):
  if (degrees < 30):
    return "Bélier";
  elif (degrees >= 30 and degrees < 60):
    return "Taureau";
  elif (degrees >= 60 and degrees < 90):
    return "Gémeaux";
  elif (degrees >= 90 and degrees < 120):
    return "Cancer";
  elif (degrees >= 120 and degrees < 150):
    return "Lion";
  elif (degrees >= 150 and degrees < 180):
    return "Vierge";
  elif (degrees >= 180 and degrees < 210):
    return "Balance";
  elif (degrees >= 210 and degrees < 240):
    return "Scorpion";
  elif (degrees >= 240 and degrees < 270):
    return "Sagittaire";
  elif (degrees >= 270 and degrees < 300):
    return "Capricorne";
  elif (degrees >= 300 and degrees < 330):
    return "Verseau";
  elif (degrees >= 330 and degrees < 360):
    return "Poissons";

def get_sign_pos(degrees):
  if (degrees < 30):
    return degrees;
  elif (degrees >= 30 and degrees < 60):
    return degrees - 30;
  elif (degrees >= 60 and degrees < 90):
    return degrees - 60;
  elif (degrees >= 90 and degrees < 120):
    return degrees - 90;
  elif (degrees >= 120 and degrees < 150):
    return degrees - 120;
  elif (degrees >= 150 and degrees < 180):
    return degrees - 150;
  elif (degrees >= 180 and degrees < 210):
    return degrees - 180;
  elif (degrees >= 210 and degrees < 240):
    return degrees - 210;
  elif (degrees >= 240 and degrees < 270):
    return degrees - 240;
  elif (degrees >= 270 and degrees < 300):
    return degrees - 270;
  elif (degrees >= 300 and degrees < 330):
    return degrees - 300;
  elif (degrees >= 330 and degrees < 360):
    return degrees - 330;

def get_pos_rev(signe):
  if (signe == "Bélier"):
    return 0
  elif (signe == "Taureau"):
    return 30
  elif (signe == "Gémeaux"):
    return 60
  elif (signe == "Cancer"):
    return 90
  elif (signe == "Lion"):
    return 120
  elif (signe == "Vierge"):
    return 150
  elif (signe == "Balance"):
    return 180
  elif (signe == "Scorpion"):
    return 210
  elif (signe == "Sagittaire"):
    return 240
  elif (signe == "Capricorne"):
    return 270
  elif (signe == "Verseau"):
    return 300
  elif (signe == "Poissons"):
    return 330

def get_sign_idx(signe):
  if (signe == "Bélier"):
    return 0
  elif (signe == "Taureau"):
    return 1
  elif (signe == "Gémeaux"):
    return 2
  elif (signe == "Cancer"):
    return 3
  elif (signe == "Lion"):
    return 4
  elif (signe == "Vierge"):
    return 5
  elif (signe == "Balance"):
    return 6
  elif (signe == "Scorpion"):
    return 7
  elif (signe == "Sagittaire"):
    return 8
  elif (signe == "Capricorne"):
    return 9
  elif (signe == "Verseau"):
    return 10
  elif (signe == "Poissons"):
    return 11

def get_astre_idx(astre):
  if (astre == "Soleil"):
    return 0
  elif (astre == "Lune"):
    return 1
  elif (astre == "Mercure"):
    return 2
  elif (astre == "Vénus"):
    return 3
  elif (astre == "Mars"):
    return 4
  elif (astre == "Jupiter"):
    return 5
  elif (astre == "Saturne"):
    return 6
  elif (astre == "Uranus"):
    return 7
  elif (astre == "Neptune"):
    return 8
  elif (astre == "Pluton"):
    return 9

def get_opp_sign(signe):
  if (signe == "Bélier"):
    return "Balance"
  elif (signe == "Taureau"):
    return "Scorpion"
  elif (signe == "Gémeaux"):
    return "Sagittaire"
  elif (signe == "Cancer"):
    return "Capricorne"
  elif (signe == "Lion"):
    return "Verseau"
  elif (signe == "Vierge"):
    return "Poissons"
  elif (signe=="Balance"):
    return "Bélier"
  elif (signe == "Scorpion"):
    return "Taureau"
  elif (signe == "Sagittaire"):
    return "Gémeaux"
  elif (signe == "Capricorne"):
    return "Cancer"
  elif (signe == "Verseau"):
    return "Lion"
  elif (signe == "Poissons"):
    return "Vierge"

def find_score(astre):
  if (astre == 'Sun' or astre == 'Moon'):
    return 4
  elif (astre == 'Mercury' or astre == 'Venus' or astre == 'Mars' or astre == 'desc. node' ):
    return 3
  elif (astre == 'Saturn' or astre == 'Jupiter'):
    return 2
  elif (astre == 'Uranus' or astre == 'Neptune' or astre == 'Pluto'):
    return 1
  else:
    return 0

def dominantes(signe,score):
  if (signe == signes[0]):
    score_signes[0] += score
    score_elements[0] += score
    score_modes[0] += score
    score_jour_nuit[0] += 720
    score_jour_nuit[1] += 720

  elif (signe == signes[1]):
    score_signes[1] += score
    score_elements[1] += score
    score_modes[1] += score
    score_jour_nuit[0] += 840
    score_jour_nuit[1] += 600
  
  elif (signe == signes[2]):
    score_signes[2] += score
    score_elements[2] += score
    score_modes[2] += score
    score_jour_nuit[0] += 930
    score_jour_nuit[1] += 510

  elif (signe == signes[3]):
    score_signes[3] += score
    score_elements[3] += score
    score_modes[0] += score
    score_jour_nuit[0] += 960
    score_jour_nuit[1] += 480
  
  elif (signe == signes[4]):
    score_signes[4] += score
    score_elements[0] += score
    score_modes[1] += score
    score_jour_nuit[0] += 930
    score_jour_nuit[1] += 510

  elif (signe == signes[5]):
    score_signes[5] += score
    score_elements[1] += score
    score_modes[2] += score
    score_jour_nuit[0] += 840
    score_jour_nuit[1] += 600

  elif (signe == signes[6]):
    score_signes[6] += score
    score_elements[2] += score
    score_modes[0] += score
    score_jour_nuit[0] += 720
    score_jour_nuit[1] += 720
  
  elif (signe == signes[7]):
    score_signes[7] += score
    score_elements[3] += score
    score_modes[1] += score
    score_jour_nuit[0] += 600
    score_jour_nuit[1] += 840
  
  elif (signe == signes[8]):
    score_signes[8] += score
    score_elements[0] += score
    score_modes[2] += score
    score_jour_nuit[0] += 510
    score_jour_nuit[1] += 930
  
  elif (signe == signes[9]):
    score_signes[9] += score
    score_elements[1] += score
    score_modes[0] += score
    score_jour_nuit[0] += 480
    score_jour_nuit[1] += 960

  elif (signe == signes[10]):
    score_signes[10] += score
    score_elements[2] += score
    score_modes[1] += score
    score_jour_nuit[0] += 510
    score_jour_nuit[1] += 930
  
  elif (signe == signes[11]):
    score_signes[11] += score
    score_elements[3] += score
    score_modes[2] += score
    score_jour_nuit[0] += 600
    score_jour_nuit[1] += 840

def trouve_orbe(plRef,pl2):
  orbe = plRef - pl2
  if (orbe < 0):
    pos_plRef = 'devant'
  else:
    pos_plRef = 'derrière'
  if (abs(orbe) > 180):
    orbe = 360 - abs(orbe)
  return [abs(orbe), pos_plRef]

def trouve_points(plRef,pl2,pts,angle_max):
  reponse = trouve_orbe(plRef,pl2)
  if (reponse[0] <= angle_max):
    points_f = pts
  else:
    points_f = 0
  return points_f

def incl_maison(plRef,pl2,posMs,pts):
  reponse = trouve_orbe(plRef,pl2)
  if (5 < reponse[0] <= 10 and reponse[1] == 'devant'):
    reponse2 = trouve_orbe(posMs,pl2)
    if (reponse2[1] == 'derrière'):
      points_f = pts
    else:
      points_f = 0
  else:
    points_f = 0
  return points_f

def planete_domicile(planete_id):
  planete = rapidite_planetes[planete_id][0]
  signe_planete = df['signe'].loc[planete_id]
  idx_signe = get_sign_idx(signe_planete)
  signe_domicile = maitrises[idx_signe]
  for i in range(len(signe_domicile)):
    if (signe_domicile[i] == planete):
      reponse = 'oui'
      break
    else:
      reponse = 'non'
  return reponse

def trouve_aspects_luminaires(plRef,pl2,nbp):
  points = 0
  reponse = trouve_orbe(plRef,pl2)
  orbe = abs(reponse[0])
  orbe = round(orbe)
  ajout_points = nbp
  if ( orbe <= 12 ):
    points += ajout_points
  if ( 56 <= orbe <= 64):
    points += ajout_points
  if (83 <= orbe <= 97):
    points+= ajout_points
  if (112 <= orbe <= 128):
    points+= ajout_points
  if (170 <= orbe <= 190):
    points += ajout_points
  return points

def trouve_aspects_planetes(plRef,pl2,nbp):
  points = 0
  reponse = trouve_orbe(plRef,pl2)
  orbe = abs(reponse[0])
  orbe = round(orbe)
  ajout_points = nbp
  if ( orbe <= 10 ):
    points += ajout_points
  if ( 56 <= orbe <= 64):
    points += ajout_points
  if (83 <= orbe <= 97):
    points+= ajout_points
  if (112 <= orbe <= 128):
    points+= ajout_points
  if (170 <= orbe <= 190):
    points += ajout_points
  return points

def maitreAsc(signeAsc,nbAsc,ligne,pts):
  # trouver l'idx signe asc
  if (nbAsc == 1):
    idx_signe = get_sign_idx(signeAsc)
    maitrises_signe = maitrises[idx_signe].copy()
    # ajouter les points
    idx_maitrises_signe = []
    for i in range(len(maitrises_signe)):
      # trouver l'idx de l'astre
      id_astre = get_astre_idx(maitrises_signe[i])
      idx_maitrises_signe.append(id_astre)
    for i in range(len(idx_maitrises_signe)):
      col = idx_maitrises_signe[i]+1
      df_points.iloc[ligne,col] = pts
  
  if (nbAsc == 2):
    idx_signe1 = get_sign_idx(signeAsc)
    if (idx_signe1 == 11):
      idx_signe2 = 0
    else:
      idx_signe2 = idx_signe1 + 1
    
    maitrises_signes = []
    maitrises_signe1 = maitrises[idx_signe1].copy()
    maitrises_signes.append(maitrises_signe1)
    maitrises_signe2 = maitrises[idx_signe2].copy()
    maitrises_signes.append(maitrises_signe2)
    idx_maitrises_signe = []
    
    for i in range(len(maitrises_signes)):
      for j in range(len(maitrises_signes[i])):
        signe = maitrises_signes[i][j]
        id_astre = get_astre_idx(signe)
        idx_maitrises_signe.append(id_astre)
    for i in range(len(idx_maitrises_signe)):
      col = idx_maitrises_signe[i] + 1
      df_points.iloc[ligne,col] = df_points.iloc[ligne,col] + pts
     

def maitreGouv(signeAsc,nbAsc,ligne,pts):
    # trouver l'idx signe asc
  if (nbAsc == 1):
    idx_signe = get_sign_idx(signeAsc)
    maitrises_signe = maitrises[idx_signe].copy()
    # ajouter les points
    idx_maitrises_signe = []
    for i in range(len(maitrises_signe)):
      # trouver l'idx de l'astre
      id_astre = get_astre_idx(maitrises_signe[i])
      idx_maitrises_signe.append(id_astre)
    for i in range(len(idx_maitrises_signe)):
      col = idx_maitrises_signe[i]+1
      df_points.iloc[ligne,col] = df_points.iloc[ligne,col] + pts
  
  if (nbAsc == 2):
    idx_signe1 = get_sign_idx(signeAsc)
    if (idx_signe1 == 11):
      idx_signe2 = 0
    else:
      idx_signe2 = idx_signe1 + 1
    maitrises_signes = []
    maitrises_signe1 = maitrises[idx_signe1].copy()
    maitrises_signes.append(maitrises_signe1)
    maitrises_signe2 = maitrises[idx_signe2].copy()
    maitrises_signes.append(maitrises_signe2)
    idx_maitrises_signe = []
    for i in range(len(maitrises_signes)):
      for j in range(len(maitrises_signes[i])):
        signe = maitrises_signes[i][j]
        id_astre = get_astre_idx(signe)
        idx_maitrises_signe.append(id_astre)
    for i in range(len(idx_maitrises_signe)):
      col = idx_maitrises_signe[i] + 1
      df_points.iloc[ligne,col] = df_points.iloc[ligne,col] + pts

def nombreAsc(signeM1,signeM2,ligne,pts):
  idxsigneM1 = get_sign_idx(signeM1)
  idxsigneM2 = get_sign_idx(signeM2)

  if (idxsigneM1 == 11):
    idxsigneM1 = -1

  if (idxsigneM2 == idxsigneM1):
    maitreAsc(signeM1,1,ligne,pts)
  elif (idxsigneM2 == idxsigneM1 + 1):
    maitreAsc(signeM1,1,ligne,pts)
  elif (idxsigneM2 == idxsigneM1 + 2):
    maitreAsc(signeM1,2,ligne,pts)

# Afficher le ou les signes de l'ascendant
def signeAsc(signeM1,signeM2):
  idxsigneM1 = get_sign_idx(signeM1)
  idxsigneM2 = get_sign_idx(signeM2)

  if (idxsigneM1 == 11):
    idxsigneM1 = -1

  if (idxsigneM2 == idxsigneM1 ):
    return [signeM1]
  if (idxsigneM2 == idxsigneM1 + 1):
    return [signeM1]
  elif (idxsigneM2 == idxsigneM1 + 2):
    idxsigneasc2 = idxsigneM1 + 1
    signe2 = signes[idxsigneasc2]
    return [signeM1,signe2]

def connected_components(lists):
    neighbors = defaultdict(set)
    seen = set()
    for each in lists:
        for item in each:
            neighbors[item].update(each)
    def component(node, neighbors=neighbors, seen=seen, see=seen.add):
        nodes = set([node])
        next_node = nodes.pop
        while nodes:
            node = next_node()
            see(node)
            nodes |= neighbors[node] - seen
            yield node
    for node in neighbors:
        if node not in seen:
            yield sorted(component(node))

def corrIdxSigne(idx):
  if (idx > 11):
    idxCorr = idx - 11
  elif (idx < 0):
    idxCorr = 12 - abs(idx)
  else:
    idxCorr = idx
  return idxCorr

def trouveSignesAdj(signe):
  idx_signe = get_sign_idx(signe)
  idx_signe1 = corrIdxSigne(idx_signe-1)
  idx_signe2 = corrIdxSigne(idx_signe-2)
  idx_signe3 = corrIdxSigne(idx_signe+1)
  idx_signe4 = corrIdxSigne(idx_signe+2)
  return [signes[idx_signe1],signes[idx_signe2],signes[idx_signe3],signes[idx_signe4]]

