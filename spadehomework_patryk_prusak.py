from spade.behaviour import State
from spade.message import Message
from spade.behaviour import FSMBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.agent import Agent
import time
import datetime
import random

chanceToInterrupt = 0.8

STATE_COUNT = "STATE_COUNT"
STATE_DISTRACTED = "STATE_DISTRACTED"


class StateCount(State):
    async def run(self):
        messageReceived = await self.receive()
        if messageReceived is not None:

            if 1 == self.agent.id:
                idOfAgentToSend = 2
            else:
                idOfAgentToSend = 1
            if 'distractagent' == str(messageReceived.sender):
                if random.random() < chanceToInterrupt:
                    self.agent.counter = int(messageReceived.body)
                    # time.sleep(4)
                    # toDiscard= await self.receive()
                    # print(toDiscard.body)
                    # await self.send(Message(to="Patryk123@jabb.im/" + str(idOfAgentToSend),
                    #                        body=str(self.agent.counter)))
                    # print("Oh no I(" + str(self.agent.id) + ") got distracted!!!")
                    # print("CounterAgent(" + str(self.agent.id) +
                    # ") claims the counter is: " + str(self.agent.counter))
                    self.set_next_state(STATE_DISTRACTED)
                else:
                    print("NOT TODAY")
            else:
                self.agent.counter = int(messageReceived.body) + 1
                await self.send(Message(to="Patryk123@jabb.im/" + str(idOfAgentToSend),
                                        body=str(self.agent.counter)))
                print("CounterAgent(" + str(self.agent.id) + ") claims the counter is: " + str(self.agent.counter))

                time.sleep(1)
                self.set_next_state(STATE_COUNT)
        else:
            self.set_next_state(STATE_COUNT)


class StateDistracted(State):
    async def run(self):
        messageReceived = await self.receive()
        if messageReceived is not None:
            if 1 == self.agent.id:
                idOfAgentToSend = 2
            else:
                idOfAgentToSend = 1
            print(
                "CounterAgent(" + str(self.agent.id) + ") got distracted and claims the counter is: "
                + str(self.agent.counter))
            await self.send(
                Message(to="Patryk123@jabb.im/" + str(idOfAgentToSend),
                        body=str(self.agent.counter)))
            self.set_next_state(STATE_COUNT)
        else:
            self.set_next_state(STATE_DISTRACTED)
        #time.sleep(1)


class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


class CounterAgent(Agent):
    counter = 0
    id = 0

    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_COUNT, state=StateCount(), initial=True)
        fsm.add_state(name=STATE_DISTRACTED, state=StateDistracted())
        fsm.add_transition(source=STATE_COUNT, dest=STATE_DISTRACTED)
        fsm.add_transition(source=STATE_DISTRACTED, dest=STATE_DISTRACTED)
        fsm.add_transition(source=STATE_DISTRACTED, dest=STATE_COUNT)
        fsm.add_transition(source=STATE_COUNT, dest=STATE_COUNT)
        self.add_behaviour(fsm)


class DistractAgent(Agent):
    async def setup(self):
        start = datetime.datetime.now() + datetime.timedelta(seconds=2)
        self.add_behaviour(self.DistractBehaviour(period=20, start_at=start))

    class DistractBehaviour(PeriodicBehaviour):
        async def run(self):
            await self.send(
                Message(to="Patryk123@jabb.im/" + str(random.randint(1, 2)),
                        body=str(random.randint(1, 100)),
                        sender="DistractAgent"))
            print("Distraction sent")


class AgentOneStart(OneShotBehaviour):
    async def run(self):
        print("CounterAgent(" + str(self.agent.id) + ") claims the counter is: " + str(self.agent.counter))
        await self.send(Message(to="Patryk123@jabb.im/2",
                                body=str(self.agent.counter)))


if __name__ == "__main__":
    counterAgentOne = CounterAgent("Patryk123@jabb.im/1", "123456789")
    counterAgentTwo = CounterAgent("Patryk123@jabb.im/2", "123456789")
    distractAgent = DistractAgent("Patryk123@jabb.im/3", "123456789")
    counterAgentOne.add_behaviour(AgentOneStart())

    counterAgentOne.id = 1
    counterAgentTwo.id = 2

    future2 = counterAgentTwo.start()
    time.sleep(1)

    future1 = counterAgentOne.start()

    future = distractAgent.start()
    future.result()
    future1.result()
    future2.result()
    while distractAgent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            distractAgent.stop()
            counterAgentOne.stop()
            counterAgentTwo.stop()
            break
    print("Agent finished")
