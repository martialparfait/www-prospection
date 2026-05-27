"""
Configure le Google Sheet 15Du4fIou9cOOMA5CjTz6aAtP3teTtewWd_YMU7I8Xm0 :
  - Onglet "Catégories"   : liste des catégories (créé une seule fois)
  - Onglet "Pays"         : liste ISO 3166-1 (~200 pays)
  - Onglet "Régions"      : provinces / Länder / régions + villes principales
                            pour Belgique, France, Espagne, Allemagne
  - Onglet "Établissements": structure vide (en-têtes uniquement)

Authentification :
    export GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/service_account.json
    (et partage le Sheet en édition avec l'email de la SA)
"""

import os
import sys

import gspread
from gspread.exceptions import WorksheetNotFound


SPREADSHEET_ID = "15Du4fIou9cOOMA5CjTz6aAtP3teTtewWd_YMU7I8Xm0"

# --------------------------------------------------------------------------- #
# Catégories
# --------------------------------------------------------------------------- #

CATEGORIES = [
    "Dance",
    "Fitness",
    "Golf",
    "Massage - Spa",
    "Pilates",
    "Pool - Aqua",
    "Volleyball - Sports",
    "Yoga Studio",
    "CrossFit & Functional Training",
    "Dojo (Arts martiaux)",
    "Tennis & Padel Club",
    "Cycling & Spinning Studio",
    "Boxing & Kickboxing",
    "Climbing Wall",
    "Running Club",
    "Hôtel avec Spa & Piscine",
    "Hôtel avec Spa",
    "Hôtel avec Piscine",
    "Wellness Retreat",
    "Thalassothérapie & Bains thermaux",
    "Cryothérapie & Récupération sportive",
    "Sauna & Hammam",
    "Flottaison (Float Tank)",
    "Kinésithérapie & Ostéopathie",
    "Coaching Sportif Privé",
    "Diététique & Nutrition Sportive",
]

# --------------------------------------------------------------------------- #
# Pays — ISO 3166-1 (FR | ISO 2 | ISO 3 | Continent | Capitale)
# --------------------------------------------------------------------------- #

