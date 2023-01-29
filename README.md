# Survivor_game
Le survivor game est un jeu où nous contrôlons un personnage vert qui peut se déplacer. Les autres personnages sont des agents qui se déplacent sur la carte. Si le joueur rentre dans leurs champs de visions, ils se mettent à le pourchasser. Si le joueur réussit à sortir de leurs champs de visions, ils iront à la dernière position connue du joueur.

## Lancer le jeu
Pour lancer le jeu, il faut se placer dans cft, puis:  
python3 Base-CFT.py

## Que contient l'archive:
L'archive contient 3 dossiers:  
- un README
- un dossier contenant le code du jeu nommé "cft"
- un dossier de test nommé "test_Astar"
- un fichier deplacement.pdf

## Jeu actuel
### Règle de la carte
La carte du jeu est une carte où le joueur peut se balader librement. Il existe 2 types d'obstacles: les murs et les murets, en noir et en gris respectivement. Les 2 types d'obstacles bloquent le chemin, mais les murets laissent les agents voir au travers contrairement aux murs.

### Champs de vision
Le champs de vision des agents est défini par la variable wideRange qui est propre à chaque type d'agent. Dans la fonction "update_sightAgent" du fichier Base-CFT, on défini la largeur du champs de vision de l'agent. Puis on lance un rayon partant de l'agent pour tous les angles compris dans la largeur du champs de vision. Ces rayons renvoient la position du mur si il se trouve sur le chemin des rayons. Il renvoi aussi la position du joueur si il le croise.  
La position du mur sert pour l'affichage graphique, si le rayon croise un mur, on n'affichera pas le rayon au dela de la position détecté.  
Ainsi le champ de vision des agents s'adaptera à l'environnement. Concrétement, la vision de l'agent est composé de plusieurs triangles.
Lorsque la portée maximale d'un rayon est différente de son prédecesseur, on ajoute dans une liste l'index de ce rayon. Cela signifie que la portée maximale est différente donc on aura besoin de tracer un nouveau triangle pour le représenter.  
Pour dessiner le champs de vision, la fonction pygame.draw.polygon() est utilisé dans Agent.py.

### Agents
Il y a actuellement 4 types d'agents différents, ils ont chacun une couleur, une vitesse, une vitesse de rotation, une portée et une largeur de vision différente. Lorsque le joueur entre dans leurs champs de vision, leurs couleurs deviendra instantanément rouge pour signaler qu'ils ont détecté le joueur. Si ce dernier échappe à leurs champs de vision, la couleur deviendra orange et ils iront à la dernière position connue du joueur.
Seul l'agent rose possède un comportement particulier, lorsqu'il croise le joueur, toutes ses statistiques sont modifié dans le script Base-CFT.py.

Une mécanique de rebond a été implémenté dans le jeu, les détails sont explicités dans le fichier deplacement.pdf.



### A*
2 algorithmes A* ont été implémenté pour le projet.  Pour passer de l'un à l'autre il suffit de changer la ligne 10 du fichier Base-CFT de:  
 import Astar as astar  
 à   
 import AstarArray as astar  
 Le premier algorithme A* utilise une classe "Node" tandis que l'algorithme AstarArray utilise des tableaux numpy comme son nom l'indique. 
 Le premier algorithme a été inspiré d'un code trouvé sur internet dont voici la source:  
 https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2  
 J'ai implémenté le 2 ème entièrement afin de pouvoir comparer et comprendre le fonctionnement des 2 algorithmes.

## Problèmes
- L'affichage graphique des champs de vision des agents n'est pas au point. Leurs champs de visions peuvent traverser les murs. (Il s'agit bien juste de l'affichage graphique, ils ne détectent pas vraiment le joueur derrière le mur)

- Les algorithmes A* souffrent également de problèmes.
Afin de bien les représenter, j'ai créer 2 cartes de jeu.  
On peut passer de une à l'autre à la ligne 431 de Base-CFT:  
scene._grid.loadTextMaze("maze_difficult.maz")  
ou bien:  
scene._grid.loadTextMaze("maze.maz")  

La différence se situe sur les obstacles à droite de la carte, "maze_difficult" possède un long obstacle qu'il faut contourner tandis que "maze" contient des trous dans cet obstacle.  
De par leurs fonctionnements, les algorithmes A* ont du mal à contourner l'obstacle de "maze_difficult" car ils essayent d'aller au plus direct.   

Sur ma machine, Astar avec "Node" fonctionne en temps réel si il n'y a pas de "grand obstacle". Dans le cas du grand obstacle, le jeu plante.      
Dans le cas de AstarArray: Le jeu ne plante jamais mais le AstarArray fait lagger le jeu avec ou sans obstacles.  


## Intentions sur le plus long terme

- Pour continuer le jeu, j'aurai rajouter une barre de vie au joueur.
Si le joueur est à portée de tir des agents (portée de tir qui sera inférieur à leur portée de vision), des explosions se déclencherons sur le joueur et il prendra des dégats. Le jeu deviendra alors un jeu de survie où des agents arriveront par vague.
L'animation de l'explosion est toujours présente dans le jeu en cliquant sur l'écran.
Enfin j'aurai rajouter une notion de communication entre les agents ennemis, afin qu'ils se rendent tous à la position du joueur reperé par leurs semblables.  
Enfin il aurait pu être également intéressant d'utiliser des cartes d'influences pour le joueur pour qu'une IA puisse jouer au jeu.

- Pour étudier davantage les 2 algorithmes A*, il aurait fallu tester les 2 algorithmes sur des maps fixes et enregistrer le temps qu'ils prennent à s'éxecuter.  
A priori, le AstarArray devrait mieux marcher sur les tableaux de grande taille. Il pourrai être intéressant d'étudier à partir de quelle dimension de map, un algorithme devient plus avantageux que l'autre. 

Un test sommaire de rapidité peut être executé dans le dossier "test_Astar" grâce au module time. 

