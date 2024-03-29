# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range (self.iterations):
            values_iter=util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state)==True:
                    continue
                max_q=float('-inf')
                for action in self.mdp.getPossibleActions(state):
                    q=self.computeQValueFromValues(state,action)
                    if q>max_q:
                        max_q=q
                values_iter[state]=max_q
            self.values=values_iter


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        q=0
        for next in self.mdp.getTransitionStatesAndProbs(state,action):
            successor=next[0]
            prob=next[1]
            reward=self.mdp.getReward(state,action,successor)
            q=q+prob*(reward+self.discount*self.values[successor])
        return q
        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state)==True:
            return None
        max_q=float('-inf')
        best_action=None
        for action in self.mdp.getPossibleActions(state):
            q=self.computeQValueFromValues(state,action)
            if q>max_q:
                max_q=q
                best_action=action
        return best_action
        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        for i in range (self.iterations):
            states=self.mdp.getStates()
            state_now=states[i%len(states)]
            if self.mdp.isTerminal(state_now)==True:
                continue
            max_q=float('-inf')
            for action in self.mdp.getPossibleActions(state_now):
                q_now=self.computeQValueFromValues(state_now, action)
                if q_now>max_q:
                    max_q=q_now
            self.values[state_now]=max_q

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        pq = util.PriorityQueue()
        predecessors = {s: set() for s in self.mdp.getStates()}

        for s in self.mdp.getStates():
            if self.mdp.isTerminal(s):
                continue

            max_q = -9999999999999
            for action in self.mdp.getPossibleActions(s):
                q = self.computeQValueFromValues(s, action)
                if q > max_q:
                    max_q = q

                for next in self.mdp.getTransitionStatesAndProbs(s, action):
                    if next[1]:
                        predecessors[next[0]].add(s)

            pq.push(s, -abs(max_q - self.values[s]))

        for i in range(self.iterations):
            if pq.isEmpty():
                break
            s = pq.pop()
            if self.mdp.isTerminal(s):
                continue
            actions = self.mdp.getPossibleActions(s)
            self.values[s] = max([self.computeQValueFromValues(s, action) for action in actions])

            for pre in predecessors[s]:
                actions = self.mdp.getPossibleActions(pre)
                q=[self.computeQValueFromValues(pre, action) for action in actions]
                q_max=max(q)
                diff= abs(self.values[pre] - q_max)
                if diff> self.theta:
                    pq.update(pre, -diff)

