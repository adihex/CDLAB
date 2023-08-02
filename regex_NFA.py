import json
import sys

non_symbols = ['/', '*', '.', '(', ')']
nfa = {}


class operatorType:
    SYMBOL = 1
    CONCAT = 2
    UNION = 3
    KLEEN = 4

class NFAState:
    def __init__(self):
        self.next_state = {}

class ExpressionTree:

    def __init__(self, operatorType, value=None):
        self.operatorType = operatorType
        self.value = value
        self.left = None
        self.right = None

def create_exp_tree(regexp):
    stack = []
    for c in regexp:
        if c == '/':
            z = ExpressionTree(operatorType.UNION)
            z.right = stack.pop()
            z.left = stack.pop()
            stack.append(z)
        elif c == '.':
            z = ExpressionTree(operatorType.CONCAT)
            z.right = stack.pop()
            z.left = stack.pop()
            stack.append(z)
        elif c == "(" or c == ")":
            continue
        else:
            stack.append(ExpressionTree(operatorType.SYMBOL, c))
    return stack[0]

def higher_precedence(a, b):
    p = ["/", ".", "*"]
    return p.index(a) > p.index(b)

def eval_regex(exp_t):
    if exp_t.operatorType == operatorType.CONCAT:
        return do_concat(exp_t)
    elif exp_t.operatorType == operatorType.UNION:
        return do_union(exp_t)
    elif exp_t.operatorType == operatorType.KLEEN:
        return do_star(exp_t)
    else:
        return eval_symbol(exp_t)

def eval_symbol(exp_t):
    start = NFAState()
    end = NFAState()

    start.next_state[exp_t.value] = [end]
    return start, end

def do_concat(exp_t):
    left_nfa = eval_regex(exp_t.left)
    right_nfa = eval_regex(exp_t.right)

    left_nfa[1].next_state['#'] = [right_nfa[0]]
    return left_nfa[0], right_nfa[1]

def do_union(exp_t):
    start = NFAState()
    end = NFAState()

    first_nfa = eval_regex(exp_t.left)
    second_nfa = eval_regex(exp_t.right)

    start.next_state['#'] = [first_nfa[0], second_nfa[0]]
    first_nfa[1].next_state['#'] = [end]
    second_nfa[1].next_state['#'] = [end]

    return start, end

def do_star(exp_t):
    start = NFAState()
    end = NFAState()

    starred_nfa = eval_regex(exp_t.left)

    start.next_state['#'] = [starred_nfa[0], end]
    starred_nfa[1].next_state['#'] = [starred_nfa[0], end]

    return start, end

def arrange_transitions(state, states_done, symbol_table):
    global nfa

    if state in states_done:
        return

    states_done.append(state)

    for symbol in list(state.next_state):
        if symbol not in nfa['letters']:
            nfa['letters'].append(symbol)
        for ns in state.next_state[symbol]:
            if ns not in symbol_table:
                symbol_table[ns] = sorted(symbol_table.values())[-1] + 1
                q_state = "Q" + str(symbol_table[ns])
                nfa['states'].append(q_state)
            nfa['transition_function'].append(
                ["Q" + str(symbol_table[state]), symbol, "Q" +
                 str(symbol_table[ns])])

        for ns in state.next_state[symbol]:
            arrange_transitions(ns, states_done, symbol_table)

def notation_to_num(str):
    return int(str[1:])

def final_st_dfs():
    global nfa
    for st in nfa["states"]:
        count = 0
        for val in nfa['transition_function']:
            if val[0] == st and val[2] != st:
                count += 1
        if count == 0 and st not in nfa["final_states"]:
            nfa["final_states"].append(st)


def arrange_nfa(fa):
    global nfa
    nfa['states'] = []
    nfa['letters'] = []
    nfa['transition_function'] = []
    nfa['start_states'] = []
    nfa['final_states'] = []
    q_1 = "Q" + str(1)
    nfa['states'].append(q_1)
    arrange_transitions(fa[0], [], {fa[0]: 1})

    # st_num = [notation_to_num(i) for i in nfa['states']]

    nfa["start_states"].append("Q1")
    # nfa["final_states"].append("Q" + str(sorted(st_num)[-1]))
    # final_st_dfs(nfa["final_states"][0])
    final_st_dfs()


