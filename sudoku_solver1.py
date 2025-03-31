from colorama import Fore, Style, init
init(autoreset=True)
from itertools import product
import copy
import time
import threading
import signal
import sys
import keyboard


class SudokuGrid:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.original_grid = [[0 for _ in range(9)] for _ in range(9)]
        self.time_warnings = [60, 300, 600, 1200]  # 1min, 5min, 10min, 20min in seconds
        self.time_messages = [
            "🕐 Toujours en cours après 1 minute...",
            "🕑 Toujours en cours après 5 minutes...",
            "🕒 Toujours en cours après 10 minutes...",
            "🕓 Toujours en cours après 20 minutes..."
            
        ]
        self.solving_start_time = None
        self.solving_complete = False
        self.attempts = 0
        self.max_attempts = 1000000000  # Limite raisonnable pour éviter une boucle infinie
        self.stop_solving = False
    
    def start_timer(self):
        """Thread pour surveiller le temps et afficher les messages"""
        if not self.solving_start_time:
            return

        while not self.solving_complete:
            current_time = time.time() - self.solving_start_time
            for i, (warn_time, msg) in enumerate(zip(self.time_warnings, self.time_messages)):
                if current_time > warn_time:
                    print(msg)
                    # Supprimer ce temps d'avertissement pour éviter les répétitions
                    self.time_warnings[i] = float('inf')
            
            time.sleep(1)  # Vérifier toutes les secondes

    def set_timeout(self, timeout_minutes=25):
        """
        Définit un timeout global pour arrêter la résolution après un temps donné
        """
        def timeout_handler(signum, frame):
            print(f"\n🚨 Timeout atteint après {timeout_minutes} minutes. Arrêt forcé.")
            self.stop_solving = True
            sys.exit(0)

        # Configurer le gestionnaire de signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_minutes * 60)  # Convertir minutes en secondes

    def solve_with_timer(self, solve_method):
        """Wrapper pour exécuter la méthode de résolution avec un timer"""
        start_time = time.time()
        
        # Démarrer le thread de timer
        timer_thread = threading.Thread(target=self.start_timer, args=(start_time,))
        timer_thread.start()

        try:
            # Exécuter la méthode de résolution
            result = solve_method()
            self.solved = result
            return result
        finally:
            # Arrêter le thread de timer
            self.stop_timer = True
            timer_thread.join()

    def from_file(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            row = []
            for char in line.strip():
                if char == '_':
                    row.append(0)
                elif char.isdigit():
                    row.append(int(char))
            self.grid[i] = row
            self.original_grid[i] = row.copy() 

    def display(self):
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("-" * 21)
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end=" ")

                num = self.grid[i][j]
                original = self.original_grid[i][j]

                if num == 0:
                    print(".", end=" ")
                elif num == original:
                    print(Fore.BLUE + str(num), end=" ")
                else:
                    print(Fore.GREEN + str(num), end=" ")
            print()  # nouvelle ligne

    
    def solve_brute_force(self):
        # Réinitialiser les variables de suivi
        self.solving_start_time = time.time()
        self.solving_complete = False

        # Démarrer le thread de timer
        timer_thread = threading.Thread(target=self.start_timer)
        timer_thread.start()
       
        # Configurer la touche d'arrêt
        self.setup_stop_key()
      
        try:
            # Trouver toutes les positions vides
            empty_positions = [(i, j) for i in range(9) for j in range(9) if self.grid[i][j] == 0]

            # Générer toutes les combinaisons possibles de chiffres 1 à 9
            for values in product(range(1, 10), repeat=len(empty_positions)):
               
                # Vérifier si l'arrêt a été demandé
                if self.stop_solving:
                   print("\nRésolution interrompue par l'utilisateur.")
                   return False
                
                test_grid = copy.deepcopy(self.grid)
                for (row, col), val in zip(empty_positions, values):
                    test_grid[row][col] = val

                if self.is_full_and_valid(test_grid):
                    self.grid = test_grid
                    return True

            return False  # Aucune combinaison n'a fonctionné
        finally:
            # Indiquer que la résolution est terminée
            self.solving_complete = True
            timer_thread.join()
          
            # Supprimer le gestionnaire d'événement
            keyboard.unhook_all()


    def solve_backtracking(self):
        # Démarrer le timer
        self.solving_start_time = time.time()
        self.solving_complete = False
        timer_thread = threading.Thread(target=self.start_timer)
        timer_thread.start()

        # Configurer la touche d'arrêt
        self.setup_stop_key()


        try:
            def backtrack():

                 # Vérifier si l'arrêt a été demandé
                if self.stop_solving:
                   return False
                

                for row in range(9):
                    for col in range(9):
                        if self.grid[row][col] == 0:
                            for num in range(1, 10):

                                # Vérifier à nouveau si l'arrêt a été demandé
                                if self.stop_solving:
                                   return False
                                
                                if self.is_valid(num, row, col):
                                    self.grid[row][col] = num
                                    if backtrack():
                                        return True
                                    self.grid[row][col] = 0  # Backtrack
                            return False  # Aucun chiffre possible ici → échec
                return True  # Tout est rempli

            result = backtrack()
            return result
        finally:
            # Indiquer que la résolution est terminée
            self.solving_complete = True
            timer_thread.join()
            
            # Supprimer le gestionnaire d'événement pour éviter les effets secondaires
            keyboard.unhook_all()

    def solve_with_timeout(self, solve_method):
        """
        Wrapper pour exécuter la méthode de résolution avec un timeout
        """
        # Configurer le timeout global
        self.set_timeout()

        # Réinitialiser le flag d'arrêt
        self.stop_solving = False
        
        # Démarrer le timer
        self.solving_start_time = time.time()
        
        # Démarrer le thread de surveillance
        timer_thread = threading.Thread(target=self.start_timer)
        timer_thread.start()

        try:
            # Exécuter la méthode de résolution
            result = solve_method()
            self.solving_complete = True
           
            if self.stop_solving:
               print("Résolution arrêtée par l'utilisateur.")
               return False
            return result
        
        except SystemExit:
            print("⏰ Résolution interrompue par timeout")
            return False
        finally:
            # Désactiver l'alarme
            signal.alarm(0)
            # Arrêter le thread de timer
            self.solving_complete = True
            timer_thread.join()

            # Supprimer tous les gestionnaires d'événements
            keyboard.unhook_all()

    def is_full_and_valid(self, grid):
        # Vérifie lignes, colonnes et blocs
        for i in range(9):
            if not self.is_unique(grid[i]):  # lignes
                return False
            if not self.is_unique([grid[j][i] for j in range(9)]):  # colonnes
                return False

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                block = [
                    grid[i][j]
                    for i in range(box_row, box_row + 3)
                    for j in range(box_col, box_col + 3)
                ]
                if not self.is_unique(block):
                    return False

        return True


    def is_unique(self, group):
        nums = [num for num in group if num != 0]
        return len(nums) == len(set(nums))

    def is_valid(self, num, row, col):
        # Vérifier la ligne
        if num in self.grid[row]:
            return False

        # Vérifier la colonne
        for i in range(9):
            if self.grid[i][col] == num:
                return False

        # Vérifier la sous-grille 3x3
        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.grid[i][j] == num:
                    return False

        return True

    def is_complete(self):
        return all(0 not in row for row in self.grid)
   


    def setup_stop_key(self):
        """Configure une touche pour arrêter la résolution"""
        def key_pressed(e):
            if e.name == 's':
                print("\n🛑 Arrêt de la résolution demandé par l'utilisateur.")
                self.stop_solving = True

        def check_key():
            print("Appuyez sur 's' pour arrêter la résolution à tout moment.")
            while not self.solving_complete:
                if keyboard.is_pressed('s'):
                   print("\n🛑 Arrêt de la résolution demandé par l'utilisateur.")
                   self.stop_solving = True
                   break
                time.sleep(0.1)  # Vérifier toutes les 100 ms
    
        # Démarrer le thread de vérification des touches
        key_thread = threading.Thread(target=check_key)
        key_thread.daemon = True  # Pour que le thread se termine quand le programme principal se termine
        key_thread.start()
    
        # Stocker le thread pour pouvoir le joindre plus tard
        self.key_thread = key_thread        
    
        # Enregistrer le gestionnaire d'événement pour la touche 's'
        keyboard.on_press(key_pressed)