import simpy
import random
import os
import datetime

from transaction import transaction_from_dict

from prettytable import PrettyTable

# Specify the Column Names while initializing the Table
myTable = PrettyTable(
    ["Agent", "Date", "Customer Number", "Amount", "Transaction Id"])


ACCOUNT_BALANCE = 10000.0
NUMBER_OF_AGENTS = 7
T_INTER = [30, 300]        # Create an egent every [min, max] seconds
AGENT_BALANCE = [500, 5500]  # create [min, max] balance to allocate to agent
SIM_TIME = 1000            # Simulation time in seconds

# keep record
transactions = []

fname = 'result.txt'

if os.path.exists(fname):
    os.remove(fname)


def write_to_file(info):
    '''
        write stats to file
    '''

   # print(info)

    with open(fname, 'a+') as f:
        f.write(str(info))


class Agent():
    '''
     registered agent, manages his own agent_balance allocated by owner
    '''

    def __init__(self, env, name, allocated_balance: float) -> None:
        self.env = env
        self.name = name
        self.allocated_balance = allocated_balance

        # keep track of this agent allocated balance
        self.agent_balance = simpy.Container(
            env, allocated_balance, init=allocated_balance)

    def perform_sale(self, oab: simpy.Container):
        '''
        agent to peform sale, sell airtime
        oab: owner actual current balance (actual_balance container instance)
        '''

        while True:
            # generate random sale amount, with upper threshold to cater for excess sale amount
            sale_amount = random.randint(50, self.allocated_balance + 30)

            # first check if agent bal is enough to perform request
            if (sale_amount < self.agent_balance.level) and (oab.level > sale_amount):
                # proceed with transaction sale
                if sale_amount < 0:
                    sale_amount = 0

                self.agent_balance.get(amount=sale_amount)

                # update actual balance also
                oab.get(amount=sale_amount)

                write_to_file(
                    f'[Agent: {self.name}] I performed a sale of ${sale_amount} | agent bal now : ${self.agent_balance.level} | owner balance: ${oab.level}\n\n')

                # add transaction history
                trans = {
                    "agent": f"Agent {self.name}",
                    "amount": sale_amount,
                    "transaction_id": str(random.randint(0, 9999)),
                    "date": datetime.datetime.now().isoformat(),
                    "phone_number": f'0778{random.randint(1, 9)}72{random.randint(10, 99)}3'
                }

                t = transaction_from_dict(trans)

                transactions.append(t)

                yield self.env.timeout(random.randint(1, 5))

            else:
                yield self.env.timeout(random.randint(1, 3))

                # insufficient balance, request owner to topup
                write_to_file(
                    f'[Agent: {self.name}] Insufficient balance to perform sale of ${sale_amount}. I have ${self.agent_balance.level},  Please allocate me more funds | owner balance: ${oab.level}\n\n')


class Owner():
    '''
        shop owner, can allocate Y amount to agents
        manages agents
    '''

    def __init__(self, env, oab: simpy.Container, vcb: simpy.Container) -> None:
        self.env = env
        self.oab = oab  # owner actual balance
        self.vcb = vcb  # virtual current balance

    def register_agents(self):
        '''
            register a new agent
        '''

        for i in range(NUMBER_OF_AGENTS):
            yield env.timeout(random.randint(*T_INTER))

            # allocate funds to agent

            agent = self.allocate_funds_to_agent(agent_name=i)

            if agent:
                env.process(agent.perform_sale(self.oab))

    def allocate_funds_to_agent(self, agent_name):
        '''
            allocate funds to an agent
        '''
        vb = self.vcb.level

        to_allocate = random.randint(*AGENT_BALANCE)

        if to_allocate < vb:
            # get amount to allocate
            self.vcb.get(amount=to_allocate)

            write_to_file(
                f'[Agent: {agent_name}] Here i am, I have been allocated ${to_allocate}, current virtual balance: ${self.vcb.level}\n\n')

            # proceed
            return Agent(name=agent_name, env=self.env, allocated_balance=to_allocate)

        else:
            # not enough funds
            write_to_file(
                f'[ERROR] Not enough funds to allocate Agent: {agent_name} | virtual balance: ${vb} | to allocate ${to_allocate}\n\n')
            return None


print('-- SimplexSolutions Retail System --')

env = simpy.Environment()

# hold actual account balance
actual_balance = simpy.Container(env, ACCOUNT_BALANCE, init=ACCOUNT_BALANCE)

# initially hold a copy of the actual balance
virtual_balance = simpy.Container(env, ACCOUNT_BALANCE, init=ACCOUNT_BALANCE)

owner = Owner(env=env, oab=actual_balance, vcb=virtual_balance)

# add process
env.process(owner.register_agents())


# Execute!
env.run(until=SIM_TIME)

print('---- stats ----')

total_agent_sales = 0.0

for t in transactions:
    myTable.add_row([t.agent, t.date, t.phone_number,
                     t.amount, t.transaction_id])

    total_agent_sales += t.amount

print(myTable)

print(f'\n\n[INFO] Total agent sales: ${total_agent_sales}\n\n')

print(
    f'[INFO] Remaing virtual balance: ${virtual_balance.level} | initial balance: ${virtual_balance.capacity}\n\n')

print(
    f'[INFO] Remaing owner balance: ${actual_balance.level} | initial balance: ${actual_balance.capacity}\n\n')

write_to_file(str(myTable))

write_to_file(f'\n\n[INFO] Total agent sales: ${total_agent_sales}\n\n')

write_to_file(
    f'[INFO] Remaing virtual balance: ${virtual_balance.level} | initial balance: ${virtual_balance.capacity}\n\n')

write_to_file(
    f'[INFO] Remaing owner balance: ${actual_balance.level} | initial balance: ${actual_balance.capacity}\n\n')

print('-- Done! --')