def add_concat(regex):
    global non_symbols
    len_reg = len(regex)
    res = []
    for i in range(len_reg-1):
        res.append(regex[i])
        if regex[i] not in non_symbols:
            if regex[i+1] not in non_symbols or regex[i+1] == '(':
                res += '.'
            elif regex[i] == ')' and regex[i+1] == '(':
                res += '.'
            elif regex[i] == '*' and regex[i+1] == '(':
                res += '.'
            elif regex[i] == '*' and regex[i+1] not in non_symbols:
                res += '.'
            elif regex[i] == ')' and regex[i+1] not in non_symbols:
                res += '.'

    res += regex[len_reg-1]
    return res


def compute_postfix(regexp):
    stk = []
    res = ""

    for c in regexp:
        if c not in non_symbols or c == "*":
            res += c
        elif c == ")":
            while len(stk) > 0 and stk[-1] != "(":
                res += stk.pop()
            stk.pop()
        elif c == "(":
            stk.append(c)
        elif len(stk) == 0 or stk[-1] == "(" or higher_precedence(c, stk[-1]):
            stk.append(c)
        else:
            while len(stk) > 0 and stk[-1] != "(" and \
                    not higher_precedence(c, stk[-1]):
                res += stk.pop()
            stk.append(c)

    while len(stk) > 0:
        res += stk.pop()

    return res


def postfix_regex(regex):
    reg = add_concat(regex)
    regg = compute_postfix(reg)
    return regg


def read_regexp():
    with open(sys.argv[1], 'r') as inpjson:
        regex = json.loads(inpjson.read())
    return regex


def epsilon_closure(state, epsilon_transitions):
    closure = set()
    stack = [state]
    while stack:
        current_state = stack.pop()
        closure.add(current_state)
        for transition in epsilon_transitions:
            if transition[0] == current_state and transition[1] == '#'\
                    and transition[2] not in closure:
                stack.append(transition[2])
    return closure

def convert_epsilon_nfa_to_nfa(epsilon_nfa):
    epsilon_transitions = [(src, letter, dest) for src, letter, dest in epsilon_nfa['transition_function'] if letter == '#']

    # Calculate epsilon closures for all states
    epsilon_closures = {state: epsilon_closure(state, epsilon_transitions) \
            for state in epsilon_nfa['states']}
    # print(epsilon_closure)
    # for state in epsilon_nfa['states']:
        # print(f"Epsilon closure of {state}: {epsilon_closures[state]}")
    # Construct the new NFA
    global nfa
    nfa = {
        'states': sorted(list(epsilon_nfa["states"])),
        'alphabet': [letter for letter in epsilon_nfa['letters'] if letter != '#'],
        'transition_function': [],
        'start_states': epsilon_nfa['start_states'],
        'final_states': set(epsilon_nfa['final_states'])
    }

    for state in sorted(list(epsilon_nfa["states"])):
        for letter in nfa['alphabet']:
            target_states = epsilon_closures[state]
            # print(state, " -> ",letter," - ",target_states," - ")
            input_states = set()
            ans_states = set()
            for t_state in list(target_states):
                for transition in epsilon_nfa['transition_function']:
                    if transition[0] == t_state and transition[1] == letter:
                        input_states.add(transition[2])
                        # print(input_states,"-> ","add")


            # print(input_states)

            for i_state in input_states:
                ans_states=ans_states.union(set(epsilon_closures[i_state]))
            for a_state in ans_states:
                nfa['transition_function'].append((state, letter, a_state))
    for state in epsilon_nfa['states']:
        if(len(epsilon_closures[state].intersection(set(nfa['final_states'])))>0):
            nfa['final_states'].add(state)

     
    final_nfa = {
        'states': (list(nfa["states"])),
        'letters': [letter for letter in epsilon_nfa['letters'] if letter != '#'],
        'transition_function': nfa['transition_function'],
        'start_states': list(nfa['start_states']),
        'final_states': list(nfa['final_states'])
    }
    return final_nfa

def output_nfa(arg,file):
    with open(sys.argv[file], 'w') as outjson:
        outjson.write(json.dumps(arg, indent=4))


if __name__ == "__main__":
    r = read_regexp()
    reg = r['regex']
    pr = postfix_regex(reg)
    et = create_exp_tree(pr)
    fa = eval_regex(et)
    arrange_nfa(fa)
    global final_nfa
    #print Epsilon-nfa
    output_nfa(nfa,2)
    final_nfa=convert_epsilon_nfa_to_nfa(nfa)
    output_nfa(final_nfa,3)
