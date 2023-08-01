# Compiler Design Laboratory
 
### Assignment 1: Convert a given regular expression to NFA

#### How to run the program:

```bash
 git clone https://github.com/adihex/CDLAB.git 
 cd CDLAB/
```
- Edit the `inp.json` file to add your desired regular expression.
- Run `python3 regex_DFA.py inp.json out.json`
- The corresponding NFA will be generated in the out.json

Overview
--- 
**Operators:**
- '/' : Union
- '*' : Star
- '#' : Epsilon
- '()' : Grouping

## Approach :

```
1. First add "." symbol for concatenation for convenience in add_concat().
2. Using shunt yard algorithm convert the infix form of the expression to postfix form.
3. An expression tree is created in the create_exp_tree() function from the postfix expression we got
4. We pass the root of the expression tree to eval_regex().
5. According to the operation encountered, we go to the respective function to evaluate it.
6. Each state consists of dictionary containing (input, next state ) pairs.
```