"""Source des questions de scénario (quiz-iso27001-scenarios.html), au format de l’examen PECB ISO/IEC 27001 LI.

    python3 author_scenarios.py data/scenarios.json

Chaque scenario est un recit long, sous une forme differente, qui melange
plusieurs domaines. Chaque question porte un domaine d'examen propre et
s'appuie sur un fait precis du recit.
"""
import json, random, sys
from collections import Counter

DOMAINS = {
    1: 'Principes et concepts fondamentaux d’un SMSI',
    2: 'Système de management de la sécurité de l’information (SMSI)',
    3: 'Planification de la mise en œuvre d’un SMSI selon ISO/IEC 27001',
    4: 'Mise en œuvre d’un SMSI selon ISO/IEC 27001',
    6: 'Amélioration continue d’un SMSI selon ISO/IEC 27001',
}

# (numero, titre, [paragraphes], [(domaine, enonce, [options], index bonne, explication)])
SCEN = []

# ---------------------------------------------------------------------------
SCEN.append((1, 'Aquila Pharma · lancement du projet', [
 "Aquila Pharma est un laboratoire pharmaceutique de 800 salariés basé à Clermont-Ferrand. Il développe des médicaments génériques et conduit des essais cliniques pour le compte de partenaires européens. En 2024, deux de ses principaux partenaires ont fait de la certification ISO/IEC 27001 une condition de renouvellement de leurs contrats.",
 "Le directeur général a nommé Inès Morel, responsable qualité, cheffe de projet SMSI. En réunion de lancement, il a précisé qu’il approuverait le budget mais ne souhaitait pas être impliqué davantage : « Inès a toute ma confiance, elle reviendra vers moi une fois le certificat obtenu. »",
 "Inès a choisi de conduire la mise en œuvre avec la méthodologie de gestion de projet déjà employée pour les essais cliniques, inspirée d’ISO 10006 : charte de projet, jalons, comité de pilotage mensuel et registre des risques du projet.",
 "Elle a ensuite analysé le contexte. La direction juridique a dressé la liste des obligations applicables (bonnes pratiques de fabrication, RGPD, hébergement de données de santé). L’équipe a par ailleurs interrogé les partenaires, l’Agence nationale de sécurité du médicament et les représentants du personnel pour recueillir leurs attentes en matière de sécurité de l’information.",
 "Pour le domaine d’application, Inès a proposé de couvrir les essais cliniques et le système d’information qui les supporte, et d’exclure l’usine de production, dont les automates sont maintenus par un prestataire. Elle a documenté ce domaine en décrivant les interfaces entre le service des essais et l’usine, qui partagent le même annuaire informatique.",
 "L’équipe a ensuite comparé les pratiques existantes aux exigences de la norme et aux mesures de l’Annexe A. Environ 60 % des mesures étaient en place mais rarement documentées : l’équipe informatique appliquait par exemple une procédure de sauvegarde quotidienne, connue de tous mais jamais écrite. L’exercice a aussi mis au jour un incident passé : un stagiaire, qui disposait des droits de modification sur l’ensemble du répertoire des essais, avait modifié par erreur un tableur de résultats, faussant une analyse statistique découverte trois mois plus tard.",
 "Enfin, Inès a rédigé la politique de sécurité de l’information. Elle l’a fait valider par le responsable informatique, puis l’a publiée sur l’intranet.",
], [
 (2, "Selon le scénario 1, la position du directeur général est-elle conforme à ISO/IEC 27001 ?",
  ["Oui, car en désignant une cheffe de projet et en approuvant le budget, il a rempli l’essentiel de ses obligations de direction",
   "Non, car la direction doit démontrer son leadership tout au long de la vie du SMSI, pas seulement au lancement",
   "Non, car ISO/IEC 27001 exige que le directeur général conduise lui-même le projet de mise en œuvre du SMSI"], 1,
  "L’article 5.1 attend de la direction qu’elle démontre son leadership : s’assurer que la politique et les objectifs sont établis et compatibles avec la stratégie, intégrer les exigences du SMSI aux processus, fournir les ressources, communiquer sur l’importance du SMSI, orienter et soutenir les personnes, promouvoir l’amélioration continue. Elle peut confier la conduite du projet à une autre personne (article 5.3), mais pas se désengager jusqu’à la certification."),
 (3, "Selon le scénario 1, quelle approche de mise en œuvre Inès a-t-elle retenue ?",
  ["L’approche systématique, qui applique les bonnes pratiques de gestion de projet",
   "L’approche itérative, qui vise d’abord les exigences minimales avant d’améliorer",
   "L’approche intégrée, qui harmonise le SMSI avec d’autres systèmes de management"], 0,
  "Dans la formation PECB, l’approche systématique désigne l’application des bonnes pratiques de gestion de projet, telles que celles d’ISO 10006 : charte, jalons, gouvernance, gestion des risques du projet. L’approche itérative met en œuvre rapidement les exigences minimales puis améliore ; l’approche intégrée harmonise le SMSI avec d’autres systèmes de management."),
 (3, "Selon le scénario 1, en interrogeant les partenaires, l’autorité de santé et les représentants du personnel, quelle exigence d’ISO/IEC 27001 l’équipe a-t-elle cherché à satisfaire ?",
  ["L’article 4.1, qui demande de déterminer les enjeux externes et internes ayant une incidence sur le SMSI",
   "L’article 4.2, qui demande de déterminer les parties intéressées pertinentes et leurs exigences",
   "L’article 7.4, qui demande de déterminer les besoins de communication interne et externe"], 1,
  "Recueillir les attentes de personnes ou d’organismes concernés par le SMSI relève de l’article 4.2 : déterminer les parties intéressées pertinentes, leurs exigences, et celles qui seront traitées au moyen du SMSI. La liste des obligations dressée par la direction juridique alimente à la fois 4.1 et 4.2 ; l’article 7.4 porte sur la communication une fois le SMSI établi."),
 (3, "Selon le scénario 1, l’exclusion de l’usine de production du domaine d’application est-elle acceptable ?",
  ["Non, car le domaine d’application d’un SMSI doit couvrir l’ensemble des sites et des activités de l’organisation, y compris ceux confiés à des prestataires",
   "Oui, car les automates de l’usine sont maintenus par un prestataire, ce qui place l’usine hors du SMSI",
   "Oui, car l’organisation peut fixer ses limites dès lors qu’elle tient compte des interfaces et dépendances et documente le domaine"], 2,
  "L’article 4.3 laisse l’organisation déterminer les limites et l’applicabilité du SMSI, en tenant compte des enjeux (4.1), des exigences des parties intéressées (4.2) et des interfaces et dépendances avec d’autres activités ou organisations, puis exige que le domaine soit documenté. Inès l’a fait, y compris pour l’annuaire partagé. Le recours à un prestataire n’est pas en soi un motif d’exclusion : l’usine reste une activité d’Aquila."),
 (4, "Selon le scénario 1, que doit faire Aquila de la procédure de sauvegarde quotidienne appliquée mais jamais écrite ?",
  ["La documenter dans la mesure jugée nécessaire à l’efficacité du SMSI, puis la maîtriser comme toute information documentée",
   "La conserver en l’état, car une pratique effectivement appliquée et connue de tous satisfait déjà aux exigences de la norme",
   "La faire rédiger et approuver par l’organisme de certification, seul habilité à valider les procédures opérationnelles"], 0,
  "L’article 7.5.1 inclut, outre les informations documentées exigées par la norme, celles que l’organisation juge nécessaires à l’efficacité du SMSI ; l’article 7.5.3 en organise la maîtrise. La mesure 5.37 d’ISO/IEC 27002 recommande de documenter les procédures d’exploitation et de les mettre à disposition de ceux qui en ont besoin. Une pratique orale dépend des personnes qui la connaissent."),
 (1, "Selon le scénario 1, quel principe de sécurité l’incident du tableur a-t-il compromis, et quelle faiblesse l’a rendu possible ?",
  ["L’intégrité, compromise par des droits de modification attribués bien au-delà du besoin du stagiaire",
   "La confidentialité, compromise par l’absence de chiffrement du répertoire contenant les résultats des essais",
   "La disponibilité, compromise par l’absence de sauvegarde permettant de restaurer le tableur d’origine"], 0,
  "Une modification erronée rend l’information inexacte : c’est l’intégrité qui est atteinte. La vulnérabilité exploitée est l’excès de droits : un stagiaire n’avait pas besoin de modifier l’ensemble du répertoire des essais. Le principe du moindre privilège, que traite la mesure 5.18 d’ISO/IEC 27002 (Droits d’accès), aurait limité l’exposition."),
 (2, "Selon le scénario 1, la manière dont la politique de sécurité a été validée et diffusée est-elle conforme ?",
  ["Oui, car le responsable informatique dispose des compétences techniques nécessaires pour approuver la politique, et l’intranet en assure la diffusion",
   "Non, car la politique doit être établie par la direction, puis communiquée en interne et mise à disposition des parties intéressées",
   "Non, car une politique de sécurité ne doit pas être publiée, afin de ne fournir aucune information à un attaquant"], 1,
  "L’article 5.2 confie à la direction l’établissement de la politique, qui doit être disponible sous forme d’informations documentées, communiquée au sein de l’organisation et mise à la disposition des parties intéressées, selon le cas. La publication sur l’intranet est une bonne pratique ; la validation par le seul responsable informatique ne suffit pas."),
 (3, "Selon le scénario 1, contexte, domaine d’application et politique étant établis, quelle étape doit logiquement suivre ?",
  ["Définir le processus d’appréciation des risques, avec ses critères, puis apprécier les risques du domaine",
   "Mettre en œuvre sans attendre les 40 % de mesures de l’Annexe A qui ne sont pas encore en place",
   "Solliciter un audit de certification à blanc pour mesurer l’écart restant avant toute autre action"], 0,
  "La planification se poursuit par l’article 6.1 : définir et appliquer un processus d’appréciation des risques (6.1.2), puis de traitement (6.1.3). Les mesures à mettre en œuvre découlent de ce traitement, et non du seul écart avec l’Annexe A ; l’audit de certification intervient une fois le SMSI en fonctionnement."),
]))

