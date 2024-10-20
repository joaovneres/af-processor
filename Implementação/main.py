import argparse

class Automaton:
    def __init__(self):
        self.states = []  # Lista de estados
        self.terminals = []  # Lista de terminais (alfabeto)
        self.initial_states = []  # Lista de estados iniciais
        self.final_states = []  # Lista de estados finais
        self.transitions = {}  # Dicionário de transições
        self.input_strings = []  # Lista de cadeias de entrada

    def read_input(self, input_file):
        """Lê o arquivo de entrada e inicializa o autômato."""
        with open(input_file, 'r') as file:
            lines = file.readlines()

        index = 0

        # Leitura do número de estados
        num_states = int(lines[index].strip())
        
        self._validate_max_number(num_states, 10, "O número de estados")
        
        self.states = [f'q{i}' for i in range(num_states)]
        index += 1

        # Leitura dos terminais (alfabeto)
        input_data = lines[index].strip().split()
        num_terminals = int(input_data[0])
        
        self._validate_max_number(num_terminals, 10, "O número de símbolos terminais")
        
        self.terminals = input_data[1:num_terminals + 1]
        index += 1

        # Leitura dos estados iniciais
        num_initial_states = int(lines[index].strip())
        
        self._validate_max_number(num_initial_states, num_states, "O número de estados iniciais")
        
        self.initial_states = [f'q{i}' for i in range(num_initial_states)]
        self._validate_initial_states()  # Verifica se os estados iniciais estão definidos em Q
        index += 1

        # Leitura dos estados finais
        final_states_input = lines[index].strip().split()
        num_final_states = int(final_states_input[0])

        self._validate_max_number(num_final_states, num_states, "O número de estados finais")        
        
        self.final_states = [f'q{int(i)}' for i in final_states_input[1:num_final_states + 1]]
        self._validate_final_states()  # Verifica se os estados finais estão definidos em Q
        index += 1

        # Leitura das transições
        n_transitions = int(lines[index].strip())

        self._validate_max_number(n_transitions, 50, "O número de transições")
        
        index += 1
        self.transitions = {state: {} for state in self.states}

        for i in range(n_transitions):
            transition = lines[index + i].strip().split()
            q, symbol, q_next = '', '', ''
            if len(transition) == 3:
                q = f'q{transition[0]}'  # Estado origem
                symbol = transition[1]  # Símbolo da transição
                q_next = f'q{transition[2]}'  # Estado destino
                
                if q not in self.states or q_next not in self.states:
                    raise ValueError(f"Erro: Estados '{q}' ou '{q_next}' não definidos em Q.")
                if (symbol not in self.terminals) and (symbol != '-'):
                    raise ValueError(f"Erro: Terminal '{symbol}' não previsto em Σ.")
            elif transition[0] == "-":
                # Caso em que temos uma cadeia vazia
                symbol = '-'
                self.transitions[symbol] = {}

            # Adiciona a transição
            if symbol not in self.transitions[q]:
                self.transitions[q][symbol] = []
            self.transitions[q][symbol].append(q_next)

        index += n_transitions

        # Leitura das cadeias de entrada
        n_input_strings = int(lines[index].strip())

        self._validate_max_number(n_input_strings, 10, "O número de cadeias de entrada")        
        
        for i in range(n_input_strings):
            line = lines[index + i + 1].strip()
            
            # Validação de comprimento da string
            self._validate_max_number(len(line), 20, "O comprimento da cadeia de entrada")

            self.input_strings.append(line)
            
    def _validate_max_number(self, number, max_number, message):
        """Verifica se o número é menor ou igual ao máximo permitido."""
        if number > max_number:
            raise ValueError(f"Erro: {message} não pode ser maior que {max_number}.")
        
    def _validate_initial_states(self):
        """Verifica se os estados iniciais estão definidos no conjunto de estados."""
        for state in self.initial_states:
            if state not in self.states:
                raise ValueError(f"Erro: Estado inicial '{state}' não definido no conjunto de estados.")

    def _validate_final_states(self):
        """Verifica se os estados finais estão definidos no conjunto de estados."""
        for state in self.final_states:
            if state not in self.states:
                raise ValueError(f"Erro: Estado final '{state}' não definido no conjunto de estados.")

    def lambda_closure(self, states):
        """Retorna o fecho-lambda (conjunto de estados alcançáveis via lambda-transições)."""
        stack = states[:]
        closure = set(states)

        while stack:
            state = stack.pop()
            if '-' in self.transitions[state]:
                for next_state in self.transitions[state]['-']:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)

        return list(closure)

    def is_valid(self, string):
        """Verifica se uma cadeia é aceita ou rejeitada pelo autômato."""
        current_states = self.lambda_closure(self.initial_states)  # Fecho-lambda dos estados iniciais

        if string == '-':
        # Verificar se o símbolo '-' está presente nas transições se estiver, a cadeia vazia é aceita
        # Ou se algum estado inicial é final, a cadeia vazia é aceita
            if ('-' in self.transitions) or any(state in self.final_states for state in current_states):
                return True
            
        for symbol in string:
            next_states = []
            for state in current_states:
                if symbol in self.transitions[state]:
                    for next_state in self.transitions[state][symbol]:
                        next_states.extend(self.lambda_closure([next_state]))
            current_states = list(set(next_states))  # Atualiza os estados atuais, removendo duplicatas

        # Verifica se algum dos estados atuais é final
        return any(state in self.final_states for state in current_states)

    def evaluate_strings(self):
        """Avalia todas as cadeias de entrada e retorna se são aceitas ou rejeitadas."""
        results = []
        for input_string in self.input_strings:
            if self.is_valid(input_string):
                results.append("aceita")
            else:
                results.append("rejeita")
        return results

    def write_output(self, output_file, results):
        """Escreve os resultados no arquivo de saída."""
        with open(output_file, 'w') as file:
            for result in results:
                file.write(f"{result}\n")

def main():
    parser = argparse.ArgumentParser(description="Process an input file for automaton simulation.")
    parser.add_argument("input_file", nargs="?", help="Input file containing the automaton strings", default="entrada.txt")
    parser.add_argument("output_file", nargs="?", help="Output file to write the results", default="saida.txt")

    args = parser.parse_args()

    try:
        automaton = Automaton()
        automaton.read_input(args.input_file)
        results = automaton.evaluate_strings()
        automaton.write_output(args.output_file, results)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()