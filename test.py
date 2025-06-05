import os
import inspect
mods_folder = "mods"
mods = os.listdir(mods_folder)
def load(name):
    print(name)
    if name.endswith(".py"):
        name = name[:-3]
    mod = __import__(f"{mods_folder}.{name}")
    return getattr(mod, name)
def runfunc(mod, func):
    d = getattr(mod, func)
    exec(inspect.getsource(d))
ex = load('example')
print(dir(ex))
print(ex.ex(1, 8))