# ---------------------------------------------------------------------------
SCEN.append((2, 'Terminal Rhône Conteneurs · comité de pilotage', [
 "Terminal Rhône Conteneurs (TRC) exploite un terminal portuaire fluvial à Lyon : déchargement des barges, stockage et expédition des conteneurs. Son SMSI est en cours de planification. Voici le compte rendu du comité de pilotage du 12 mars.",
 "Méthode. Karim, responsable du SMSI, présente la méthode retenue : chaque risque est évalué sur une échelle de vraisemblance et une échelle d’impact de 1 à 4 ; le niveau de risque est leur produit. Tout risque d’un niveau inférieur ou égal à 4 est accepté. La méthode et les échelles ont été documentées et approuvées par la direction.",
 "Identification. L’équipe a recensé les actifs, puis les menaces et vulnérabilités qui les concernent. Elle relève notamment que le logiciel de pilotage des grues n’a pas été mis à jour depuis deux ans, alors que l’éditeur a publié plusieurs correctifs de sécurité, et que le local technique du quai 3, qui héberge les serveurs d’exploitation, se trouve en zone inondable.",
 "Propriétaires. Pour simplifier, Karim propose d’être désigné propriétaire de l’ensemble des risques : « je suis le mieux placé pour les suivre ».",
 "Traitement. Pour le risque d’inondation, la direction décide de déménager les serveurs dans un bâtiment situé hors zone inondable. Pour le logiciel des grues, elle décide d’appliquer les correctifs et d’isoler le réseau des grues du reste du système d’information. Pour le risque de cyberattaque sur la facturation, évalué au niveau 6, le directeur général déclare qu’il « accepte le risque pour cette année, faute de budget ».",
 "Déclaration d’applicabilité. Karim présente une première version de la déclaration d’applicabilité, qui liste uniquement les mesures retenues ; les mesures de l’Annexe A non retenues n’y apparaissent pas.",
 "Suite. Le comité convient de réapprécier les risques une fois par an, « et seulement une fois par an, pour ne pas alourdir le dispositif ».",
], [
 (1, "Selon le scénario 2, comment qualifier respectivement l’inondation et l’implantation du local technique en zone inondable ?",
  ["L’inondation est une vulnérabilité du local, et son implantation en zone inondable est la menace qui pèse sur lui",
   "L’inondation est une menace, et l’implantation du local en zone inondable est la vulnérabilité qu’elle peut exploiter",
   "L’inondation et l’implantation en zone inondable sont toutes deux des risques, à inscrire tels quels au registre"], 1,
  "Selon ISO/IEC 27000, une menace est la cause potentielle d’un incident indésirable (ici l’inondation) ; une vulnérabilité est la faiblesse d’un actif ou d’une mesure qui peut être exploitée par une menace (ici l’emplacement du local). Le risque naît de leur combinaison et s’exprime par la vraisemblance et les conséquences."),
 (3, "Selon le scénario 2, la méthode d’appréciation des risques présentée par Karim satisfait-elle aux exigences d’ISO/IEC 27001 ?",
  ["Oui, car elle fixe des critères d’acceptation et de réalisation des appréciations, documentés et approuvés",
   "Non, car ISO/IEC 27001 impose d’appliquer la méthode d’appréciation décrite dans ISO/IEC 27005",
   "Non, car ISO/IEC 27001 exige une évaluation financière des risques plutôt que des échelles qualitatives"], 0,
  "L’article 6.1.2 a) exige d’établir et de tenir à jour des critères de risque, dont les critères d’acceptation et ceux de réalisation des appréciations. La norme n’impose aucune méthode : ISO/IEC 27005 fournit des lignes directrices, et les approches qualitatives comme quantitatives sont admises."),
 (3, "Selon le scénario 2, la proposition de Karim d’être propriétaire de tous les risques est-elle appropriée ?",
  ["Oui, car un propriétaire unique garantit un suivi homogène et une vision consolidée de l’ensemble des risques",
   "Non, car ISO/IEC 27001 exige que l’ensemble des risques soit attribué au directeur général, seul redevable",
   "Non, car chaque risque doit revenir à une personne qui a la responsabilité et l’autorité pour le gérer"], 2,
  "ISO/IEC 27000 définit le propriétaire du risque comme la personne ou l’entité ayant la responsabilité et l’autorité pour gérer un risque. Le responsable du SMSI coordonne le processus, mais n’a généralement pas l’autorité sur les activités portuaires, la facturation ou l’informatique. L’article 6.1.2 c) demande d’identifier les propriétaires des risques."),
 (3, "Selon le scénario 2, quelle option de traitement la direction a-t-elle retenue pour le risque d’inondation ?",
  ["La modification du risque", "L’évitement du risque", "Le partage du risque"], 1,
  "ISO/IEC 27005 décrit l’évitement comme le fait de renoncer à une activité ou de modifier les conditions dans lesquelles elle s’exerce pour ne plus être exposé au risque ; elle cite notamment le déplacement des moyens de traitement hors d’une zone exposée à un aléa naturel. La modification agirait sur la vraisemblance ou l’impact sans supprimer l’exposition, par exemple en surélevant les baies."),
 (1, "Selon le scénario 2, l’application des correctifs et l’isolement du réseau des grues correspondent à quel type de mesures ?",
  ["Des mesures préventives et technologiques, qui relèvent de la gestion des vulnérabilités techniques et du cloisonnement des réseaux",
   "Des mesures détectives et technologiques, qui relèvent de la journalisation et de la surveillance des activités réseau",
   "Des mesures correctives et organisationnelles, qui relèvent de la réponse aux incidents de sécurité de l’information"], 0,
  "Les deux dispositions visent à empêcher l’exploitation de la faiblesse avant tout incident : elles sont préventives. ISO/IEC 27002:2022 les classe dans le thème technologique : 8.8 Gestion des vulnérabilités techniques et 8.22 Cloisonnement des réseaux."),
 (3, "Selon le scénario 2, l’acceptation du risque de cyberattaque sur la facturation est-elle valable en l’état ?",
  ["Oui, car la direction peut accepter n’importe quel risque, quel que soit son niveau, sans autre formalité",
   "Non, car un risque d’un niveau supérieur au seuil d’acceptation doit obligatoirement être traité par réduction, jusqu’à repasser sous ce seuil",
   "Non, car un risque au-dessus du seuil ne peut être retenu que par une décision explicite et justifiée de son propriétaire, documentée"], 2,
  "Le niveau 6 dépasse le seuil d’acceptation de 4. ISO/IEC 27005 admet qu’un risque soit retenu au-delà des critères, à condition que la décision soit explicite et justifiée. ISO/IEC 27001 (article 6.1.3 f) confie l’acceptation des risques résiduels à leurs propriétaires, et le processus de traitement doit être documenté. Une déclaration orale « faute de budget » ne remplit pas ces conditions."),
 (3, "Selon le scénario 2, que manque-t-il à la déclaration d’applicabilité présentée par Karim ?",
  ["Les mesures de l’Annexe A non retenues avec la justification de leur exclusion, ainsi que l’état de mise en œuvre des mesures",
   "Le coût estimé et le budget alloué à chacune des mesures retenues, nécessaires à l’arbitrage de la direction",
   "Rien, car la déclaration d’applicabilité n’a vocation à présenter que les mesures effectivement retenues"], 0,
  "L’article 6.1.3 d) exige une déclaration d’applicabilité contenant les mesures nécessaires et la justification de leur inclusion, l’indication de leur mise en œuvre ou non, et la justification de l’exclusion de toute mesure de l’Annexe A. Les 93 mesures de l’Annexe A doivent donc toutes y apparaître."),
 (2, "Selon le scénario 2, la décision de réapprécier les risques « une fois par an, et seulement une fois par an » est-elle conforme ?",
  ["Oui, car ISO/IEC 27001 fixe une fréquence annuelle de réappréciation, indépendamment des changements qui surviennent entre-temps",
   "Non, car les risques doivent aussi être réappréciés lorsque des changements significatifs sont envisagés ou surviennent",
   "Non, car ISO/IEC 27001 impose une réappréciation complète des risques au moins chaque trimestre"], 1,
  "L’article 8.2 exige de réaliser les appréciations des risques à des intervalles planifiés, et lorsque des changements significatifs sont envisagés ou se produisent, en tenant compte des critères de 6.1.2 a). La norme ne fixe aucune fréquence ; exclure toute réappréciation hors calendrier contredit l’exigence."),
]))

