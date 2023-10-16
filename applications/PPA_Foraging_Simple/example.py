import time

from applications.PPA_Foraging_Simple.agents import Agent, SAMPLE_TIME


def main():
    goal_position = [5, 4]

    class NewAgent(Agent):

        def control(self):
            super().control()
            self.setInput([0.1,0])

    agent = NewAgent()
    agent.setPosition([0, 0])
    agent.setGoalPosition(goal_position)


    for i in range(0, 100):
        agent.update()
        print(agent.state)
        time.sleep(SAMPLE_TIME)




if __name__ == '__main__':
    main()