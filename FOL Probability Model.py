#!/usr/bin/env python
# coding: utf-8

# # UPDATED

# In[1]:


from fractions import Fraction
from itertools import product

class Probability:
    def __init__(self, n, k_list=None,  operator = None, 
                 
                 prob_type="Regular", relation="=", rhs="value",
                 k_list_rhs = None, operator_rhs = None,
                 initial_probability=None, 
                 
                 c_list=None, c_operator=None, 
                 independence_type=None, 
                 i_list=None, i_eq ="indep",
                 
                 ci_list=None, ci_operator=None):
        
        """prob_type: Regular: Union/Intersection"""
        self.n = n
        self.k_list = k_list
        self.operator = operator
        
        self.prob_type = prob_type # Regular/Conditional
        self.relation = relation # =, !=, >, <, >=, <=
        self.rhs = rhs # value/expression
        
        if self.rhs == "value":
            self.probability = initial_probability
        else:
            self.k_list_rhs = k_list_rhs
            self.operator_rhs = operator_rhs
            
            
        
        self.c_list = c_list if prob_type=="Conditional" else None
        self.c_operator = c_operator if prob_type=="Conditional" else None

        # If there are independent events
        self.independence = independence_type # Regular/Conditional
        self.i_list = i_list if independence_type!=None else None
        self.i_eq = i_eq
        
        self.ci_list = ci_list if independence_type == "Conditional" else None
        self.ci_operator = ci_operator if independence_type == "Conditional" else None
        
        if k_list is not None:
            self.k = self._parse_events(k_list) # {'normal': [0], 'complement': [1]}
            self.binary = self.generate_combinations(k_list, n, operator) # [[1, 0, 0], [1, 0, 1]]
            self.name = self.generate_default_name() # A1∩A2c
    
    def _parse_events(self, binary_lst):
        """Parse the list of events to separate normal and complement events."""
        events = {'normal': [], 'complement': []}
        for event in binary_lst:
            event_str = str(event)
            if 'c' in event_str:
                events['complement'].append(int(event_str[0]) - 1)
            else:
                events['normal'].append(int(event_str) - 1)
        return events
    
    def generate_all_combinations(self):
        """Generate all combinations for the number of events.
        e.g. [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]"""
        return list(product([0, 1], repeat=self.n))
    
    def generate_combinations(self, binary_lst, n, operator="Intersection"):
        """Generate valid combinations for the inputted event
        e.g. [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]] """
        
        combinations = list(product([0, 1], repeat=n))
        valid_combinations = []
        parsed_events = self._parse_events(binary_lst)
        
        if operator == "Intersection":
            for combo in combinations:
                if all(combo[idx] == 1 for idx in parsed_events['normal']) and all(combo[idx] == 0 for idx in parsed_events['complement']):
                    valid_combinations.append(tuple(combo))

        elif operator == "Union":
            for combo in combinations:
                # Check if at least one 'normal' is 1 or at least one 'complement' is 0
                if any(combo[idx] == 1 for idx in parsed_events['normal']) or any(combo[idx] == 0 for idx in parsed_events['complement']):
                    valid_combinations.append(tuple(combo))
                    
        unique_valid_combinations = list(set(valid_combinations))  # Now you can use a set because it contains tuples
        return [list(combo) for combo in unique_valid_combinations]

    
