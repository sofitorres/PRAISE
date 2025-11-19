import random
from environments import SimulatedEnvironment

class TrucoCard:
    def __init__(self, valor: int, palo: str):
        self.valor = valor        
        self.palo = palo           

    def __repr__(self):
        return f"{self.valor} de {self.palo}"


class TrucoEnvironment(SimulatedEnvironment):

    def __init__(self, num_players: int = 2):
        super().__init__()

        self._num_players = num_players
        self._scores = {1: 0, 2: 0}

        # Estados del juego
        self._mazo = self._initialize_mazo()
        self._mano = {}              
        self._mesa = []             
        self._current_bet = None


    def _initialize_mazo(self):
        palos = ["espadas", "bastos", "oros", "copas"]
        valores = [1,2,3,4,5,6,7,10,11,12]

        mazo = []
        for palo in palos:
            for valor in valores:
                mazo.append(TrucoCard(valor, palo))

        random.shuffle(mazo)
        return mazo
    

    def repartir_cartas(self): 
        "aca va la logica para repartir cartas a los jugadores"
    
        if not self._agents:
            print("No hay agentes registrados para repartir.")
            return

        # Resetear manos
        self._mano = {}

        # Por cada agente, darle 3 cartas
        for agent_id in self._agents:
            self._mano[agent_id] = [self._mazo.pop(), self._mazo.pop(), self._mazo.pop()]

        print("Cartas repartidas correctamente.")


    def get_property(self, agent_id: int, property_name: str) -> dict:

        if agent_id not in self._mano:
            return {}

        response = {"agent": agent_id}

        property_methods = {
            "Mi_Mano": self._get_agent_cards,
            "Puntos_envido": self._calculate_envido_for_agent,
            "scores": lambda _ : self._scores,
        }

        method = property_methods.get(property_name)

        if method:
            response[property_name] = method(agent_id)
        else:
            print(f"Propiedad inválida solicitada: {property_name}")

        return response

  
    def _get_agent_cards(self, agent_id: int):
        return self._mano.get(agent_id, [])


    def _calculate_envido_for_agent(self, agent_id: int) -> int:
        cartas = self._mano.get(agent_id, [])
        return self._calcular_envido(cartas)


    def _calcular_envido(self, cartas) -> int:

        def valor_envido(carta: TrucoCard):
            """Las figuras valen 0, 1 a 7 mantienen su valor."""
            if carta.valor >= 10:
                return 0
            return carta.valor

        # Agrupar por palo
        palos = {}
        for carta in cartas:
            palos.setdefault(carta.palo, []).append(carta)

        mejor = 0

        for palo, lista in palos.items():
            if len(lista) >= 2:
                valores = sorted([valor_envido(c) for c in lista], reverse=True)
                mejor = max(mejor, valores[0] + valores[1] + 20)

        # Si no hay palos repetidos
        if mejor == 0:
            mejor = max(valor_envido(c) for c in cartas)

        return mejor

    def take_action(self, agent_id: int, action_name: str, params: dict = {}):
        """
        A implementar luego: jugar carta, cantar truco, etc.
        """
        print(f"Agente {agent_id} ejecutó acción {action_name} con {params}")