# ---------------------------------------------------------------------------
SCEN.append((3, 'Kalia Pay · chronologie d’un incident', [
 "Kalia Pay est une fintech de 120 salariés qui traite les paiements de 3 000 commerçants. Son SMSI est certifié depuis dix-huit mois. Voici la chronologie, reconstituée après coup, de l’incident du 14 novembre.",
 "08 h 40 — Un développeur reçoit un e-mail imitant le service des ressources humaines, qui l’invite à consulter sa « nouvelle grille de primes ». Il saisit ses identifiants sur la page proposée. Il la trouve étrange mais ne le signale pas : « je ne savais pas à qui m’adresser ».",
 "09 h 15 — L’attaquant se connecte au VPN avec ces identifiants : l’accès distant n’exige qu’un mot de passe. Le compte du développeur dispose de droits d’administrateur sur tous les serveurs, attribués pour un projet terminé depuis un an et jamais retirés.",
 "11 h 30 — L’outil de supervision détecte une exportation massive de la base des commerçants vers une adresse IP inconnue et alerte l’équipe d’exploitation. L’analyste d’astreinte, recruté la semaine précédente, ne connaît pas la procédure de réponse et attend 13 h pour joindre son responsable.",
 "13 h 20 — Le responsable sécurité coupe le VPN et désactive le compte. L’analyse montre que les données exportées n’étaient pas chiffrées, alors que la déclaration d’applicabilité de Kalia Pay présente la mesure « Utilisation de la cryptographie » comme mise en œuvre.",
 "13 h 45 — Pour accélérer la remise en service, un administrateur réinstalle le serveur compromis, avant toute copie de ses journaux et de son disque.",
 "Jours suivants — Kalia Pay notifie la violation à l’autorité de contrôle et informe les commerçants concernés. Trois semaines plus tard, lors de la réunion de retour d’expérience, le directeur général propose de « ne pas en faire un dossier » et de clore l’incident sans autre suite.",
], [
 (1, "Selon le scénario 3 et la terminologie d’ISO/IEC 27000, comment qualifier la réception de l’e-mail frauduleux, considérée isolément, puis l’exportation de la base des commerçants ?",
  ["La réception de l’e-mail est déjà un incident de sécurité de l’information, et l’exportation est une non-conformité",
   "La réception de l’e-mail est un événement de sécurité de l’information, et l’exportation un incident de sécurité de l’information",
   "La réception de l’e-mail et l’exportation restent toutes deux de simples événements tant que l’enquête n’a pas établi de préjudice avéré"], 1,
  "Un événement de sécurité de l’information est une occurrence indiquant une possible violation de la sécurité ou une défaillance des mesures. Un incident est un ou plusieurs événements, liés et identifiés, susceptibles de nuire aux actifs ou de compromettre les activités. L’exportation avérée d’une base de données est un incident ; un e-mail suspect reçu, pris isolément, est un événement à signaler et à évaluer (ISO/IEC 27002, mesure 5.25)."),
 (4, "Selon le scénario 3, le développeur n’a pas signalé l’e-mail suspect faute de savoir à qui s’adresser. Quelle mesure traite directement ce point ?",
  ["Annexe A 6.8 Déclaration des événements de sécurité de l’information",
   "Annexe A 6.3 Sensibilisation, enseignement et formation en matière de sécurité de l’information",
   "Annexe A 5.26 Réponse aux incidents de sécurité de l’information"], 0,
  "La mesure 6.8 demande que le personnel dispose d’un mécanisme permettant de signaler rapidement, par des canaux appropriés, les événements de sécurité observés ou suspectés. Le développeur ignorait à qui s’adresser : le canal n’existait pas ou n’était pas connu. La sensibilisation (6.3) aide à reconnaître l’hameçonnage, mais c’est la mesure 6.8 qui organise le signalement ; la réponse aux incidents (5.26) n’intervient qu’ensuite. Un signalement à 08 h 40 aurait permis de bloquer le compte avant la connexion de 09 h 15."),
 (4, "Selon le scénario 3, quelle mesure aurait empêché l’attaquant de se connecter au VPN avec les seuls identifiants dérobés ?",
  ["Annexe A 8.23 Filtrage web",
   "Annexe A 8.17 Synchronisation des horloges",
   "Annexe A 8.5 Authentification sécurisée"], 2,
  "La mesure 8.5 demande de mettre en œuvre des technologies et procédures d’authentification sécurisée adaptées au niveau de sensibilité de l’accès ; pour un accès distant à privilèges, une authentification multifacteur rend inutilisable un mot de passe volé. Le filtrage web aurait pu bloquer la page frauduleuse, mais il n’agit pas sur la connexion au VPN."),
 (1, "Selon le scénario 3, le maintien des droits d’administrateur du développeur un an après la fin du projet méconnaît quel principe ?",
  ["La défense en profondeur", "Le moindre privilège", "La séparation des environnements"], 1,
  "Le principe du moindre privilège limite les droits de chacun au strict nécessaire à ses fonctions actuelles. Des droits attribués pour un projet terminé auraient dû être retirés : la mesure 5.18 (Droits d’accès) demande de les revoir régulièrement et de les ajuster lorsque le besoin change, la mesure 8.2 encadre spécifiquement les droits d’accès à privilèges."),
 (4, "Selon le scénario 3, l’analyste d’astreinte ne connaît pas la procédure de réponse. Quelle exigence d’ISO/IEC 27001 est en cause en premier lieu ?",
  ["L’article 7.4 Communication, car la procédure n’a pas été diffusée à l’ensemble du personnel",
   "L’article 7.2 Compétence, car l’organisation doit s’assurer que les personnes occupant des rôles de sécurité sont compétentes",
   "L’article 9.2 Audit interne, car la procédure de réponse aux incidents n’a été ni auditée ni testée avant l’obtention de la certification"], 1,
  "L’article 7.2 demande de déterminer les compétences nécessaires aux personnes dont le travail a une incidence sur la sécurité de l’information, de s’assurer qu’elles les possèdent et d’agir pour combler les écarts. Placer en astreinte un analyste non formé à la réponse aux incidents est une défaillance de compétence avant d’être un défaut de communication."),
 (2, "Selon le scénario 3, la déclaration d’applicabilité présente le chiffrement comme mis en œuvre alors que les données exportées étaient en clair. Que révèle cet écart ?",
  ["Un défaut sans conséquence, car la déclaration d’applicabilité énonce des intentions et non l’état réel des mesures",
   "Une faute de l’organisme de certification, qui aurait dû vérifier lui-même le chiffrement de chaque base de données",
   "Une non-conformité potentielle, car la déclaration doit indiquer si chaque mesure nécessaire est effectivement mise en œuvre"], 2,
  "L’article 6.1.3 d) exige que la déclaration d’applicabilité indique si les mesures nécessaires sont mises en œuvre ou non. Une mesure déclarée en place mais inopérante sur des données sensibles révèle un écart entre le SMSI documenté et la réalité, à traiter au titre de l’article 10.2. La responsabilité en incombe à l’organisation, pas à l’organisme de certification, qui procède par échantillonnage."),
 (4, "Selon le scénario 3, quelle mesure a été négligée lorsque l’administrateur a réinstallé le serveur avant toute copie ?",
  ["Annexe A 8.32 Gestion des changements",
   "Annexe A 5.28 Recueil de preuves",
   "Annexe A 8.10 Suppression des informations"], 1,
  "La mesure 5.28 demande d’établir et d’appliquer des procédures pour identifier, recueillir, acquérir et préserver les preuves liées aux événements de sécurité. Réinstaller le serveur a détruit les journaux et le disque, indispensables pour comprendre l’attaque et pour d’éventuelles suites judiciaires ou réglementaires."),
 (6, "Selon le scénario 3, que doit faire Kalia Pay face à la proposition du directeur général de clore l’incident sans suite ?",
  ["Clore l’incident, puisque le service est rétabli, l’autorité de contrôle notifiée dans les délais et les commerçants concernés tous informés",
   "Reporter toute décision à l’audit de surveillance, qui dira si des actions correctives sont attendues",
   "Tirer les enseignements de l’incident et traiter chaque défaillance par une action corrective, dont l’efficacité sera vérifiée"], 2,
  "La mesure 5.27 demande d’exploiter les connaissances acquises lors des incidents pour renforcer les mesures. Les défaillances relevées (signalement, authentification, droits, compétence, chiffrement, preuves) sont autant de non-conformités : l’article 10.2 impose d’en rechercher les causes, de mettre en œuvre des actions correctives et d’en examiner l’efficacité, sans attendre un audit externe."),
]))

