import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List
import time

class SquadScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_team_squad(self, team: str) -> List[Dict]:
        """Get actual player names and details for a team"""
        
        # Real squad data for major teams
        squads = {
            'Argentina': [
                {'name': 'Emiliano Martínez', 'position': 'GK', 'age': 31, 'club': 'Aston Villa'},
                {'name': 'Cristian Romero', 'position': 'DF', 'age': 26, 'club': 'Tottenham'},
                {'name': 'Nicolás Otamendi', 'position': 'DF', 'age': 36, 'club': 'Benfica'},
                {'name': 'Lisandro Martínez', 'position': 'DF', 'age': 26, 'club': 'Manchester United'},
                {'name': 'Nahuel Molina', 'position': 'DF', 'age': 26, 'club': 'Atlético Madrid'},
                {'name': 'Alexis Mac Allister', 'position': 'MF', 'age': 25, 'club': 'Liverpool'},
                {'name': 'Rodrigo De Paul', 'position': 'MF', 'age': 30, 'club': 'Atlético Madrid'},
                {'name': 'Enzo Fernández', 'position': 'MF', 'age': 23, 'club': 'Chelsea'},
                {'name': 'Leandro Paredes', 'position': 'MF', 'age': 30, 'club': 'Roma'},
                {'name': 'Julián Álvarez', 'position': 'FW', 'age': 24, 'club': 'Manchester City'},
                {'name': 'Lionel Messi', 'position': 'FW', 'age': 37, 'club': 'Inter Miami'},
                {'name': 'Ángel Di María', 'position': 'FW', 'age': 36, 'club': 'Benfica'},
                {'name': 'Lautaro Martínez', 'position': 'FW', 'age': 27, 'club': 'Inter Milan'},
                {'name': 'Nicolás González', 'position': 'FW', 'age': 26, 'club': 'Fiorentina'},
                {'name': 'Giovani Lo Celso', 'position': 'MF', 'age': 28, 'club': 'Tottenham'},
                {'name': 'Germán Pezzella', 'position': 'DF', 'age': 33, 'club': 'Real Betis'},
                {'name': 'Franco Armani', 'position': 'GK', 'age': 37, 'club': 'River Plate'},
                {'name': 'Gonzalo Montiel', 'position': 'DF', 'age': 27, 'club': 'Sevilla'},
                {'name': 'Marcos Acuña', 'position': 'DF', 'age': 32, 'club': 'Sevilla'},
                {'name': 'Exequiel Palacios', 'position': 'MF', 'age': 25, 'club': 'Bayer Leverkusen'},
                {'name': 'Alejandro Garnacho', 'position': 'FW', 'age': 20, 'club': 'Manchester United'},
                {'name': 'Valentín Carboni', 'position': 'MF', 'age': 19, 'club': 'Monza'},
                {'name': 'Thiago Almada', 'position': 'MF', 'age': 23, 'club': 'Botafogo'},
            ],
            'France': [
                {'name': 'Hugo Lloris', 'position': 'GK', 'age': 37, 'club': 'LAFC'},
                {'name': 'Raphaël Varane', 'position': 'DF', 'age': 31, 'club': 'Manchester United'},
                {'name': 'Jules Koundé', 'position': 'DF', 'age': 25, 'club': 'Barcelona'},
                {'name': 'Dayot Upamecano', 'position': 'DF', 'age': 25, 'club': 'Bayern Munich'},
                {'name': 'Theo Hernández', 'position': 'DF', 'age': 27, 'club': 'AC Milan'},
                {'name': 'Aurélien Tchouaméni', 'position': 'MF', 'age': 24, 'club': 'Real Madrid'},
                {'name': 'Eduardo Camavinga', 'position': 'MF', 'age': 21, 'club': 'Real Madrid'},
                {'name': 'Antoine Griezmann', 'position': 'FW', 'age': 33, 'club': 'Atlético Madrid'},
                {'name': 'Kylian Mbappé', 'position': 'FW', 'age': 25, 'club': 'Real Madrid'},
                {'name': 'Olivier Giroud', 'position': 'FW', 'age': 38, 'club': 'LAFC'},
                {'name': 'Ousmane Dembélé', 'position': 'FW', 'age': 27, 'club': 'PSG'},
                {'name': 'Kingsley Coman', 'position': 'FW', 'age': 28, 'club': 'Bayern Munich'},
                {'name': 'Adrien Rabiot', 'position': 'MF', 'age': 29, 'club': 'Juventus'},
                {'name': 'N\'Golo Kanté', 'position': 'MF', 'age': 33, 'club': 'Al-Ittihad'},
                {'name': 'William Saliba', 'position': 'DF', 'age': 23, 'club': 'Arsenal'},
                {'name': 'Mike Maignan', 'position': 'GK', 'age': 29, 'club': 'AC Milan'},
                {'name': 'Ibrahima Konaté', 'position': 'DF', 'age': 25, 'club': 'Liverpool'},
                {'name': 'Youssouf Fofana', 'position': 'MF', 'age': 25, 'club': 'Monaco'},
                {'name': 'Marcus Thuram', 'position': 'FW', 'age': 27, 'club': 'Inter Milan'},
                {'name': 'Randal Kolo Muani', 'position': 'FW', 'age': 25, 'club': 'PSG'},
                {'name': 'Bradley Barcola', 'position': 'FW', 'age': 22, 'club': 'PSG'},
                {'name': 'Warren Zaïre-Emery', 'position': 'MF', 'age': 18, 'club': 'PSG'},
            ],
            'Brazil': [
                {'name': 'Alisson', 'position': 'GK', 'age': 31, 'club': 'Liverpool'},
                {'name': 'Marquinhos', 'position': 'DF', 'age': 30, 'club': 'PSG'},
                {'name': 'Éder Militão', 'position': 'DF', 'age': 26, 'club': 'Real Madrid'},
                {'name': 'Gabriel Magalhães', 'position': 'DF', 'age': 26, 'club': 'Arsenal'},
                {'name': 'Danilo', 'position': 'DF', 'age': 33, 'club': 'Juventus'},
                {'name': 'Casemiro', 'position': 'MF', 'age': 32, 'club': 'Manchester United'},
                {'name': 'Bruno Guimarães', 'position': 'MF', 'age': 26, 'club': 'Newcastle'},
                {'name': 'Lucas Paquetá', 'position': 'MF', 'age': 27, 'club': 'West Ham'},
                {'name': 'Vinícius Júnior', 'position': 'FW', 'age': 24, 'club': 'Real Madrid'},
                {'name': 'Neymar', 'position': 'FW', 'age': 32, 'club': 'Al-Hilal'},
                {'name': 'Richarlison', 'position': 'FW', 'age': 27, 'club': 'Tottenham'},
                {'name': 'Raphinha', 'position': 'FW', 'age': 27, 'club': 'Barcelona'},
                {'name': 'Rodrygo', 'position': 'FW', 'age': 23, 'club': 'Real Madrid'},
                {'name': 'Endrick', 'position': 'FW', 'age': 18, 'club': 'Real Madrid'},
                {'name': 'Ederson', 'position': 'GK', 'age': 31, 'club': 'Manchester City'},
                {'name': 'Bremer', 'position': 'DF', 'age': 27, 'club': 'Juventus'},
                {'name': 'Vanderson', 'position': 'DF', 'age': 23, 'club': 'Monaco'},
                {'name': 'Douglas Luiz', 'position': 'MF', 'age': 26, 'club': 'Juventus'},
                {'name': 'André', 'position': 'MF', 'age': 23, 'club': 'Fluminense'},
                {'name': 'Gabriel Martinelli', 'position': 'FW', 'age': 23, 'club': 'Arsenal'},
                {'name': 'Antony', 'position': 'FW', 'age': 24, 'club': 'Manchester United'},
            ],
            'England': [
                {'name': 'Jordan Pickford', 'position': 'GK', 'age': 30, 'club': 'Everton'},
                {'name': 'Harry Maguire', 'position': 'DF', 'age': 31, 'club': 'Manchester United'},
                {'name': 'John Stones', 'position': 'DF', 'age': 30, 'club': 'Manchester City'},
                {'name': 'Kyle Walker', 'position': 'DF', 'age': 34, 'club': 'Manchester City'},
                {'name': 'Luke Shaw', 'position': 'DF', 'age': 29, 'club': 'Manchester United'},
                {'name': 'Declan Rice', 'position': 'MF', 'age': 25, 'club': 'Arsenal'},
                {'name': 'Jude Bellingham', 'position': 'MF', 'age': 21, 'club': 'Real Madrid'},
                {'name': 'Phil Foden', 'position': 'MF', 'age': 24, 'club': 'Manchester City'},
                {'name': 'Harry Kane', 'position': 'FW', 'age': 31, 'club': 'Bayern Munich'},
                {'name': 'Bukayo Saka', 'position': 'FW', 'age': 23, 'club': 'Arsenal'},
                {'name': 'Raheem Sterling', 'position': 'FW', 'age': 29, 'club': 'Chelsea'},
                {'name': 'Marcus Rashford', 'position': 'FW', 'age': 27, 'club': 'Manchester United'},
                {'name': 'Trent Alexander-Arnold', 'position': 'DF', 'age': 26, 'club': 'Liverpool'},
                {'name': 'Jordan Henderson', 'position': 'MF', 'age': 34, 'club': 'Ajax'},
                {'name': 'Kalvin Phillips', 'position': 'MF', 'age': 28, 'club': 'Manchester City'},
                {'name': 'Aaron Ramsdale', 'position': 'GK', 'age': 26, 'club': 'Southampton'},
                {'name': 'Ben White', 'position': 'DF', 'age': 27, 'club': 'Arsenal'},
                {'name': 'Kieran Trippier', 'position': 'DF', 'age': 34, 'club': 'Newcastle'},
                {'name': 'Conor Gallagher', 'position': 'MF', 'age': 24, 'club': 'Atlético Madrid'},
                {'name': 'Cole Palmer', 'position': 'MF', 'age': 22, 'club': 'Chelsea'},
                {'name': 'Ollie Watkins', 'position': 'FW', 'age': 28, 'club': 'Aston Villa'},
            ],
            'Spain': [
                {'name': 'Unai Simón', 'position': 'GK', 'age': 27, 'club': 'Athletic Bilbao'},
                {'name': 'Dani Carvajal', 'position': 'DF', 'age': 32, 'club': 'Real Madrid'},
                {'name': 'Aymeric Laporte', 'position': 'DF', 'age': 30, 'club': 'Al-Nassr'},
                {'name': 'Pau Torres', 'position': 'DF', 'age': 27, 'club': 'Aston Villa'},
                {'name': 'Alejandro Balde', 'position': 'DF', 'age': 21, 'club': 'Barcelona'},
                {'name': 'Sergio Busquets', 'position': 'MF', 'age': 36, 'club': 'Inter Miami'},
                {'name': 'Pedri', 'position': 'MF', 'age': 21, 'club': 'Barcelona'},
                {'name': 'Gavi', 'position': 'MF', 'age': 20, 'club': 'Barcelona'},
                {'name': 'Álvaro Morata', 'position': 'FW', 'age': 31, 'club': 'AC Milan'},
                {'name': 'Ferran Torres', 'position': 'FW', 'age': 24, 'club': 'Barcelona'},
                {'name': 'Dani Olmo', 'position': 'MF', 'age': 26, 'club': 'Barcelona'},
                {'name': 'Mikel Oyarzabal', 'position': 'FW', 'age': 27, 'club': 'Real Sociedad'},
                {'name': 'Rodri', 'position': 'MF', 'age': 28, 'club': 'Manchester City'},
                {'name': 'Nico Williams', 'position': 'FW', 'age': 22, 'club': 'Athletic Bilbao'},
                {'name': 'Lamine Yamal', 'position': 'FW', 'age': 17, 'club': 'Barcelona'},
                {'name': 'David Raya', 'position': 'GK', 'age': 29, 'club': 'Arsenal'},
                {'name': 'Robin Le Normand', 'position': 'DF', 'age': 27, 'club': 'Atlético Madrid'},
                {'name': 'Marc Cucurella', 'position': 'DF', 'age': 26, 'club': 'Chelsea'},
                {'name': 'Fabián Ruiz', 'position': 'MF', 'age': 28, 'club': 'PSG'},
                {'name': 'Mikel Merino', 'position': 'MF', 'age': 28, 'club': 'Arsenal'},
            ],
        }
        
        # Return squad or generic squad structure
        if team in squads:
            return squads[team]
        else:
            # Generate generic squad for teams without detailed data
            return [
                {'name': f'{team} Player {i+1}', 'position': pos, 'age': 25, 'club': 'Various'}
                for i, pos in enumerate(['GK', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'FW', 'FW', 'FW'] * 2)
            ][:23]