# GENERATING EXPRESSIONS
    
    def non_negativity_expression(self):
        """Generate constraints for the probability space."""
        expr_parts = ["x_" + ''.join(map(str, combo)) for combo in self.generate_all_combinations()]
        expression = ', '.join([f"{combo}>=0" for combo in expr_parts])
        return expression
    
    def sum_is_one_expression(self):
        expr_parts = ["x_" + ''.join(map(str, combo)) for combo in self.generate_all_combinations()]
        expression = '+'.join([f"{combo}" for combo in expr_parts])
        return f"{expression}==1"

    def _expr_from_lst(self, lst, expr_operator):
        """given [1,2,3], self.n, self.operator
            1. gets binary rep: [1,1,1]
            2. creates expression: x111"""
            
        binary = self.generate_combinations(lst, self.n, operator=expr_operator) # generate combinations
        if len(binary)==0:
            return "0"
        parts = ["x_" + ''.join(map(str, combo)) for combo in binary]
        expression = " + ".join(parts)
        return expression
    
    def generate_probability_expression(self):
                 
    
        if self.prob_type == "Regular":
            lhs = self._expr_from_lst(self.k_list, self.operator)
            if self.relation == "=":
                self.relation = "=="
                
                
            if self.rhs == "value":
                probability_as_rational = str(Fraction(self.probability).limit_denominator()) if isinstance(self.probability, float) else str(self.probability)
                return f"{lhs} {self.relation} {probability_as_rational}"
            
            else:
                rhs = self._expr_from_lst(self.k_list_rhs, self.operator_rhs)
                return f"{lhs} {self.relation} {rhs}" 
    

        
        elif self.prob_type == "Conditional":
            

            rhs = str(Fraction(self.probability).limit_denominator()) if isinstance(self.probability, float) else str(self.probability)

                
                
                
            k_set = set(tuple(comb) for comb in self.generate_combinations(self.k_list, self.n, self.operator))
            c_set = set(tuple(comb) for comb in self.generate_combinations(self.c_list, self.n, self.c_operator))
            k_intersect_c_combs = list(k_set.intersection(c_set))

            parts = ["x_" + ''.join(map(str, combo)) for combo in k_intersect_c_combs]
            if len(parts) == 0:
                k_c_intersection_expression = "0"
            else:
                k_c_intersection_expression = " + ".join(parts)

            c_expression = self._expr_from_lst(self.c_list, self.c_operator)
            
            if self.relation == "=":
                self.relation = "=="
            return f"{k_c_intersection_expression} {self.relation} ({c_expression})*({rhs})"
        

    def independence_expression(self):
        
        def find_intersection_of_items_of(lst):
                    # Convert each string in the list into a list of elements
            list_of_elements = [item.split('+') for item in lst]
            sets_of_elements = [set(item.strip() for item in sublist) for sublist in list_of_elements]

            intersection_set = sets_of_elements[0]
            for elements_set in sets_of_elements[1:]:
                intersection_set.intersection_update(elements_set)

            return list(intersection_set)
        
        if self.independence == "Regular":
            
            expr_list = []
            for events in self.i_list: 
                opr = events[-1]
                events = events[:-1]
                expr = self._expr_from_lst(events, opr)
                expr_list.append(expr)
                
            intersection_lst = find_intersection_of_items_of(expr_list)
            if len(intersection_lst)==0:
                lhs = "0"
            else:
                lhs = "+".join(f"{i}" for i in intersection_lst)
            
            rhs = "*".join(f"({expr})" for expr in expr_list)
                
            if self.i_eq == "indep":
                return f"{lhs}=={rhs}"
            if self.i_eq == "no":
                return f"{lhs}!={rhs}"
                                    
        
        elif self.independence == "Conditional":
            # lhs 
            i_set = set(tuple(comb) for comb in self.generate_combinations(self.i_list, self.n, "Intersection"))
            ci_set = set(tuple(comb) for comb in self.generate_combinations(self.ci_list, self.n, self.ci_operator))
            i_intersect_ci_combs = list(i_set.intersection(ci_set))
            
            parts = ["x_" + ''.join(map(str, combo)) for combo in i_intersect_ci_combs]
            
            i_ci_intersection_expression = " + ".join(parts) if len(parts)!=0 else "0"

            intersection_conditioned_expr = self._expr_from_lst(self.ci_list, self.ci_operator)
   
            # rhs: expr for the product of pairwise interesections
            pairwise_intersections = []
            
            for event in self.i_list:
                event_set = set(tuple(comb) for comb in self.generate_combinations([event], self.n, "Intersection"))
                ci_set = set(tuple(comb) for comb in self.generate_combinations(self.ci_list, self.n, self.ci_operator))
                event_intersect_ci_combs = list(event_set.intersection(ci_set))

                parts = ["x_" + ''.join(map(str, combo)) for combo in event_intersect_ci_combs]
                event_ci_intersection_expression = " + ".join(parts) if len(parts)!=0 else "0" 
    
                pairwise_intersections.append(event_ci_intersection_expression)       
                
            rhs = "*".join(f"({prob})" for prob in pairwise_intersections)
            
            return f"({i_ci_intersection_expression})*(({intersection_conditioned_expr})^({len(self.i_list)-1}))=={rhs}"
    
    
    def generate_default_name(self):
        """Generate default name based on the events and their complements.
        e.g. A1∪A2c"""
        
        if not self.k['normal'] and not self.k['complement']:
            return "Sample Space"

        operator_symbol = "∩" if self.operator == "Intersection" else "∪"
        name_parts = []

        # Generate parts for normal and complement events
        for event_type in ['normal', 'complement']:
            if self.k[event_type]:
                suffix = 'c' if event_type == 'complement' else ''
                names = [f"A{idx + 1}{suffix}" for idx in self.k[event_type]]
                name_parts.append(operator_symbol.join(names))

        # Join all parts with the operator symbol and return
        return operator_symbol.join(name_parts)
    