PAYS = [
    # Afrique
    ("Afrique du Sud", "ZA", "ZAF", "Afrique", "Pretoria"),
    ("Algérie", "DZ", "DZA", "Afrique", "Alger"),
    ("Angola", "AO", "AGO", "Afrique", "Luanda"),
    ("Bénin", "BJ", "BEN", "Afrique", "Porto-Novo"),
    ("Botswana", "BW", "BWA", "Afrique", "Gaborone"),
    ("Burkina Faso", "BF", "BFA", "Afrique", "Ouagadougou"),
    ("Burundi", "BI", "BDI", "Afrique", "Gitega"),
    ("Cameroun", "CM", "CMR", "Afrique", "Yaoundé"),
    ("Cap-Vert", "CV", "CPV", "Afrique", "Praia"),
    ("République centrafricaine", "CF", "CAF", "Afrique", "Bangui"),
    ("Comores", "KM", "COM", "Afrique", "Moroni"),
    ("République du Congo", "CG", "COG", "Afrique", "Brazzaville"),
    ("République démocratique du Congo", "CD", "COD", "Afrique", "Kinshasa"),
    ("Côte d'Ivoire", "CI", "CIV", "Afrique", "Yamoussoukro"),
    ("Djibouti", "DJ", "DJI", "Afrique", "Djibouti"),
    ("Égypte", "EG", "EGY", "Afrique", "Le Caire"),
    ("Érythrée", "ER", "ERI", "Afrique", "Asmara"),
    ("Eswatini", "SZ", "SWZ", "Afrique", "Mbabane"),
    ("Éthiopie", "ET", "ETH", "Afrique", "Addis-Abeba"),
    ("Gabon", "GA", "GAB", "Afrique", "Libreville"),
    ("Gambie", "GM", "GMB", "Afrique", "Banjul"),
    ("Ghana", "GH", "GHA", "Afrique", "Accra"),
    ("Guinée", "GN", "GIN", "Afrique", "Conakry"),
    ("Guinée-Bissau", "GW", "GNB", "Afrique", "Bissau"),
    ("Guinée équatoriale", "GQ", "GNQ", "Afrique", "Malabo"),
    ("Kenya", "KE", "KEN", "Afrique", "Nairobi"),
    ("Lesotho", "LS", "LSO", "Afrique", "Maseru"),
    ("Libéria", "LR", "LBR", "Afrique", "Monrovia"),
    ("Libye", "LY", "LBY", "Afrique", "Tripoli"),
    ("Madagascar", "MG", "MDG", "Afrique", "Antananarivo"),
    ("Malawi", "MW", "MWI", "Afrique", "Lilongwe"),
    ("Mali", "ML", "MLI", "Afrique", "Bamako"),
    ("Maroc", "MA", "MAR", "Afrique", "Rabat"),
    ("Maurice", "MU", "MUS", "Afrique", "Port-Louis"),
    ("Mauritanie", "MR", "MRT", "Afrique", "Nouakchott"),
    ("Mozambique", "MZ", "MOZ", "Afrique", "Maputo"),
    ("Namibie", "NA", "NAM", "Afrique", "Windhoek"),
    ("Niger", "NE", "NER", "Afrique", "Niamey"),
    ("Nigeria", "NG", "NGA", "Afrique", "Abuja"),
    ("Ouganda", "UG", "UGA", "Afrique", "Kampala"),
    ("Rwanda", "RW", "RWA", "Afrique", "Kigali"),
    ("São Tomé-et-Principe", "ST", "STP", "Afrique", "São Tomé"),
    ("Sénégal", "SN", "SEN", "Afrique", "Dakar"),
    ("Seychelles", "SC", "SYC", "Afrique", "Victoria"),
    ("Sierra Leone", "SL", "SLE", "Afrique", "Freetown"),
    ("Somalie", "SO", "SOM", "Afrique", "Mogadiscio"),
    ("Soudan", "SD", "SDN", "Afrique", "Khartoum"),
    ("Soudan du Sud", "SS", "SSD", "Afrique", "Djouba"),
    ("Tanzanie", "TZ", "TZA", "Afrique", "Dodoma"),
    ("Tchad", "TD", "TCD", "Afrique", "N'Djamena"),
    ("Togo", "TG", "TGO", "Afrique", "Lomé"),
    ("Tunisie", "TN", "TUN", "Afrique", "Tunis"),
    ("Zambie", "ZM", "ZMB", "Afrique", "Lusaka"),
    ("Zimbabwe", "ZW", "ZWE", "Afrique", "Harare"),

    # Amérique
    ("Antigua-et-Barbuda", "AG", "ATG", "Amérique", "Saint John's"),
    ("Argentine", "AR", "ARG", "Amérique", "Buenos Aires"),
    ("Bahamas", "BS", "BHS", "Amérique", "Nassau"),
    ("Barbade", "BB", "BRB", "Amérique", "Bridgetown"),
    ("Belize", "BZ", "BLZ", "Amérique", "Belmopan"),
    ("Bolivie", "BO", "BOL", "Amérique", "Sucre"),
    ("Brésil", "BR", "BRA", "Amérique", "Brasilia"),
    ("Canada", "CA", "CAN", "Amérique", "Ottawa"),
    ("Chili", "CL", "CHL", "Amérique", "Santiago"),
    ("Colombie", "CO", "COL", "Amérique", "Bogota"),
    ("Costa Rica", "CR", "CRI", "Amérique", "San José"),
    ("Cuba", "CU", "CUB", "Amérique", "La Havane"),
    ("Dominique", "DM", "DMA", "Amérique", "Roseau"),
    ("République dominicaine", "DO", "DOM", "Amérique", "Saint-Domingue"),
    ("Équateur", "EC", "ECU", "Amérique", "Quito"),
    ("États-Unis", "US", "USA", "Amérique", "Washington"),
    ("Grenade", "GD", "GRD", "Amérique", "Saint-Georges"),
    ("Guatemala", "GT", "GTM", "Amérique", "Guatemala"),
    ("Guyana", "GY", "GUY", "Amérique", "Georgetown"),
    ("Haïti", "HT", "HTI", "Amérique", "Port-au-Prince"),
    ("Honduras", "HN", "HND", "Amérique", "Tegucigalpa"),
    ("Jamaïque", "JM", "JAM", "Amérique", "Kingston"),
    ("Mexique", "MX", "MEX", "Amérique", "Mexico"),
    ("Nicaragua", "NI", "NIC", "Amérique", "Managua"),
    ("Panama", "PA", "PAN", "Amérique", "Panama"),
    ("Paraguay", "PY", "PRY", "Amérique", "Asunción"),
    ("Pérou", "PE", "PER", "Amérique", "Lima"),
    ("Saint-Kitts-et-Nevis", "KN", "KNA", "Amérique", "Basseterre"),
    ("Sainte-Lucie", "LC", "LCA", "Amérique", "Castries"),
    ("Saint-Vincent-et-les-Grenadines", "VC", "VCT", "Amérique", "Kingstown"),
    ("Salvador", "SV", "SLV", "Amérique", "San Salvador"),
    ("Suriname", "SR", "SUR", "Amérique", "Paramaribo"),
    ("Trinité-et-Tobago", "TT", "TTO", "Amérique", "Port-d'Espagne"),
    ("Uruguay", "UY", "URY", "Amérique", "Montevideo"),
    ("Venezuela", "VE", "VEN", "Amérique", "Caracas"),

    # Asie
    ("Afghanistan", "AF", "AFG", "Asie", "Kaboul"),
    ("Arabie saoudite", "SA", "SAU", "Asie", "Riyad"),
    ("Arménie", "AM", "ARM", "Asie", "Erevan"),
    ("Azerbaïdjan", "AZ", "AZE", "Asie", "Bakou"),
    ("Bahreïn", "BH", "BHR", "Asie", "Manama"),
    ("Bangladesh", "BD", "BGD", "Asie", "Dacca"),
    ("Bhoutan", "BT", "BTN", "Asie", "Thimphou"),
    ("Birmanie", "MM", "MMR", "Asie", "Naypyidaw"),
    ("Brunei", "BN", "BRN", "Asie", "Bandar Seri Begawan"),
    ("Cambodge", "KH", "KHM", "Asie", "Phnom Penh"),
    ("Chine", "CN", "CHN", "Asie", "Pékin"),
    ("Corée du Nord", "KP", "PRK", "Asie", "Pyongyang"),
    ("Corée du Sud", "KR", "KOR", "Asie", "Séoul"),
    ("Émirats arabes unis", "AE", "ARE", "Asie", "Abou Dabi"),
    ("Géorgie", "GE", "GEO", "Asie", "Tbilissi"),
    ("Hong Kong", "HK", "HKG", "Asie", "Hong Kong"),
    ("Inde", "IN", "IND", "Asie", "New Delhi"),
    ("Indonésie", "ID", "IDN", "Asie", "Jakarta"),
    ("Irak", "IQ", "IRQ", "Asie", "Bagdad"),
    ("Iran", "IR", "IRN", "Asie", "Téhéran"),
    ("Israël", "IL", "ISR", "Asie", "Jérusalem"),
    ("Japon", "JP", "JPN", "Asie", "Tokyo"),
    ("Jordanie", "JO", "JOR", "Asie", "Amman"),
    ("Kazakhstan", "KZ", "KAZ", "Asie", "Astana"),
    ("Kirghizstan", "KG", "KGZ", "Asie", "Bichkek"),
    ("Koweït", "KW", "KWT", "Asie", "Koweït"),
    ("Laos", "LA", "LAO", "Asie", "Vientiane"),
    ("Liban", "LB", "LBN", "Asie", "Beyrouth"),
    ("Macao", "MO", "MAC", "Asie", "Macao"),
    ("Malaisie", "MY", "MYS", "Asie", "Kuala Lumpur"),
    ("Maldives", "MV", "MDV", "Asie", "Malé"),
    ("Mongolie", "MN", "MNG", "Asie", "Oulan-Bator"),
    ("Népal", "NP", "NPL", "Asie", "Katmandou"),
    ("Oman", "OM", "OMN", "Asie", "Mascate"),
    ("Ouzbékistan", "UZ", "UZB", "Asie", "Tachkent"),
    ("Pakistan", "PK", "PAK", "Asie", "Islamabad"),
    ("Palestine", "PS", "PSE", "Asie", "Ramallah"),
    ("Philippines", "PH", "PHL", "Asie", "Manille"),
    ("Qatar", "QA", "QAT", "Asie", "Doha"),
    ("Singapour", "SG", "SGP", "Asie", "Singapour"),
    ("Sri Lanka", "LK", "LKA", "Asie", "Colombo"),
    ("Syrie", "SY", "SYR", "Asie", "Damas"),
    ("Tadjikistan", "TJ", "TJK", "Asie", "Douchanbé"),
    ("Taïwan", "TW", "TWN", "Asie", "Taipei"),
    ("Thaïlande", "TH", "THA", "Asie", "Bangkok"),
    ("Timor oriental", "TL", "TLS", "Asie", "Dili"),
    ("Turkménistan", "TM", "TKM", "Asie", "Achgabat"),
    ("Turquie", "TR", "TUR", "Asie", "Ankara"),
    ("Vietnam", "VN", "VNM", "Asie", "Hanoï"),
    ("Yémen", "YE", "YEM", "Asie", "Sanaa"),

    # Europe
    ("Albanie", "AL", "ALB", "Europe", "Tirana"),
    ("Allemagne", "DE", "DEU", "Europe", "Berlin"),
    ("Andorre", "AD", "AND", "Europe", "Andorre-la-Vieille"),
    ("Autriche", "AT", "AUT", "Europe", "Vienne"),
    ("Belgique", "BE", "BEL", "Europe", "Bruxelles"),
    ("Biélorussie", "BY", "BLR", "Europe", "Minsk"),
    ("Bosnie-Herzégovine", "BA", "BIH", "Europe", "Sarajevo"),
    ("Bulgarie", "BG", "BGR", "Europe", "Sofia"),
    ("Chypre", "CY", "CYP", "Europe", "Nicosie"),
    ("Croatie", "HR", "HRV", "Europe", "Zagreb"),
    ("Danemark", "DK", "DNK", "Europe", "Copenhague"),
    ("Espagne", "ES", "ESP", "Europe", "Madrid"),
    ("Estonie", "EE", "EST", "Europe", "Tallinn"),
    ("Finlande", "FI", "FIN", "Europe", "Helsinki"),
    ("France", "FR", "FRA", "Europe", "Paris"),
    ("Grèce", "GR", "GRC", "Europe", "Athènes"),
    ("Hongrie", "HU", "HUN", "Europe", "Budapest"),
    ("Irlande", "IE", "IRL", "Europe", "Dublin"),
    ("Islande", "IS", "ISL", "Europe", "Reykjavík"),
    ("Italie", "IT", "ITA", "Europe", "Rome"),
    ("Kosovo", "XK", "XKX", "Europe", "Pristina"),
    ("Lettonie", "LV", "LVA", "Europe", "Riga"),
    ("Liechtenstein", "LI", "LIE", "Europe", "Vaduz"),
    ("Lituanie", "LT", "LTU", "Europe", "Vilnius"),
    ("Luxembourg", "LU", "LUX", "Europe", "Luxembourg"),
    ("Macédoine du Nord", "MK", "MKD", "Europe", "Skopje"),
    ("Malte", "MT", "MLT", "Europe", "La Valette"),
    ("Moldavie", "MD", "MDA", "Europe", "Chișinău"),
    ("Monaco", "MC", "MCO", "Europe", "Monaco"),
    ("Monténégro", "ME", "MNE", "Europe", "Podgorica"),
    ("Norvège", "NO", "NOR", "Europe", "Oslo"),
    ("Pays-Bas", "NL", "NLD", "Europe", "Amsterdam"),
    ("Pologne", "PL", "POL", "Europe", "Varsovie"),
    ("Portugal", "PT", "PRT", "Europe", "Lisbonne"),
    ("République tchèque", "CZ", "CZE", "Europe", "Prague"),
    ("Roumanie", "RO", "ROU", "Europe", "Bucarest"),
    ("Royaume-Uni", "GB", "GBR", "Europe", "Londres"),
    ("Russie", "RU", "RUS", "Europe", "Moscou"),
    ("Saint-Marin", "SM", "SMR", "Europe", "Saint-Marin"),
    ("Serbie", "RS", "SRB", "Europe", "Belgrade"),
    ("Slovaquie", "SK", "SVK", "Europe", "Bratislava"),
    ("Slovénie", "SI", "SVN", "Europe", "Ljubljana"),
    ("Suède", "SE", "SWE", "Europe", "Stockholm"),
    ("Suisse", "CH", "CHE", "Europe", "Berne"),
    ("Ukraine", "UA", "UKR", "Europe", "Kiev"),
    ("Vatican", "VA", "VAT", "Europe", "Vatican"),

    # Océanie
    ("Australie", "AU", "AUS", "Océanie", "Canberra"),
    ("Fidji", "FJ", "FJI", "Océanie", "Suva"),
    ("Îles Marshall", "MH", "MHL", "Océanie", "Majuro"),
    ("Îles Salomon", "SB", "SLB", "Océanie", "Honiara"),
    ("Kiribati", "KI", "KIR", "Océanie", "Tarawa"),
    ("Micronésie", "FM", "FSM", "Océanie", "Palikir"),
    ("Nauru", "NR", "NRU", "Océanie", "Yaren"),
    ("Nouvelle-Zélande", "NZ", "NZL", "Océanie", "Wellington"),
    ("Palaos", "PW", "PLW", "Océanie", "Ngerulmud"),
    ("Papouasie-Nouvelle-Guinée", "PG", "PNG", "Océanie", "Port Moresby"),
    ("Samoa", "WS", "WSM", "Océanie", "Apia"),
    ("Tonga", "TO", "TON", "Océanie", "Nukualofa"),
    ("Tuvalu", "TV", "TUV", "Océanie", "Funafuti"),
    ("Vanuatu", "VU", "VUT", "Océanie", "Port-Vila"),
]