# ---------------------------------------------------------------------------
SCEN.append((4, 'Val-Vert Agglomération · rapport d’audit interne', [
 "La communauté d’agglomération du Val-Vert (430 agents) a mis en place un SMSI couvrant ses services numériques aux usagers : état civil en ligne, inscriptions scolaires et paiement des services. L’audit interne annuel a eu lieu en septembre. Extrait du rapport :",
 "Constat 1 — Le plan de sensibilisation prévu pour l’année n’a pas été réalisé : 40 % des agents n’ont suivi aucune action de sensibilisation et plusieurs ignorent l’existence de la politique de sécurité.",
 "Constat 2 — Les objectifs de sécurité de l’information sont formulés, mais aucun indicateur ne permet de savoir s’ils sont atteints.",
 "Constat 3 — La procédure de gestion des accès prévoit une revue semestrielle des droits ; aucune revue n’a eu lieu depuis dix-huit mois.",
 "Constat 4 — Le service informatique a mis en place, de sa propre initiative, une authentification à deux facteurs sur la messagerie, au-delà de ce qu’exige la politique.",
 "Suites données. Nadia, responsable du SMSI, lance d’abord une revue des droits en urgence et supprime 85 comptes inutiles. Elle réunit ensuite les chefs de service : l’analyse montre que la revue semestrielle n’a plus été attribuée à personne depuis le départ de l’agent qui la réalisait. Nadia désigne un nouveau responsable et inscrit la revue dans l’outil de gestion des tâches, avec une alerte automatique à chaque échéance.",
 "Pour le constat 2, Nadia propose de supprimer purement et simplement les objectifs de sécurité, « puisqu’on ne sait pas les mesurer ».",
 "En décembre, la revue de direction examine les résultats de l’audit, l’état des actions correctives et les retours des usagers. La direction générale décide d’étendre le SMSI au service d’urbanisme en 2025.",
], [
 (6, "Selon le scénario 4, laquelle des actions de Nadia constitue une action corrective au sens d’ISO/IEC 27001 ?",
  ["La revue des droits en urgence et la suppression des 85 comptes inutiles",
   "La désignation d’un responsable de la revue et son inscription dans l’outil, avec alerte automatique",
   "La proposition de supprimer les objectifs de sécurité qui ne peuvent pas être mesurés"], 1,
  "Une correction élimine la non-conformité détectée : supprimer les comptes inutiles traite le symptôme. Une action corrective élimine la cause pour éviter la réapparition : l’analyse a montré que la revue n’avait plus de responsable, et c’est cette cause que traitent la désignation et l’alerte."),
 (6, "Selon le scénario 4, quelle étape de l’article 10.2 Nadia a-t-elle réalisée en réunissant les chefs de service ?",
  ["L’évaluation du besoin d’agir sur les causes, par la recherche de la cause de la non-conformité",
   "L’examen de l’efficacité de l’action corrective déjà mise en œuvre par le service informatique",
   "La revue de direction, qui doit précéder toute décision d’action corrective"], 0,
  "L’article 10.2 demande, après avoir réagi à la non-conformité, d’évaluer s’il faut agir pour éliminer ses causes : revoir la non-conformité, en déterminer les causes, rechercher si des non-conformités similaires existent ou pourraient survenir. La réunion a établi la cause : la tâche n’était plus attribuée."),
 (6, "Selon le scénario 4, que reste-t-il à faire pour clore l’action corrective du constat 3 ?",
  ["Rien, l’action corrective est close dès lors qu’un responsable a été désigné et l’alerte configurée",
   "Vérifier à la prochaine échéance que la revue a bien eu lieu, puis conserver la preuve de l’action et de son résultat",
   "Soumettre l’action à l’organisme de certification, seul habilité à constater son efficacité"], 1,
  "L’article 10.2 exige d’examiner l’efficacité de toute action corrective mise en œuvre et de conserver des informations documentées sur la nature des non-conformités, les actions menées et leurs résultats. L’efficacité se constate à l’usage, ici lorsque la première revue semestrielle a effectivement lieu ; c’est à l’organisation de la vérifier."),
 (2, "Selon le scénario 4, comment traiter le constat 4 (authentification à deux facteurs au-delà de la politique) ?",
  ["Comme une non-conformité, car toute pratique qui s’écarte de la politique de sécurité est non conforme",
   "Comme une non-conformité majeure, car le service informatique a modifié le système sans autorisation",
   "Comme un point fort ou une opportunité d’amélioration, qui peut conduire à mettre à jour la politique"], 2,
  "Une non-conformité est le non-respect d’une exigence. Aller au-delà d’une exigence ne la viole pas : l’auditeur peut relever un point fort ou une opportunité d’amélioration. L’organisation examinera s’il convient de généraliser la pratique et de mettre à jour la politique ; si elle juge que cette initiative contourne sa gestion des changements, c’est ce défaut qu’il faudra traiter, pas la mesure elle-même."),
 (2, "Selon le scénario 4, la proposition de Nadia de supprimer les objectifs de sécurité est-elle acceptable ?",
  ["Non, car l’article 6.2 exige des objectifs, mesurables lorsque c’est possible, avec la manière d’évaluer leurs résultats",
   "Oui, car les objectifs de sécurité sont facultatifs lorsque l’organisation ne dispose pas d’indicateurs",
   "Oui, à condition de justifier l’absence d’objectifs dans la déclaration d’applicabilité"], 0,
  "L’article 6.2 impose d’établir des objectifs de sécurité de l’information aux fonctions et niveaux concernés, mesurables lorsque c’est possible, surveillés et mis à jour, en précisant comment leurs résultats seront évalués. L’absence d’indicateur appelle une correction des objectifs, pas leur suppression ; la déclaration d’applicabilité ne porte que sur les mesures."),
 (4, "Selon le scénario 4, quelle exigence d’ISO/IEC 27001 le constat 1 met-il en défaut ?",
  ["L’article 7.2 Compétence, car les agents n’ont pas reçu la formation technique nécessaire à leur poste",
   "L’article 7.3 Sensibilisation, car le personnel doit connaître la politique et sa contribution à l’efficacité du SMSI",
   "L’article 7.5 Informations documentées, car la politique n’est pas maîtrisée comme information documentée"], 1,
  "L’article 7.3 exige que les personnes travaillant sous le contrôle de l’organisation soient sensibilisées à la politique de sécurité, à leur contribution à l’efficacité du SMSI et aux conséquences d’un manquement. Des agents qui ignorent l’existence de la politique en sont la preuve directe. L’article 7.2 vise les compétences requises par les personnes dont le travail a une incidence sur la sécurité."),
 (6, "Selon le scénario 4, la décision de la direction générale d’étendre le SMSI au service d’urbanisme relève de quoi ?",
  ["D’une action corrective, qui répond au constat 1 du rapport d’audit interne et à l’insuffisance de sensibilisation des agents",
   "D’une correction, imposée par l’audit interne et à réaliser avant la fin de l’année",
   "D’une décision d’amélioration issue de la revue de direction, dont la mise en œuvre devra être planifiée"], 2,
  "L’article 9.3.3 prévoit que les résultats de la revue de direction comprennent les décisions relatives aux opportunités d’amélioration et aux besoins de modification du SMSI ; l’article 10.1 demande d’améliorer continuellement le système. Étendre le domaine d’application est une telle décision, à mettre en œuvre de façon planifiée (article 6.3). Elle ne répond à aucune non-conformité."),
]))

