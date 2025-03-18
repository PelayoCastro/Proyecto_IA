import numpy as np
'''
CIAE -> cantidad inicial de agua en el embalse
TEC -> tiempo que tarda el agua en ir desde el embalse a la central
AV_CAEE -> media de la cantidad de agua que entra en el embalse
SD_CAEE -> desviación típica de la cantidad de agua que entra en el embalse
AV_CASE -> media de la cantidad de agua que sale del embalse
SD_CASE -> desviación típica de la cantidad de agua que sale del embalse
ECSE -> estado de la compuerta de la salida del embalse (True -> abierto)
'''

class Central:
    def __init__(self, env, CIAE=300_000, TEC=30, AV_CAEE=10, SD_CAEE=2,
                 AV_CASE=10, SD_CASE=2, ECSE=True):
        self.env = env
        self.TEC = TEC
        self.CIAE = CIAE
        self.AV_CAEE = AV_CAEE
        self.SD_CAEE = SD_CAEE
        self.AV_CASE = AV_CASE
        self.SD_CASE = SD_CASE
        self.ECSE = ECSE
        self.case_historico = []

        self.action = env.process(self.run())

    # Generación de la cantidad de agua que entra en el embalse
    def generate_caee(self):
        return np.random.normal(self.AV_CAEE, self.SD_CAEE)

    # Generación de la cantidad de agua que sale del embalse
    def generate_case(self):
        return np.random.normal(self.AV_CASE, self.SD_CASE)

    def run(self):
        while True:
            print(f'MOMENTO {self.env.now}')
            print(f'Cantidad de agua en el embalse: {self.CIAE}')
            caee = self.generate_caee() # Distribución normal
            print(f'Cantidad de agua entrando en el embalse: {caee}')
            case = self.generate_case() # Distribución normal
            self.case_historico.append(case)
            if self.ECSE and self.CIAE > case:
                print(f'Cantidad de agua saliendo del embalse: {case}')
            '''
            La cantidad de agua abandonando el embalse será asignado al valor de la cantidad de agua entrando en 
            el generador 30 instantes más tarde, que es el tiempo que tarda el agua en avanzar desde el embalse 
            donde se almacena hasta el generador donde es turbinada. 
            '''
            if len(self.case_historico) <= 30:
                print('Cantidad de agua turbinada en la central: 0') # Antes del instante 30
            else:
                print(f'Cantidad de agua turbinada en la central: {self.case_historico[self.env.now - self.TEC]}')
            # Actualización de los valores
            self.CIAE += caee - case
            yield self.env.timeout(1)