# --------------------------------------------------------------------------- #
# Régions — (Région, Province/Subdivision, Ville, Code postal, Pays)
#   Belgique : Région | Province
#   France   : Région | Département
#   Espagne  : Communauté autonome | Province
#   Allemagne: Land    | (vide)
# --------------------------------------------------------------------------- #

REGIONS = [
    # ---------- BELGIQUE ----------
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Bruxelles", "1000", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Ixelles", "1050", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Schaerbeek", "1030", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Uccle", "1180", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Anderlecht", "1070", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Etterbeek", "1040", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Saint-Gilles", "1060", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Woluwe-Saint-Lambert", "1200", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Woluwe-Saint-Pierre", "1150", "Belgique"),
    ("Région de Bruxelles-Capitale", "Bruxelles-Capitale", "Forest", "1190", "Belgique"),
    ("Région flamande", "Anvers", "Anvers", "2000", "Belgique"),
    ("Région flamande", "Anvers", "Malines", "2800", "Belgique"),
    ("Région flamande", "Anvers", "Turnhout", "2300", "Belgique"),
    ("Région flamande", "Anvers", "Lierre", "2500", "Belgique"),
    ("Région flamande", "Anvers", "Geel", "2440", "Belgique"),
    ("Région flamande", "Limbourg", "Hasselt", "3500", "Belgique"),
    ("Région flamande", "Limbourg", "Genk", "3600", "Belgique"),
    ("Région flamande", "Limbourg", "Saint-Trond", "3800", "Belgique"),
    ("Région flamande", "Limbourg", "Tongres", "3700", "Belgique"),
    ("Région flamande", "Flandre orientale", "Gand", "9000", "Belgique"),
    ("Région flamande", "Flandre orientale", "Alost", "9300", "Belgique"),
    ("Région flamande", "Flandre orientale", "Saint-Nicolas", "9100", "Belgique"),
    ("Région flamande", "Flandre orientale", "Termonde", "9200", "Belgique"),
    ("Région flamande", "Flandre orientale", "Audenarde", "9700", "Belgique"),
    ("Région flamande", "Flandre occidentale", "Bruges", "8000", "Belgique"),
    ("Région flamande", "Flandre occidentale", "Courtrai", "8500", "Belgique"),
    ("Région flamande", "Flandre occidentale", "Ostende", "8400", "Belgique"),
    ("Région flamande", "Flandre occidentale", "Roulers", "8800", "Belgique"),
    ("Région flamande", "Flandre occidentale", "Ypres", "8900", "Belgique"),
    ("Région flamande", "Flandre occidentale", "Knokke-Heist", "8300", "Belgique"),
    ("Région flamande", "Brabant flamand", "Louvain", "3000", "Belgique"),
    ("Région flamande", "Brabant flamand", "Vilvorde", "1800", "Belgique"),
    ("Région flamande", "Brabant flamand", "Hal", "1500", "Belgique"),
    ("Région flamande", "Brabant flamand", "Tirlemont", "3300", "Belgique"),
    ("Région flamande", "Brabant flamand", "Diest", "3290", "Belgique"),
    ("Région wallonne", "Hainaut", "Mons", "7000", "Belgique"),
    ("Région wallonne", "Hainaut", "Charleroi", "6000", "Belgique"),
    ("Région wallonne", "Hainaut", "Tournai", "7500", "Belgique"),
    ("Région wallonne", "Hainaut", "La Louvière", "7100", "Belgique"),
    ("Région wallonne", "Hainaut", "Mouscron", "7700", "Belgique"),
    ("Région wallonne", "Hainaut", "Ath", "7800", "Belgique"),
    ("Région wallonne", "Liège", "Liège", "4000", "Belgique"),
    ("Région wallonne", "Liège", "Verviers", "4800", "Belgique"),
    ("Région wallonne", "Liège", "Seraing", "4100", "Belgique"),
    ("Région wallonne", "Liège", "Huy", "4500", "Belgique"),
    ("Région wallonne", "Liège", "Spa", "4900", "Belgique"),
    ("Région wallonne", "Liège", "Eupen", "4700", "Belgique"),
    ("Région wallonne", "Luxembourg", "Arlon", "6700", "Belgique"),
    ("Région wallonne", "Luxembourg", "Bastogne", "6600", "Belgique"),
    ("Région wallonne", "Luxembourg", "Marche-en-Famenne", "6900", "Belgique"),
    ("Région wallonne", "Luxembourg", "Bouillon", "6830", "Belgique"),
    ("Région wallonne", "Luxembourg", "Durbuy", "6940", "Belgique"),
    ("Région wallonne", "Namur", "Namur", "5000", "Belgique"),
    ("Région wallonne", "Namur", "Dinant", "5500", "Belgique"),
    ("Région wallonne", "Namur", "Philippeville", "5600", "Belgique"),
    ("Région wallonne", "Namur", "Andenne", "5300", "Belgique"),
    ("Région wallonne", "Namur", "Ciney", "5590", "Belgique"),
    ("Région wallonne", "Brabant wallon", "Wavre", "1300", "Belgique"),
    ("Région wallonne", "Brabant wallon", "Nivelles", "1400", "Belgique"),
    ("Région wallonne", "Brabant wallon", "Louvain-la-Neuve", "1348", "Belgique"),
    ("Région wallonne", "Brabant wallon", "Braine-l'Alleud", "1420", "Belgique"),
    ("Région wallonne", "Brabant wallon", "Waterloo", "1410", "Belgique"),

    # ---------- FRANCE ----------
    # Île-de-France
    ("Île-de-France", "Paris", "Paris", "75001", "France"),
    ("Île-de-France", "Yvelines", "Versailles", "78000", "France"),
    ("Île-de-France", "Hauts-de-Seine", "Boulogne-Billancourt", "92100", "France"),
    ("Île-de-France", "Hauts-de-Seine", "Nanterre", "92000", "France"),
    ("Île-de-France", "Seine-Saint-Denis", "Saint-Denis", "93200", "France"),
    ("Île-de-France", "Val-de-Marne", "Créteil", "94000", "France"),
    # Auvergne-Rhône-Alpes
    ("Auvergne-Rhône-Alpes", "Rhône", "Lyon", "69001", "France"),
    ("Auvergne-Rhône-Alpes", "Isère", "Grenoble", "38000", "France"),
    ("Auvergne-Rhône-Alpes", "Loire", "Saint-Étienne", "42000", "France"),
    ("Auvergne-Rhône-Alpes", "Puy-de-Dôme", "Clermont-Ferrand", "63000", "France"),
    ("Auvergne-Rhône-Alpes", "Haute-Savoie", "Annecy", "74000", "France"),
    ("Auvergne-Rhône-Alpes", "Savoie", "Chambéry", "73000", "France"),
    # Provence-Alpes-Côte d'Azur
    ("Provence-Alpes-Côte d'Azur", "Bouches-du-Rhône", "Marseille", "13001", "France"),
    ("Provence-Alpes-Côte d'Azur", "Alpes-Maritimes", "Nice", "06000", "France"),
    ("Provence-Alpes-Côte d'Azur", "Var", "Toulon", "83000", "France"),
    ("Provence-Alpes-Côte d'Azur", "Bouches-du-Rhône", "Aix-en-Provence", "13100", "France"),
    ("Provence-Alpes-Côte d'Azur", "Alpes-Maritimes", "Cannes", "06400", "France"),
    ("Provence-Alpes-Côte d'Azur", "Alpes-Maritimes", "Antibes", "06600", "France"),
    ("Provence-Alpes-Côte d'Azur", "Vaucluse", "Avignon", "84000", "France"),
    # Occitanie
    ("Occitanie", "Haute-Garonne", "Toulouse", "31000", "France"),
    ("Occitanie", "Hérault", "Montpellier", "34000", "France"),
    ("Occitanie", "Gard", "Nîmes", "30000", "France"),
    ("Occitanie", "Pyrénées-Orientales", "Perpignan", "66000", "France"),
    ("Occitanie", "Aude", "Carcassonne", "11000", "France"),
    # Nouvelle-Aquitaine
    ("Nouvelle-Aquitaine", "Gironde", "Bordeaux", "33000", "France"),
    ("Nouvelle-Aquitaine", "Vienne", "Poitiers", "86000", "France"),
    ("Nouvelle-Aquitaine", "Haute-Vienne", "Limoges", "87000", "France"),
    ("Nouvelle-Aquitaine", "Charente-Maritime", "La Rochelle", "17000", "France"),
    ("Nouvelle-Aquitaine", "Pyrénées-Atlantiques", "Pau", "64000", "France"),
    ("Nouvelle-Aquitaine", "Pyrénées-Atlantiques", "Biarritz", "64200", "France"),
    # Hauts-de-France
    ("Hauts-de-France", "Nord", "Lille", "59000", "France"),
    ("Hauts-de-France", "Somme", "Amiens", "80000", "France"),
    ("Hauts-de-France", "Nord", "Roubaix", "59100", "France"),
    ("Hauts-de-France", "Nord", "Tourcoing", "59200", "France"),
    ("Hauts-de-France", "Nord", "Dunkerque", "59140", "France"),
    # Grand Est
    ("Grand Est", "Bas-Rhin", "Strasbourg", "67000", "France"),
    ("Grand Est", "Marne", "Reims", "51100", "France"),
    ("Grand Est", "Moselle", "Metz", "57000", "France"),
    ("Grand Est", "Meurthe-et-Moselle", "Nancy", "54000", "France"),
    ("Grand Est", "Haut-Rhin", "Mulhouse", "68100", "France"),
    # Pays de la Loire
    ("Pays de la Loire", "Loire-Atlantique", "Nantes", "44000", "France"),
    ("Pays de la Loire", "Maine-et-Loire", "Angers", "49000", "France"),
    ("Pays de la Loire", "Sarthe", "Le Mans", "72000", "France"),
    ("Pays de la Loire", "Loire-Atlantique", "Saint-Nazaire", "44600", "France"),
    # Bretagne
    ("Bretagne", "Ille-et-Vilaine", "Rennes", "35000", "France"),
    ("Bretagne", "Finistère", "Brest", "29200", "France"),
    ("Bretagne", "Finistère", "Quimper", "29000", "France"),
    ("Bretagne", "Morbihan", "Vannes", "56000", "France"),
    ("Bretagne", "Ille-et-Vilaine", "Saint-Malo", "35400", "France"),
    # Normandie
    ("Normandie", "Seine-Maritime", "Rouen", "76000", "France"),
    ("Normandie", "Calvados", "Caen", "14000", "France"),
    ("Normandie", "Seine-Maritime", "Le Havre", "76600", "France"),
    ("Normandie", "Manche", "Cherbourg-en-Cotentin", "50100", "France"),
    # Bourgogne-Franche-Comté
    ("Bourgogne-Franche-Comté", "Côte-d'Or", "Dijon", "21000", "France"),
    ("Bourgogne-Franche-Comté", "Doubs", "Besançon", "25000", "France"),
    ("Bourgogne-Franche-Comté", "Territoire de Belfort", "Belfort", "90000", "France"),
    # Centre-Val de Loire
    ("Centre-Val de Loire", "Loiret", "Orléans", "45000", "France"),
    ("Centre-Val de Loire", "Indre-et-Loire", "Tours", "37000", "France"),
    ("Centre-Val de Loire", "Cher", "Bourges", "18000", "France"),
    # Corse
    ("Corse", "Corse-du-Sud", "Ajaccio", "20000", "France"),
    ("Corse", "Haute-Corse", "Bastia", "20200", "France"),
    # DROM
    ("Guadeloupe", "Guadeloupe", "Pointe-à-Pitre", "97110", "France"),
    ("Martinique", "Martinique", "Fort-de-France", "97200", "France"),
    ("Guyane", "Guyane", "Cayenne", "97300", "France"),
    ("La Réunion", "La Réunion", "Saint-Denis (La Réunion)", "97400", "France"),
    ("Mayotte", "Mayotte", "Mamoudzou", "97600", "France"),

    # ---------- ESPAGNE ----------
    # Andalousie
    ("Andalousie", "Séville", "Séville", "41001", "Espagne"),
    ("Andalousie", "Malaga", "Malaga", "29001", "Espagne"),
    ("Andalousie", "Cordoue", "Cordoue", "14001", "Espagne"),
    ("Andalousie", "Grenade", "Grenade", "18001", "Espagne"),
    ("Andalousie", "Cadix", "Cadix", "11001", "Espagne"),
    ("Andalousie", "Malaga", "Marbella", "29600", "Espagne"),
    # Aragon
    ("Aragon", "Saragosse", "Saragosse", "50001", "Espagne"),
    # Asturies
    ("Asturies", "Asturies", "Oviedo", "33001", "Espagne"),
    ("Asturies", "Asturies", "Gijón", "33201", "Espagne"),
    # Îles Baléares
    ("Îles Baléares", "Îles Baléares", "Palma de Majorque", "07001", "Espagne"),
    ("Îles Baléares", "Îles Baléares", "Ibiza", "07800", "Espagne"),
    # Îles Canaries
    ("Îles Canaries", "Las Palmas", "Las Palmas de Gran Canaria", "35001", "Espagne"),
    ("Îles Canaries", "Santa Cruz de Tenerife", "Santa Cruz de Tenerife", "38001", "Espagne"),
    # Cantabrie
    ("Cantabrie", "Cantabrie", "Santander", "39001", "Espagne"),
    # Castille-La Manche
    ("Castille-La Manche", "Tolède", "Tolède", "45001", "Espagne"),
    ("Castille-La Manche", "Albacete", "Albacete", "02001", "Espagne"),
    # Castille-et-León
    ("Castille-et-León", "Valladolid", "Valladolid", "47001", "Espagne"),
    ("Castille-et-León", "Salamanque", "Salamanque", "37001", "Espagne"),
    ("Castille-et-León", "Burgos", "Burgos", "09001", "Espagne"),
    ("Castille-et-León", "León", "León", "24001", "Espagne"),
    # Catalogne
    ("Catalogne", "Barcelone", "Barcelone", "08001", "Espagne"),
    ("Catalogne", "Tarragone", "Tarragone", "43001", "Espagne"),
    ("Catalogne", "Gérone", "Gérone", "17001", "Espagne"),
    ("Catalogne", "Lleida", "Lérida", "25001", "Espagne"),
    # Estrémadure
    ("Estrémadure", "Badajoz", "Mérida", "06800", "Espagne"),
    ("Estrémadure", "Badajoz", "Badajoz", "06001", "Espagne"),
    ("Estrémadure", "Cáceres", "Cáceres", "10001", "Espagne"),
    # Galice
    ("Galice", "La Corogne", "Saint-Jacques-de-Compostelle", "15700", "Espagne"),
    ("Galice", "La Corogne", "La Corogne", "15001", "Espagne"),
    ("Galice", "Pontevedra", "Vigo", "36201", "Espagne"),
    # Communauté de Madrid
    ("Communauté de Madrid", "Madrid", "Madrid", "28001", "Espagne"),
    # Murcie
    ("Région de Murcie", "Murcie", "Murcie", "30001", "Espagne"),
    ("Région de Murcie", "Murcie", "Carthagène", "30201", "Espagne"),
    # Navarre
    ("Navarre", "Navarre", "Pampelune", "31001", "Espagne"),
    # Pays basque
    ("Pays basque", "Biscaye", "Bilbao", "48001", "Espagne"),
    ("Pays basque", "Guipuscoa", "Saint-Sébastien", "20001", "Espagne"),
    ("Pays basque", "Alava", "Vitoria-Gasteiz", "01001", "Espagne"),
    # La Rioja
    ("La Rioja", "La Rioja", "Logroño", "26001", "Espagne"),
    # Communauté valencienne
    ("Communauté valencienne", "Valence", "Valence", "46001", "Espagne"),
    ("Communauté valencienne", "Alicante", "Alicante", "03001", "Espagne"),
    ("Communauté valencienne", "Castellón", "Castellón de la Plana", "12001", "Espagne"),
    # Villes autonomes
    ("Ceuta", "Ceuta", "Ceuta", "51001", "Espagne"),
    ("Melilla", "Melilla", "Melilla", "52001", "Espagne"),

    # ---------- ALLEMAGNE ----------
    # Bade-Wurtemberg
    ("Bade-Wurtemberg", "", "Stuttgart", "70173", "Allemagne"),
    ("Bade-Wurtemberg", "", "Karlsruhe", "76131", "Allemagne"),
    ("Bade-Wurtemberg", "", "Mannheim", "68159", "Allemagne"),
    ("Bade-Wurtemberg", "", "Fribourg-en-Brisgau", "79098", "Allemagne"),
    ("Bade-Wurtemberg", "", "Heidelberg", "69115", "Allemagne"),
    # Bavière
    ("Bavière", "", "Munich", "80331", "Allemagne"),
    ("Bavière", "", "Nuremberg", "90402", "Allemagne"),
    ("Bavière", "", "Augsbourg", "86150", "Allemagne"),
    ("Bavière", "", "Wurtzbourg", "97070", "Allemagne"),
    ("Bavière", "", "Ratisbonne", "93047", "Allemagne"),
    # Berlin
    ("Berlin", "", "Berlin", "10115", "Allemagne"),
    # Brandebourg
    ("Brandebourg", "", "Potsdam", "14467", "Allemagne"),
    # Brême
    ("Brême", "", "Brême", "28195", "Allemagne"),
    ("Brême", "", "Bremerhaven", "27568", "Allemagne"),
    # Hambourg
    ("Hambourg", "", "Hambourg", "20095", "Allemagne"),
    # Hesse
    ("Hesse", "", "Francfort-sur-le-Main", "60311", "Allemagne"),
    ("Hesse", "", "Wiesbaden", "65183", "Allemagne"),
    ("Hesse", "", "Cassel", "34117", "Allemagne"),
    ("Hesse", "", "Darmstadt", "64283", "Allemagne"),
    # Mecklembourg-Poméranie-Occidentale
    ("Mecklembourg-Poméranie-Occidentale", "", "Schwerin", "19053", "Allemagne"),
    ("Mecklembourg-Poméranie-Occidentale", "", "Rostock", "18055", "Allemagne"),
    # Basse-Saxe
    ("Basse-Saxe", "", "Hanovre", "30159", "Allemagne"),
    ("Basse-Saxe", "", "Brunswick", "38100", "Allemagne"),
    ("Basse-Saxe", "", "Osnabrück", "49074", "Allemagne"),
    ("Basse-Saxe", "", "Oldenbourg", "26122", "Allemagne"),
    # Rhénanie-du-Nord-Westphalie
    ("Rhénanie-du-Nord-Westphalie", "", "Cologne", "50667", "Allemagne"),
    ("Rhénanie-du-Nord-Westphalie", "", "Düsseldorf", "40213", "Allemagne"),
    ("Rhénanie-du-Nord-Westphalie", "", "Dortmund", "44135", "Allemagne"),
    ("Rhénanie-du-Nord-Westphalie", "", "Essen", "45127", "Allemagne"),
    ("Rhénanie-du-Nord-Westphalie", "", "Bonn", "53111", "Allemagne"),
    ("Rhénanie-du-Nord-Westphalie", "", "Münster", "48143", "Allemagne"),
    # Rhénanie-Palatinat
    ("Rhénanie-Palatinat", "", "Mayence", "55116", "Allemagne"),
    ("Rhénanie-Palatinat", "", "Coblence", "56068", "Allemagne"),
    ("Rhénanie-Palatinat", "", "Trèves", "54290", "Allemagne"),
    ("Rhénanie-Palatinat", "", "Ludwigshafen", "67059", "Allemagne"),
    # Sarre
    ("Sarre", "", "Sarrebruck", "66111", "Allemagne"),
    # Saxe
    ("Saxe", "", "Dresde", "01067", "Allemagne"),
    ("Saxe", "", "Leipzig", "04109", "Allemagne"),
    ("Saxe", "", "Chemnitz", "09111", "Allemagne"),
    # Saxe-Anhalt
    ("Saxe-Anhalt", "", "Magdebourg", "39104", "Allemagne"),
    ("Saxe-Anhalt", "", "Halle", "06108", "Allemagne"),
    # Schleswig-Holstein
    ("Schleswig-Holstein", "", "Kiel", "24103", "Allemagne"),
    ("Schleswig-Holstein", "", "Lübeck", "23552", "Allemagne"),
    ("Schleswig-Holstein", "", "Flensbourg", "24937", "Allemagne"),
    # Thuringe
    ("Thuringe", "", "Erfurt", "99084", "Allemagne"),
    ("Thuringe", "", "Iéna", "07743", "Allemagne"),
    ("Thuringe", "", "Weimar", "99423", "Allemagne"),

    # ---------- ÉTATS-UNIS ----------
    # Schéma US : Région = région du recensement | Province = État | Ville | ZIP
    # ----- Northeast -----
    ("Northeast", "Connecticut", "Bridgeport", "06604", "États-Unis"),
    ("Northeast", "Connecticut", "New Haven", "06510", "États-Unis"),
    ("Northeast", "Connecticut", "Hartford", "06103", "États-Unis"),
    ("Northeast", "Connecticut", "Stamford", "06901", "États-Unis"),
    ("Northeast", "Maine", "Portland", "04101", "États-Unis"),
    ("Northeast", "Maine", "Bangor", "04401", "États-Unis"),
    ("Northeast", "Massachusetts", "Boston", "02108", "États-Unis"),
    ("Northeast", "Massachusetts", "Worcester", "01608", "États-Unis"),
    ("Northeast", "Massachusetts", "Cambridge", "02139", "États-Unis"),
    ("Northeast", "Massachusetts", "Springfield", "01103", "États-Unis"),
    ("Northeast", "New Hampshire", "Manchester", "03101", "États-Unis"),
    ("Northeast", "New Hampshire", "Nashua", "03060", "États-Unis"),
    ("Northeast", "Rhode Island", "Providence", "02903", "États-Unis"),
    ("Northeast", "Vermont", "Burlington", "05401", "États-Unis"),
    ("Northeast", "New Jersey", "Newark", "07102", "États-Unis"),
    ("Northeast", "New Jersey", "Jersey City", "07302", "États-Unis"),
    ("Northeast", "New Jersey", "Paterson", "07501", "États-Unis"),
    ("Northeast", "New Jersey", "Trenton", "08608", "États-Unis"),
    ("Northeast", "New York", "New York", "10001", "États-Unis"),
    ("Northeast", "New York", "Buffalo", "14201", "États-Unis"),
    ("Northeast", "New York", "Rochester", "14604", "États-Unis"),
    ("Northeast", "New York", "Albany", "12207", "États-Unis"),
    ("Northeast", "New York", "Syracuse", "13202", "États-Unis"),
    ("Northeast", "Pennsylvania", "Philadelphia", "19103", "États-Unis"),
    ("Northeast", "Pennsylvania", "Pittsburgh", "15222", "États-Unis"),
    ("Northeast", "Pennsylvania", "Allentown", "18101", "États-Unis"),
    ("Northeast", "Pennsylvania", "Harrisburg", "17101", "États-Unis"),
    # ----- Midwest -----
    ("Midwest", "Illinois", "Chicago", "60601", "États-Unis"),
    ("Midwest", "Illinois", "Aurora", "60505", "États-Unis"),
    ("Midwest", "Illinois", "Naperville", "60540", "États-Unis"),
    ("Midwest", "Illinois", "Springfield", "62701", "États-Unis"),
    ("Midwest", "Indiana", "Indianapolis", "46204", "États-Unis"),
    ("Midwest", "Indiana", "Fort Wayne", "46802", "États-Unis"),
    ("Midwest", "Michigan", "Detroit", "48226", "États-Unis"),
    ("Midwest", "Michigan", "Grand Rapids", "49503", "États-Unis"),
    ("Midwest", "Michigan", "Ann Arbor", "48104", "États-Unis"),
    ("Midwest", "Ohio", "Columbus", "43215", "États-Unis"),
    ("Midwest", "Ohio", "Cleveland", "44114", "États-Unis"),
    ("Midwest", "Ohio", "Cincinnati", "45202", "États-Unis"),
    ("Midwest", "Ohio", "Toledo", "43604", "États-Unis"),
    ("Midwest", "Wisconsin", "Milwaukee", "53202", "États-Unis"),
    ("Midwest", "Wisconsin", "Madison", "53703", "États-Unis"),
    ("Midwest", "Iowa", "Des Moines", "50309", "États-Unis"),
    ("Midwest", "Iowa", "Cedar Rapids", "52401", "États-Unis"),
    ("Midwest", "Kansas", "Wichita", "67202", "États-Unis"),
    ("Midwest", "Kansas", "Topeka", "66603", "États-Unis"),
    ("Midwest", "Minnesota", "Minneapolis", "55401", "États-Unis"),
    ("Midwest", "Minnesota", "Saint Paul", "55102", "États-Unis"),
    ("Midwest", "Missouri", "Kansas City", "64106", "États-Unis"),
    ("Midwest", "Missouri", "Saint Louis", "63101", "États-Unis"),
    ("Midwest", "Missouri", "Springfield", "65806", "États-Unis"),
    ("Midwest", "Nebraska", "Omaha", "68102", "États-Unis"),
    ("Midwest", "Nebraska", "Lincoln", "68508", "États-Unis"),
    ("Midwest", "North Dakota", "Fargo", "58102", "États-Unis"),
    ("Midwest", "North Dakota", "Bismarck", "58501", "États-Unis"),
    ("Midwest", "South Dakota", "Sioux Falls", "57104", "États-Unis"),
    # ----- South -----
    ("South", "Delaware", "Wilmington", "19801", "États-Unis"),
    ("South", "Florida", "Jacksonville", "32202", "États-Unis"),
    ("South", "Florida", "Miami", "33130", "États-Unis"),
    ("South", "Florida", "Tampa", "33602", "États-Unis"),
    ("South", "Florida", "Orlando", "32801", "États-Unis"),
    ("South", "Florida", "Fort Lauderdale", "33301", "États-Unis"),
    ("South", "Florida", "Saint Petersburg", "33701", "États-Unis"),
    ("South", "Georgia", "Atlanta", "30303", "États-Unis"),
    ("South", "Georgia", "Savannah", "31401", "États-Unis"),
    ("South", "Georgia", "Augusta", "30901", "États-Unis"),
    ("South", "Maryland", "Baltimore", "21202", "États-Unis"),
    ("South", "Maryland", "Annapolis", "21401", "États-Unis"),
    ("South", "North Carolina", "Charlotte", "28202", "États-Unis"),
    ("South", "North Carolina", "Raleigh", "27601", "États-Unis"),
    ("South", "North Carolina", "Greensboro", "27401", "États-Unis"),
    ("South", "North Carolina", "Durham", "27701", "États-Unis"),
    ("South", "South Carolina", "Charleston", "29401", "États-Unis"),
    ("South", "South Carolina", "Columbia", "29201", "États-Unis"),
    ("South", "Virginia", "Virginia Beach", "23451", "États-Unis"),
    ("South", "Virginia", "Richmond", "23219", "États-Unis"),
    ("South", "Virginia", "Arlington", "22201", "États-Unis"),
    ("South", "Virginia", "Norfolk", "23510", "États-Unis"),
    ("South", "West Virginia", "Charleston", "25301", "États-Unis"),
    ("South", "District of Columbia", "Washington", "20001", "États-Unis"),
    ("South", "Alabama", "Birmingham", "35203", "États-Unis"),
    ("South", "Alabama", "Montgomery", "36104", "États-Unis"),
    ("South", "Alabama", "Huntsville", "35801", "États-Unis"),
    ("South", "Kentucky", "Louisville", "40202", "États-Unis"),
    ("South", "Kentucky", "Lexington", "40507", "États-Unis"),
    ("South", "Mississippi", "Jackson", "39201", "États-Unis"),
    ("South", "Tennessee", "Nashville", "37203", "États-Unis"),
    ("South", "Tennessee", "Memphis", "38103", "États-Unis"),
    ("South", "Tennessee", "Knoxville", "37902", "États-Unis"),
    ("South", "Tennessee", "Chattanooga", "37402", "États-Unis"),
    ("South", "Arkansas", "Little Rock", "72201", "États-Unis"),
    ("South", "Louisiana", "New Orleans", "70112", "États-Unis"),
    ("South", "Louisiana", "Baton Rouge", "70802", "États-Unis"),
    ("South", "Oklahoma", "Oklahoma City", "73102", "États-Unis"),
    ("South", "Oklahoma", "Tulsa", "74103", "États-Unis"),
    ("South", "Texas", "Houston", "77002", "États-Unis"),
    ("South", "Texas", "San Antonio", "78205", "États-Unis"),
    ("South", "Texas", "Dallas", "75201", "États-Unis"),
    ("South", "Texas", "Austin", "78701", "États-Unis"),
    ("South", "Texas", "Fort Worth", "76102", "États-Unis"),
    ("South", "Texas", "El Paso", "79901", "États-Unis"),
    # ----- West -----
    ("West", "Arizona", "Phoenix", "85003", "États-Unis"),
    ("West", "Arizona", "Tucson", "85701", "États-Unis"),
    ("West", "Arizona", "Scottsdale", "85251", "États-Unis"),
    ("West", "Arizona", "Mesa", "85201", "États-Unis"),
    ("West", "Colorado", "Denver", "80202", "États-Unis"),
    ("West", "Colorado", "Colorado Springs", "80903", "États-Unis"),
    ("West", "Colorado", "Boulder", "80302", "États-Unis"),
    ("West", "Idaho", "Boise", "83702", "États-Unis"),
    ("West", "Montana", "Billings", "59101", "États-Unis"),
    ("West", "Montana", "Bozeman", "59715", "États-Unis"),
    ("West", "Nevada", "Las Vegas", "89101", "États-Unis"),
    ("West", "Nevada", "Reno", "89501", "États-Unis"),
    ("West", "New Mexico", "Albuquerque", "87102", "États-Unis"),
    ("West", "New Mexico", "Santa Fe", "87501", "États-Unis"),
    ("West", "Utah", "Salt Lake City", "84101", "États-Unis"),
    ("West", "Utah", "Park City", "84060", "États-Unis"),
    ("West", "Wyoming", "Cheyenne", "82001", "États-Unis"),
    ("West", "Wyoming", "Jackson", "83001", "États-Unis"),
    ("West", "Alaska", "Anchorage", "99501", "États-Unis"),
    ("West", "California", "Los Angeles", "90012", "États-Unis"),
    ("West", "California", "San Francisco", "94102", "États-Unis"),
    ("West", "California", "San Diego", "92101", "États-Unis"),
    ("West", "California", "San Jose", "95113", "États-Unis"),
    ("West", "California", "Sacramento", "95814", "États-Unis"),
    ("West", "California", "Oakland", "94607", "États-Unis"),
    ("West", "California", "Santa Monica", "90401", "États-Unis"),
    ("West", "California", "Long Beach", "90802", "États-Unis"),
    ("West", "Hawaii", "Honolulu", "96813", "États-Unis"),
    ("West", "Oregon", "Portland", "97204", "États-Unis"),
    ("West", "Oregon", "Eugene", "97401", "États-Unis"),
    ("West", "Oregon", "Bend", "97701", "États-Unis"),
    ("West", "Washington", "Seattle", "98101", "États-Unis"),
    ("West", "Washington", "Spokane", "99201", "États-Unis"),
    ("West", "Washington", "Tacoma", "98402", "États-Unis"),
    ("West", "Washington", "Bellevue", "98004", "États-Unis"),
]