# ---------------------------------------------------------------------------
SCEN.append((5, 'Pixelnord · notes d’entretiens', [
 "Pixelnord est un studio de jeux vidéo lillois de 250 personnes, dont la moitié en télétravail. Un éditeur international lui confie le développement d’un jeu très attendu, à condition que le code source et les éléments graphiques soient protégés. Léa, nouvelle responsable de la sécurité, rencontre les responsables d’équipe pendant sa première semaine. Extraits de ses notes :",
 "Responsable de production — « Les graphistes partagent les maquettes non publiées avec nos prestataires d’animation par des liens publics de stockage en ligne. C’est plus rapide que les procédures. »",
 "Directeur technique — « Le code source est dans notre dépôt. Tout le monde y a accès en lecture et en écriture, stagiaires compris : ça évite les demandes. Pour les tests, on utilise une copie des comptes réels des joueurs de notre précédent jeu. »",
 "Responsable des ressources humaines — « Les contrats de travail ne parlent pas de confidentialité : l’éditeur ne l’a pas demandé explicitement. Quand quelqu’un part, on récupère son badge, mais pas toujours son ordinateur portable. »",
 "Responsable informatique — « Les télétravailleurs utilisent leurs ordinateurs personnels. On leur a envoyé une note de cinq pages sur les bonnes pratiques, mais je ne sais pas qui l’a lue. »",
 "Office manager — « Les bureaux sont en open space. Les esquisses des personnages restent souvent sur les tables le soir, et l’équipe de ménage d’un prestataire passe à 21 h. »",
 "À l’issue de ces entretiens, Léa rédige un plan d’action.",
], [
 (1, "Selon le scénario 5, quel principe le partage des maquettes par liens publics menace-t-il, et quelle mesure traite directement ce point ?",
  ["La disponibilité, traitée par Annexe A 8.14 Redondance des moyens de traitement de l’information",
   "La confidentialité, traitée par Annexe A 5.14 Transfert des informations",
   "L’intégrité, traitée par Annexe A 8.17 Synchronisation des horloges"], 1,
  "Un lien public rend les maquettes accessibles à quiconque l’obtient : la confidentialité est menacée. La mesure 5.14 demande que des règles, procédures ou accords encadrent tous les types de transfert d’informations, en interne comme avec les tiers. Le recours aux prestataires d’animation relève aussi des mesures sur les relations avec les fournisseurs (5.19 à 5.22)."),
 (4, "Selon le scénario 5, quelle mesure Léa doit-elle appliquer en priorité au dépôt de code source ouvert en écriture à tous ?",
  ["Annexe A 8.4 Accès au code source",
   "Annexe A 8.6 Dimensionnement",
   "Annexe A 7.12 Sécurité du câblage"], 0,
  "La mesure 8.4 demande de gérer de manière appropriée les accès en lecture et en écriture au code source, aux outils de développement et aux bibliothèques logicielles. Donner l’écriture à tous, stagiaires compris, expose le code à des modifications non autorisées, accidentelles ou malveillantes, et à des fuites."),
 (4, "Selon le scénario 5, l’utilisation d’une copie des comptes réels des joueurs pour les tests est-elle une bonne pratique ?",
  ["Oui, car des données réelles rendent les tests plus représentatifs, ce qui sert la qualité du jeu",
   "Non, car les informations de test doivent être choisies et protégées, par exemple par masquage des données personnelles",
   "Oui, à condition que l’environnement de test soit hébergé sur les mêmes serveurs que la production"], 1,
  "La mesure 8.33 demande que les informations de test soient sélectionnées, protégées et gérées de manière appropriée ; la mesure 8.11 recommande le masquage des données, en particulier des données à caractère personnel. Héberger les tests avec la production contredirait en outre la mesure 8.31 (Séparation des environnements)."),
 (2, "Selon le scénario 5, l’absence de clause de confidentialité dans les contrats est-elle justifiée par le silence de l’éditeur ?",
  ["Oui, car les engagements de confidentialité ne s’imposent que lorsqu’un client, un éditeur ou une autorité les exige expressément par contrat",
   "Non, car la confidentialité doit figurer uniquement dans la politique de sécurité, et non dans les contrats",
   "Non, car les conditions d’emploi doivent préciser les responsabilités de sécurité, appuyées par des accords de confidentialité"], 2,
  "La mesure 6.2 demande que les accords contractuels d’emploi indiquent les responsabilités du personnel et de l’organisation en matière de sécurité de l’information ; la mesure 6.6 prévoit des accords de confidentialité ou de non-divulgation reflétant les besoins de protection de l’organisation. Ces besoins découlent des risques identifiés par Pixelnord, pas des seules demandes de l’éditeur."),
 (2, "Selon le scénario 5, quelle mesure de l’Annexe A n’est pas respectée lorsqu’un salarié part sans rendre son ordinateur portable ?",
  ["Annexe A 5.9 Inventaire des informations et autres actifs associés",
   "Annexe A 5.11 Restitution des actifs",
   "Annexe A 8.6 Dimensionnement"], 1,
  "La mesure 5.11 demande que le personnel et les autres parties intéressées restituent tous les actifs de l’organisation en leur possession au changement ou à la fin de leur emploi, contrat ou accord. L’inventaire (5.9) permet de savoir ce qui doit être restitué, mais c’est bien la restitution qui fait ici défaut."),
 (4, "Selon le scénario 5, que manque-t-il à la note envoyée aux télétravailleurs ?",
  ["Une signature de chaque télétravailleur, qui suffit à démontrer qu’il a lu et compris les bonnes pratiques",
   "Des mesures propres au télétravail et une sensibilisation dont l’effet est vérifié, au-delà du simple envoi",
   "Une validation de la note par l’organisme de certification avant sa diffusion au personnel"], 1,
  "La mesure 6.7 demande des mesures de sécurité adaptées au travail à distance, ce qui inclut l’encadrement des ordinateurs personnels. L’article 7.3 exige que les personnes soient effectivement sensibilisées, et la mesure 6.3 recommande d’évaluer la compréhension à l’issue des actions de sensibilisation. Envoyer une note sans savoir qui l’a lue ne démontre rien."),
 (4, "Selon le scénario 5, quelle mesure Léa doit-elle inscrire à son plan d’action pour les esquisses laissées sur les tables le soir ?",
  ["Annexe A 7.4 Surveillance de la sécurité physique",
   "Annexe A 7.7 Bureau propre et écran vide",
   "Annexe A 7.12 Sécurité du câblage"], 1,
  "La mesure 7.7 demande de définir et d’appliquer des règles de bureau propre pour les documents papier et les supports amovibles, et d’écran vide pour les moyens de traitement. Une vidéosurveillance (7.4) pourrait détecter un vol, mais n’empêche pas qu’un document laissé sur un bureau soit vu ou photographié par le personnel de ménage."),
]))

