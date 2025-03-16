import simpy
from process import Central

if __name__=='__main__':
    env = simpy.Environment()
    central = Central(env)
    env.run(until=60)