# --------------------------------------------------------------------------- #
# Établissements (en-têtes uniquement)
# --------------------------------------------------------------------------- #

ETABLISSEMENTS_HEADERS = [
    "Nom",
    "Catégorie",
    "Adresse",
    "Ville",
    "Code postal",
    "Province",
    "Pays",
    "Latitude",
    "Longitude",
    "Site web",
    "Description",
    "Résumé",
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_service_account_json():
    """Cherche un JSON Service Account, dans l'ordre :
      1. $GOOGLE_APPLICATION_CREDENTIALS
      2. <script>/service_account.json
      3. <script>/.secrets/service_account.json
      4. premier .json dans <script>/.secrets/
    """
    env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env and os.path.exists(env):
        return env

    for c in (
        os.path.join(SCRIPT_DIR, "service_account.json"),
        os.path.join(SCRIPT_DIR, ".secrets", "service_account.json"),
    ):
        if os.path.exists(c):
            return c

    secrets_dir = os.path.join(SCRIPT_DIR, ".secrets")
    if os.path.isdir(secrets_dir):
        for fn in sorted(os.listdir(secrets_dir)):
            if fn.endswith(".json"):
                return os.path.join(secrets_dir, fn)

    return None


def get_client():
    sa_path = find_service_account_json()
    if sa_path:
        return gspread.service_account(filename=sa_path)
    try:
        return gspread.oauth()
    except Exception as e:
        print(
            "Aucune authentification trouvée. Place le JSON Service Account dans :\n"
            f"  {SCRIPT_DIR}/service_account.json\n"
            f"  ou {SCRIPT_DIR}/.secrets/service_account.json\n"
            "Ou définis GOOGLE_APPLICATION_CREDENTIALS vers un autre chemin.\n"
            f"Erreur : {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def delete_worksheet_if_exists(spreadsheet, title):
    try:
        existing = spreadsheet.worksheet(title)
        spreadsheet.del_worksheet(existing)
    except WorksheetNotFound:
        pass


def reset_worksheet(spreadsheet, title, rows, cols):
    delete_worksheet_if_exists(spreadsheet, title)
    return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def col_letter(n):
    """1 -> A, 2 -> B, ..., 26 -> Z, 27 -> AA."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    gc = get_client()
    sh = gc.open_by_key(SPREADSHEET_ID)

    # Catégories
    ws = reset_worksheet(sh, "Catégories", rows=len(CATEGORIES) + 10, cols=2)
    ws.update(range_name="A1", values=[["Catégorie"]] + [[c] for c in CATEGORIES])
    ws.format("A1", {"textFormat": {"bold": True}})

    # Pays
    ws = reset_worksheet(sh, "Pays", rows=len(PAYS) + 10, cols=5)
    pays_values = [["Pays", "Code ISO 2", "Code ISO 3", "Continent", "Capitale"]]
    pays_values.extend([list(row) for row in PAYS])
    ws.update(range_name="A1", values=pays_values)
    ws.format("A1:E1", {"textFormat": {"bold": True}})
    ws.freeze(rows=1)

    # Régions (remplace l'ancien onglet "Régions - Belgique" si présent)
    delete_worksheet_if_exists(sh, "Régions - Belgique")
    ws = reset_worksheet(sh, "Régions", rows=len(REGIONS) + 10, cols=5)
    reg_values = [["Région", "Province", "Ville principale", "Code postal", "Pays"]]
    reg_values.extend([list(row) for row in REGIONS])
    ws.update(range_name="A1", values=reg_values)
    ws.format("A1:E1", {"textFormat": {"bold": True}})
    ws.freeze(rows=1)

    # Établissements
    ws = reset_worksheet(sh, "Établissements", rows=1000, cols=len(ETABLISSEMENTS_HEADERS))
    ws.update(range_name="A1", values=[ETABLISSEMENTS_HEADERS])
    last_col = col_letter(len(ETABLISSEMENTS_HEADERS))
    ws.format(f"A1:{last_col}1", {"textFormat": {"bold": True}})
    ws.freeze(rows=1)

    # Récap par pays pour Régions
    by_country = {}
    for r in REGIONS:
        by_country[r[4]] = by_country.get(r[4], 0) + 1

    print(f"OK — Sheet : https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
    print(f"  - Catégories   : {len(CATEGORIES)} entrées")
    print(f"  - Pays         : {len(PAYS)} pays")
    print(f"  - Régions      : {len(REGIONS)} villes")
    for c, n in by_country.items():
        print(f"      • {c}: {n}")
    print(f"  - Établissements: structure vide ({len(ETABLISSEMENTS_HEADERS)} colonnes)")


if __name__ == "__main__":
    main()