# In[2]:


p_example = Probability(
    n=5, 
    k_list=[2, "3c"], 
    operator="Intersection",
    relation = "<=", 
    rhs="expression",
    k_list_rhs = [1,2, "3c"], operator_rhs = "intersection")
    
print("\n Probability expression:")
print(p_example.sum_is_one_expression())   


# In[3]:


def validate_events(events, n):
    """Validate event format and range, convert to desired format."""
    validated_events = []
    for event in events:
        if event.startswith('a'):
            event_suffix = event[1:].rstrip('c')
            is_complement = event.endswith('c')
            if event_suffix.isdigit() and 1 <= int(event_suffix) <= n:
                event_format = f"{event_suffix}c" if is_complement else int(event_suffix)
                validated_events.append(event_format)
            else:
                return False, None
        else:
            return False, None
    return True, validated_events

def user_input():
    print("How many events are in your probability space?")
    n = input("Enter the number of events (n): ")
    while not n.isdigit() or int(n) <= 0:
        print("Please enter a positive integer for n.")
        n = input("Enter the number of events (n): ")
    n = int(n)

    probability_assumptions = []
    prob_instance = Probability(n)
    probability_assumptions.append(prob_instance.non_negativity_expression())
    probability_assumptions.append(prob_instance.sum_is_one_expression())
    
    summary = []
    

    while True:
        print("\n What information would you like to enter?")
        print("1. Enter a statement about probability of events (Their union or intersection)")
        print("2. Enter a conditional probability of events ")
        print("3. Enter a statement about independence of events")
        print("4. List a group of conditionally independent events")
        print("5. Finish entering data")
        choice = input("\nChoose an option (1-5): ")

        if choice == '5':
            break

        if choice == '1':
            print("\nEnter the Left-Hand Side (LHS): Describe the first part of your statement (Later you will be asked to enter the RHS and the relational operator linking them (e.g. =, <)). Include events or probabilities. \nExample: P(a1 ∪ a2c), P(a1)")
            # LHS:     
                
            events_input = input("Please enter one or multiple events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
            valid, events = validate_events(events_input, n)
            while not valid:
                print(f"Invalid or out of range events. Events should be within the range a1 to a{n}.")
                events_input = input("Please enter one or multiple events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                valid, events = validate_events(events_input, n)
            
            
            opr = ""
            operator = "Union"            
            
            if len(events)>1:
                operator = input("Enter the operator for events you've entered ('u' for Union or 'i' for Intersection): ").strip().capitalize()
                while operator not in ['U', 'I']:
                    print("Invalid operator. Please enter 'u' or 'i'.")
                    operator = input("Enter the operator for events you've entered ('u' for Union or 'i' for Intersection): ").strip().capitalize()

                #remapping user input of operator
                opr = "∪" if operator == 'U' else "∩"
                operator = "Union" if operator == 'U' else "Intersection"
    
            events_str = f"{opr}".join(map(str, events_input)) 
            
#           Relation: ______________________________________________________________________________
            
            relation = input("Choose the Relational Operator: Select an operator to describe the relationship between the LHS and RHS. \nEnter one of the following: '=', '!=', '>', '<', '>=', '<=' ").strip().capitalize()
            while relation not in ['=', '!=', '>', '<','>=', '<=']:
                print("Invalid operator. Please enter '=', '!=', '>', '<','>=', or '<='. ")
                relation = input("Choose the Relational Operator: Select an operator to describe the relationship between the LHS and RHS. \nEnter one of the following: '=', '!=', '>', '<', '>=', '<='").strip().capitalize()

        
#           RHS: _________________________________________________________________________________

            rhs_type = input("Define the Right-Hand Side (RHS): Choose the type of RHS. \nEnter 'E' for another expression (like P(a1Ua2)) or 'P' for a probability value (0.34).").strip().lower()
            while rhs_type not in ['e', 'p']:
                print("Invalid operator. Please enter 'e' or 'p'.")
                rhs_type = input("Define the Right-Hand Side (RHS): Choose the type of RHS. \nEnter 'E' for another expression (like P(a1Ua2)) or 'P' for a probability value (0.34).").strip().lower()

            # if rhs is an expression ________________________________________________________________
            if rhs_type == "e":
                
                events_input_rhs = input("Please enter one or multiple events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                valid, events_rhs = validate_events(events_input_rhs, n)
                while not valid:
                    print(f"Invalid or out of range events. Events should be within the range a1 to a{n}.")
                    events_input_rhs = input("Please enter one or multiple events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                    valid, events_rhs = validate_events(events_input_rhs, n)


                opr_rhs = ""
                operator_rhs = "Union"            

                if len(events_rhs)>1:
                    operator_rhs = input("Enter the operator for events you've entered ('u' for Union or 'i' for Intersection): ").strip().capitalize()
                    while operator_rhs not in ['U', 'I']:
                        print("Invalid operator. Please enter 'u' or 'i'.")
                        operator_rhs = input("Enter the operator for events you've entered ('u' for Union or 'i' for Intersection): ").strip().capitalize()

                    #remapping user input of operator
                    opr_rhs = "∪" if operator_rhs == 'U' else "∩"
                    operator_rhs = "Union" if operator_rhs == 'U' else "Intersection"

                events_str_rhs = f"{opr_rhs}".join(map(str, events_input_rhs))
                
                print(f"You have entered P({events_str}){relation}P({events_str_rhs})")
                summary.append(f"P({events_str}){relation}P({events_str_rhs})")
                
                prob_instance = Probability(n=n, k_list = events, operator= operator, relation = relation, rhs="expression", k_list_rhs = events_rhs, operator_rhs= operator_rhs)

                
            # if rhs is a probability value _____________________________________________________________
            else: 
                probability_value = input(f"Enter the probability for P({events_str}){relation}: ")
                while not probability_value.replace('.', '', 1).isdigit() or not (0 <= float(probability_value) <= 1):
                    print("Invalid probability value. Please enter a number between 0 and 1.")
                    probability_value = input(f"Enter the probability for P({events_str}){relation}: ")
                
                print(f"You have entered P({events_str}){relation}{probability_value}")
                summary.append(f"P({events_str}){relation}{probability_value}")

                prob_instance = Probability(n=n, k_list = events, initial_probability = float(probability_value), operator=operator, relation = relation)
                
            probability_assumptions.append(prob_instance.generate_probability_expression())
            
############################################################################################################

        elif choice == '2':

            
            events_input = input("\nPlease enter one or multiple events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
            valid, events = validate_events(events_input, n)
            while not valid:
                print(f"Invalid or out of range events. Events should be within the range a1 to a{n}.")
                events_input = input("Please enter one or multiple events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                
                
            opr = ""
            operator = "Union"            
            
            if len(events)>1:
                operator = input("Enter the operator for events ('u' for Union or 'i' for Intersection): ").strip().capitalize()
                while operator not in ['U', 'I']:
                    print("Invalid operator. Please enter 'u' or 'i'.")
                    operator = input("Enter the operator for events ('u' for Union or 'i' for Intersection): ").strip().capitalize()

                #remapping user input of operator
                opr = "∪" if operator == 'U' else "∩"
                operator = "Union" if operator == 'U' else "Intersection"
    
            events_str = f"{opr}".join(map(str, events_input)) 
            
# __________________________________________________________________________________________________                   
            
            conditioned_events_input = input("Please enter one or multiple GIVEN (conditioning) events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
            valid, conditioned_events = validate_events(conditioned_events_input, n)
            while not valid:
                print(f"Invalid or out of range conditioned events. Events should be within the range a1 to a{n}.")
                conditioned_events_input = input("Please enter one or multiple GIVEN (conditioning) events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                valid, conditioned_events = validate_events(conditioned_events_input, n)
                
                
                
            c_opr = ""
            c_operator = "Union"            
            
            if len(conditioned_events)>1:
                c_operator = input("Enter the operator for given (conditioning) events ('u' for Union or 'i' for Intersection): ").strip().capitalize()
                while c_operator not in ['U', 'I']:
                    print("Invalid operator. Please enter 'u' or 'i'.")
                    c_operator = input("Enter the operator for given (conditioning) events ('u' for Union or 'i' for Intersection): ").strip().capitalize()

                #remapping user input of operator
                c_opr = "∪" if c_operator == 'U' else "∩"
                c_operator = "Union" if c_operator == 'U' else "Intersection"
        
# __________________________________________________________________________________________________                
            relation = input("What is the relation of LHS to RHS, enter a relational operator: ").strip().capitalize()
            while relation not in ['=', '!=', '>', '<','>=', '<=']:
                print("Invalid operator. Please enter '=', '!=', '>', '<','>=', or '<='. ")
                relation = input("Enter a relational operator: ").strip().capitalize()
      # __________________________________________________________          
            events_str = f"{opr}".join(map(str, events_input)) 
            given_str = f"{c_opr}".join(map(str, conditioned_events_input))
            
            probability_value = input(f"Enter a probability value: P({events_str}|{given_str}){relation}:")
            while not probability_value.replace('.', '', 1).isdigit() or not (0 <= float(probability_value) <= 1):
                print("Invalid probability value. Please enter a number between 0 and 1.")
                probability_value = input(f"Enter a probability value: P({events_str}|{given_str}){relation}:")
            
            print(f"You have entered P({events_str}|{given_str}){relation}{probability_value}")
            summary.append(f"P({events_str}|{given_str}){relation}{probability_value}")
            
            prob_instance = Probability(n=n, k_list = events, initial_probability = float(probability_value), operator = operator, relation=relation, prob_type = "Conditional", c_list=conditioned_events, c_operator=c_operator)
            probability_assumptions.append(prob_instance.generate_probability_expression())
            
############################################################################################################

        elif choice == '3':
            event_groups = []  # List to hold groups of events
            just_events = []
            
            #____________________________________________________________________ 
            events_input = input("Enter events separated by commas (e.g., a1,a2,a3c): ").strip().split(',')
            valid, events = validate_events(events_input, n)
            
            if not valid:
                print(f"Invalid or out of range events. Events should be within the range a1 to a{n}.")
                continue
            
            if len(events)>1:
                operator_input = input("Enter the operator for this group ('u' for union, 'i' for intersection): ").strip().lower()
                while operator_input not in ['u', 'i']:
                    print("Error: Operator must be 'u' (union) or 'i' (intersection). Please try again.")
                    operator_input = input("Enter the operator for this group ('u' for union, 'i' for intersection): ").strip().lower()
            else: 
                operator_input = "u"
            
            just_events.append(events)
            events.append("Union" if operator_input == 'u' else "Intersection")

            event_groups.append(events)
            #____________________________________________________________________    

            
            while True:
                events_input = input("Enter events separated by commas (e.g., a1,a2,a3c): ").strip().split(',')
                valid, events = validate_events(events_input, n)

                if not valid:
                    print(f"Invalid or out of range events. Events should be within the range a1 to a{n}.")
                    continue

                if len(events)>1:
                    operator_input = input("Enter the operator for this group ('u' for union, 'i' for intersection): ").strip().lower()
                    while operator_input not in ['u', 'i']:
                        print("Error: Operator must be 'u' (union) or 'i' (intersection). Please try again.")
                        operator_input = input("Enter the operator for this group ('u' for union, 'i' for intersection): ").strip().lower()
                else: 
                    operator_input = "u"
                    
                just_events.append(events)
                events.append("Union" if operator_input == 'u' else "Intersection")

                event_groups.append(events)
                
                
            # ___________________________________________
                continue_input = input("Do you want to continue entering independent events? (yes/no): ")
                if continue_input.lower() != 'yes':
                    print("Returning to the main menu.")
                    break
                    
            
            #____________________________________________________________________ 
            i_eq = input("Enter 'indep' if they are independent or 'no' if they are not independent.")
            def format_independence_statement(event_groups,i_eq):
                formatted_statements = []

                for group in event_groups:
                    # Extract the operator and replace with appropriate symbol
                    operator_symbol = "∪" if group[-1] == 'Union' else "∩"
                    # Remove the operator from the list and process event identifiers
                    events = group[:-1]
                    # Format events with prefix 'a' and handle complements correctly
                    formatted_events = [f"a{event.rstrip('c')}" + ("c" if event.endswith('c') else "") for event in map(str, events)]
                    # Join the events with the operator
                    event_expression = operator_symbol.join(formatted_events)
                    formatted_statements.append(event_expression)

                # Join all group expressions with a comma and add the independence claim
                if i_eq == "indep":
                    final_statement = ', '.join(formatted_statements) + " are independent"
                else: 
                    final_statement = ', '.join(formatted_statements) + " are not independent"
                
                return final_statement
            
            output_statement = format_independence_statement(event_groups,i_eq)
            print(output_statement)
            summary.append(output_statement)
            
            prob_instance = Probability(n=n, i_list=event_groups, i_eq = i_eq, independence_type="Regular")
            probability_assumptions.append(prob_instance.independence_expression())

                    
############################################################################################################

        elif choice == '4':
        
            events_input = input("\nPlease enter one or multiple INDEPENDENT events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
            valid, events = validate_events(events_input, n)
            while not valid:
                print(f"Invalid or out of range events. Events should be within the range a1 to a{n}.")
                events_input = input("Please enter one or multiple INDEPENDENT events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                valid, events = validate_events(events_input, n)
           
            events_str = f"⊥⊥".join(map(str, events_input))
            
            conditioned_events_input = input("Please enter one or multiple GIVEN (conditioning) events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
            valid, conditioned_events = validate_events(conditioned_events_input, n)
            while not valid:
                print(f"Invalid or out of range conditioned events. Events should be within the range a1 to a{n}.")
                conditioned_events_input = input("Please enter one or multiple GIVEN (conditioning) events, separated by commas (e.g., 'a1, a2c'):").strip().split(',')
                valid, conditioned_events = validate_events(conditioned_events_input, n)

            ci_opr = ""
            ci_operator = "Union"            
            
            if len(conditioned_events)>1:
                ci_operator = input("Enter the operator for given (conditioning) events ('u' for Union or 'i' for Intersection): ").strip().capitalize()
                while ci_operator not in ['U', 'I']:
                    print("Invalid operator. Please enter 'u' or 'i'.")
                    ci_operator = input("Enter the operator for given (conditioning) events ('u' for Union or 'i' for Intersection): ").strip().capitalize()

                #remapping user input of operator
                ci_opr = "∪" if ci_operator == 'U' else "∩"
                ci_operator = "Union" if ci_operator == 'U' else "Intersection"
                        
            c_events_str = f"{ci_opr}".join(map(str, conditioned_events_input))   
            
                    
            
            print(f"You have entered {events_str}|{c_events_str}")
            summary.append(f"{events_str}|{c_events_str}")
            
            prob_instance = Probability(n, i_list=events, independence_type="Conditional", ci_list=conditioned_events, ci_operator = ci_operator)
            probability_assumptions.append(prob_instance.independence_expression())
            
############################################################################################################
    
    print("\nYou have entered the following probabilities and assumptions:")
    for assumption in summary:
        print(assumption)
    return probability_assumptions

# Example usage
if __name__ == "__main__":
    assumptions = user_input()


# In[4]:


import re

def variable_mapping(variables):

    mapping = {}
    pattern = re.compile(r'x_([01]+)')

    for var in variables:
        match = pattern.search(var)
        if match:
            binary_string = match.group(1)
            decimal = int(binary_string, 2)
            new_var_name = f"p{decimal}"
            mapping[var] = new_var_name
        else:
            mapping[var] = var

    return mapping

def apply_mapping_to_expressions(expressions, mapping):

    mapped_expressions = []
    for expression in expressions:
        mapped_expression = expression
        for original_var, new_var in mapping.items():
            mapped_expression = re.sub(r'\b{}\b'.format(original_var), new_var, mapped_expression)
        mapped_expressions.append(mapped_expression)
    return mapped_expressions

def extract_variables(expressions):

    pattern = r'[a-z_]\w*'
    variables = set()
    for expression in expressions:
        found_vars = re.findall(pattern, expression)
        variables.update(found_vars)
    return sorted(variables)

def create_combined_cd_query(expressions):

    variables = extract_variables(expressions)
    mapping = variable_mapping(variables)
    mapped_expressions = apply_mapping_to_expressions(expressions, mapping)
    combined_assumptions = ', '.join(mapped_expressions)
    mapped_variables = [mapping[var] for var in variables]
    cd_query = f"CylindricalDecomposition[{{{combined_assumptions}}}, {{{', '.join(mapped_variables)}}}]"
    
    return cd_query

combined_cd_query = create_combined_cd_query(assumptions)
print(assumptions)



from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr

def execute_mathematica_cd(combined_cd_query, kernel_path):
    try:
        session = WolframLanguageSession(kernel_path)
        
        result = session.evaluate(wlexpr(combined_cd_query))
        return result

    except Exception as e:
        print("An error occurred:", e)
        return None

    finally:
        if session:
            session.terminate()

kernel_path = "/Applications/Mathematica.app/Contents/MacOS/MathKernel"
result = execute_mathematica_cd(combined_cd_query, kernel_path)

if result is False: 
    print("There is an inconsistency in your probability assumptions")
else: 
    print("Assumptions are consistent")