# ---------------------------------------------------------------------------
SCEN.append((6, 'Hydréa · décisions du comité de direction', [
 "Hydréa, régie des eaux d’une métropole de 600 agents, distribue l’eau potable à 900 000 habitants. Elle est certifiée ISO 9001 et ISO 14001. Avec la transposition de la directive NIS 2, elle relève désormais des entités soumises à des obligations de gestion des risques de cybersécurité et de notification des incidents.",
 "Le conseil d’administration demande un plan d’action. Le comité de direction retient les orientations suivantes :",
 "1. Mettre en place un SMSI conforme à ISO/IEC 27001 et le faire certifier dans les deux ans, en l’intégrant au système de management qualité et environnement existant.",
 "2. S’appuyer sur ISO/IEC 27005 pour la gestion des risques et sur ISO/IEC 27002 pour le choix et la mise en œuvre des mesures.",
 "3. Inclure dans le domaine d’application les systèmes de télégestion des stations de pompage et de traitement.",
 "4. Faire appel à un organisme de certification. La directrice qualité suggère plutôt de « demander directement l’accréditation au COFRAC, ce sera plus rapide ».",
 "5. Le directeur des systèmes d’information propose d’adopter à la place le NIST Cybersecurity Framework, « plus moderne », et de renoncer à la certification.",
 "6. La direction juridique rappelle qu’un ordre de modification du dosage de chlore envoyé par la télégestion doit pouvoir être attribué de façon certaine à son émetteur, qui ne doit pas pouvoir le contester.",
 "Le comité confie enfin la conduite du projet au directeur des opérations.",
], [
 (2, "Selon le scénario 6, l’intégration du SMSI au système de management qualité et environnement est-elle envisageable ?",
  ["Non, car ISO/IEC 27001 exige un système de management distinct, audité séparément des autres",
   "Oui, mais à condition de renoncer aux certifications ISO 9001 et ISO 14001 au profit d’ISO/IEC 27001",
   "Oui, car les normes ISO de système de management partagent une structure harmonisée qui facilite leur intégration"], 2,
  "ISO/IEC 27001, ISO 9001 et ISO 14001 suivent la structure harmonisée des normes ISO de système de management (anciennement Annexe SL) : mêmes articles de haut niveau, texte et définitions communs. Un système de management intégré peut répondre aux trois normes, chacune restant certifiable."),
 (1, "Selon le scénario 6, le recours à ISO/IEC 27005 et à ISO/IEC 27002 décidé dans l’orientation 2 est-il cohérent ?",
  ["Oui, car ISO/IEC 27005 guide la gestion des risques et ISO/IEC 27002 décrit des mesures de référence, sans être certifiables",
   "Non, car ISO/IEC 27005 énonce les exigences certifiables du SMSI, tandis qu’ISO/IEC 27002 traite de la protection de la vie privée",
   "Non, car ISO/IEC 27001 interdit de recourir à d’autres normes pour concevoir le SMSI"], 0,
  "ISO/IEC 27005 fournit des lignes directrices pour gérer les risques de sécurité de l’information, en appui des exigences d’ISO/IEC 27001 ; ISO/IEC 27002 fournit un ensemble de référence de mesures et des recommandations de mise en œuvre. Seule ISO/IEC 27001 contient des exigences certifiables ; la protection de la vie privée relève d’ISO/IEC 27701."),
 (1, "Selon le scénario 6, que penser de la suggestion de « demander directement l’accréditation au COFRAC » ?",
  ["Elle est pertinente, car l’accréditation remplace la certification pour les organismes publics",
   "Elle confond deux notions : le COFRAC accrédite les organismes de certification, qui certifient les organisations",
   "Elle est pertinente, car le COFRAC certifie directement les SMSI des entités soumises à la directive NIS 2, sans intermédiaire"], 1,
  "L’accréditation est la reconnaissance, par un organisme national comme le COFRAC en France, de la compétence et de l’impartialité d’un organisme d’évaluation de la conformité. C’est cet organisme de certification accrédité qui audite et certifie le SMSI d’une organisation. Hydréa ne peut pas demander une accréditation pour elle-même."),
 (1, "Selon le scénario 6, la proposition d’adopter le NIST Cybersecurity Framework à la place d’ISO/IEC 27001 est-elle adaptée à l’objectif fixé ?",
  ["Non, car le NIST Cybersecurity Framework est un cadre volontaire, qui ne donne lieu à aucune certification",
   "Oui, car le NIST Cybersecurity Framework est une norme certifiable, reconnue de manière équivalente en Europe",
   "Oui, car le NIST Cybersecurity Framework est le référentiel imposé par la directive NIS 2"], 0,
  "Le NIST Cybersecurity Framework est un cadre volontaire de gestion des risques de cybersécurité. Il peut compléter un SMSI, mais il ne fait l’objet d’aucune certification et n’est pas imposé par NIS 2. Il ne permet donc pas d’atteindre l’objectif fixé par le conseil : une certification ISO/IEC 27001 dans les deux ans."),
 (1, "Selon le scénario 6, quelle propriété de la sécurité de l’information la direction juridique vise-t-elle dans l’orientation 6 ?",
  ["La disponibilité", "La confidentialité", "La non-répudiation"], 2,
  "ISO/IEC 27000 définit la sécurité de l’information comme la préservation de la confidentialité, de l’intégrité et de la disponibilité, en précisant que d’autres propriétés peuvent être concernées, comme l’authenticité, l’imputabilité, la non-répudiation et la fiabilité. La non-répudiation est la capacité à prouver qu’une action a eu lieu et qui en est l’auteur, de sorte que celui-ci ne puisse pas la contester."),
 (3, "Selon le scénario 6, comment Hydréa doit-elle prendre en compte la directive NIS 2 dans la planification de son SMSI ?",
  ["Elle n’a pas à la prendre en compte, car la certification ISO/IEC 27001 vaut à elle seule présomption de conformité à NIS 2",
   "Comme une exigence légale à identifier dans le contexte, puis à refléter dans l’appréciation des risques et le choix des mesures",
   "Uniquement après l’obtention de la certification, lors de la première revue de direction"], 1,
  "Les obligations légales et réglementaires font partie des enjeux et des exigences des parties intéressées (articles 4.1 et 4.2) ; elles orientent l’appréciation des risques et le choix des mesures, et la mesure 5.31 d’ISO/IEC 27002 demande de les identifier et de les tenir à jour. Un SMSI certifié aide fortement à satisfaire NIS 2, mais la certification n’en vaut pas conformité automatique."),
 (2, "Selon le scénario 6, que doit encore faire la direction après avoir confié le projet au directeur des opérations, au titre de l’article 5.3 ?",
  ["Faire valider cette désignation par l’organisme de certification avant le lancement des travaux, comme l’exige la procédure de certification",
   "Rien de plus, car la désignation d’un responsable de projet satisfait entièrement l’article 5.3",
   "Attribuer et communiquer les responsabilités et autorités des rôles de sécurité, dont le compte rendu des performances du SMSI"], 2,
  "L’article 5.3 demande à la direction de s’assurer que les responsabilités et autorités des rôles concernés par la sécurité de l’information sont attribuées et communiquées au sein de l’organisation, notamment pour assurer la conformité du SMSI à la norme et pour rendre compte de ses performances à la direction. Désigner un chef de projet n’en est qu’une partie."),
]))

