"""Restricted loader for ResPlan.pkl: only the three globals found by the
opcode scan (shapely.io.from_wkb, numpy scalar, numpy dtype) may be imported."""
import pickle, os

PKL = r"C:\Users\lsire\autocad-mcp\reference\datasets\resplan\ResPlan.pkl"
ALLOWED = {
    ("shapely.io", "from_wkb"),
    ("numpy._core.multiarray", "scalar"),
    ("numpy.core.multiarray", "scalar"),
    ("numpy", "dtype"),
}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"blocked global {module}.{name}")


def load():
    with open(PKL, "rb") as f:
        return RestrictedUnpickler(f).load()
