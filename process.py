import numpy as np

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


    def generate_caee(self):
        return np.random.normal(self.AV_CAEE, self.SD_CAEE)

    def generate_case(self):
        return np.random.normal(self.AV_CASE, self.SD_CASE)

    def run(self):
        while True:
            print(f'MOMENTO {self.env.now}')
            print(f'Cantidad de agua en el embalse: {self.CIAE}')
            caee = self.generate_caee()
            print(f'Cantidad de agua entrando en el embalse: {caee}')
            case = self.generate_case()
            self.case_historico.append(case)
            if self.ECSE and self.CIAE > case:
                print(f'Cantidad de agua saliendo del embalse: {case}')
            if len(self.case_historico) <= 30:
                print('Cantidad de agua turbinada en la central: 0')
            else:
                print(f'Cantidad de agua turbinada en la central: {self.case_historico[self.env.now - self.TEC]}')
            # Actualización de los valores
            self.CIAE += caee - case
            yield self.env.timeout(1)


