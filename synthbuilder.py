import time

import builderelements as e

def mysynth():
    oscA.play_at(-1)

if __name__ == "__main__":
    from random import randint

    while True:
        env = e.Env(attack=0.5)
        oscA = e.SinOsc(freq=randint(300, 500), mul=env)
        oscA.play_at(-1)
        time.sleep(1)

        env.gate = 0
        oscA.play_at(-1)
        time.sleep(1)
