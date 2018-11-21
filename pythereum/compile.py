import multiprocessing

from pythereum.restricted_python import safe_globals, compile_restricted, allowed_functions
from pythereum.restricted_python.Guards import guarded_iter_unpack_sequence
from pythereum.restricted_python.Eval import default_guarded_getiter
from pythereum.restricted_python.PrintCollector import PrintCollector


class CompileContract:
    def __init__(self, code, state_vars=None, *, sender=None, data=None):
        # Allow basic (but safe) python functionality
        self.__globals = safe_globals.copy()

        # Allow specific module functions outside of regular builtins
        self.__globals["__builtins__"].update(allowed_functions)

        # Allow safe usage of 'for' loops
        self.__globals["__builtins__"]["_getiter_"] = default_guarded_getiter
        self.__globals["__builtins__"]["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence

        # Pass state information
        self.__state_vars = {}

        # Allow access to sender and data class
        self.__globals["__builtins__"]["sender"] = sender
        self.__globals["__builtins__"]["data"] = data

        # Allow updating of state variables
        self.__globals["__builtins__"]["state"] = self.update_state_var

        # Allow program to emit logs to keep in history
        self.__emit_log = []
        self.__globals["_print_"] = PrintCollector
        self.__globals["_getattr_"] = None

        # Allow modification of list/dict
        self.__globals["_write_"] = lambda x: x

        self.__code = code
        self.__byte_code = compile_restricted(self.__code, "<string>", "exec")

        if state_vars:
            for var_name, var_value in state_vars.items():
                if isinstance(var_value, (int, str, list, dict)):
                    self.__globals["__builtins__"][var_name] = var_value
                    self.__state_vars[var_name] = var_value

        self.__locals = {}
        exec(self.__byte_code, self.__globals, self.__locals)

        for var_name, var_value in self.__locals.items():
            if var_name in self.__state_vars:
                continue
            if isinstance(var_value, (int, str, list, dict)):
                self.__globals["__builtins__"][var_name] = var_value
                self.__state_vars[var_name] = var_value
            elif callable(var_value):
                self.__globals["__builtins__"][var_name] = var_value

    def update_state_var(self, name=None, value=None):
        if not name and not value:
            return self.__state_vars

        if name in self.__state_vars:
            if not value:
                return self.__state_vars.get(name)
            if isinstance(value, (str, int, list, dict)):
                self.__state_vars[name] = value
                return None
            raise TypeError("State variable must be either 'int' or 'str'")
        raise EnvironmentError("State variable does not exist")

    def emit(self, log):
        if isinstance(log, str):
            self.__emit_log.append(log)

    @property
    def state_variables(self):
        return self.__state_vars

    @property
    def emits(self):
        return self.__emit_log

    @property
    def byte_code(self):
        return self.__byte_code.co_code

    @staticmethod
    def __wrapper(queue, func, *args):
        result = func(*args)
        queue.put(result)
        queue.close()

    def run(self, *args):
        if "main" in self.__locals and callable(self.__locals["main"]):
            queue = multiprocessing.Queue(2)
            proc = multiprocessing.Process(target=self.__wrapper, args=(queue, self.__locals["main"], *args))
            proc.start()
            try:
                ret = queue.get(True, 2)
            except:
                ret = None
            finally:
                proc.terminate()
            if not ret or len(ret) != 2:
                return None
            new_state, emits = ret
            for var_name, var_value in new_state.items():
                self.__state_vars[var_name] = var_value
                self.__globals["__builtins__"][var_name] = var_value
            if emits:
                self.__emit_log.extend(list(filter(None, emits.split("\n"))))
        return None
        pass

    def jsonify(self):
        return {
            "code": self.__code,
            "state_vars": self.__state_vars,
            "emits": self.__emit_log
        }