# ---------------------------------------------------------------------------
total_q = sum(len(s[3]) for s in SCEN)
targets = [i % 3 for i in range(total_q)]
random.Random(27001).shuffle(targets)

out, n = [], 0
for num, title, context, qs in SCEN:
    for domain, q, opts, correct, exp in qs:
        n += 1
        assert domain in DOMAINS and 0 <= correct < len(opts) == 3, (n, q)
        right = opts[correct]
        others = [o for i, o in enumerate(opts) if i != correct]
        correct = targets[n - 1]
        opts = others[:correct] + [right] + others[correct:]
        out.append({'n': n, 'quiz': num, 'quizTitle': title, 'domain': domain,
                    'scenario': num, 'scenarioText': context, 'question': q,
                    'options': opts, 'correct': correct, 'explanation': exp})

json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- controles de qualite -------------------------------------------------
dom = Counter(q['domain'] for q in out)
pos = Counter('ABC'[q['correct']] for q in out)
longest = sum(1 for q in out if max(range(3), key=lambda i: len(q['options'][i])) == q['correct'])
print('%d questions, %d scenarios' % (len(out), len(SCEN)))
print('par domaine   :', dict(sorted(dom.items())))
print('position      :', dict(sorted(pos.items())))
print('bonne = la plus longue : %d / %d (hasard ~ 1/3 = %d)' % (longest, len(out), len(out)//3))
print('par scenario  :', [len(s[3]) for s in SCEN], '| paragraphes :', [len(s[2]) for s in SCEN])
