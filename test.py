from tree_hugger.core import PythonParser
pp = PythonParser()
pp.parse_file("GenerateAST.py")
pp.get_all_function_names()
