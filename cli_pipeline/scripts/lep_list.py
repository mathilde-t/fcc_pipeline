LEP_LIST = ["Electron", "Muon"]

OBJECT_LEVEL_HISTS = [
]

# Hists of branches stored once per event, without the "{lep}_" prefix
EVENT_LEVEL_HISTS = [
    "weight",
]

def branch_name(lep, var):
    """Tree branch holding var for the given lepton flavour."""
    return var if var in EVENT_LEVEL_HISTS else f"{lep}_{var}"

def fill_weight(var, selection="weight"):
    """Selection used to fill the hist of var.

    The weight distribution is filled unweighted, so that its y-axis
    counts events; all other hists keep the given (weighted) selection.
    """
    return selection.replace("weight", "1", 1) if var == "weight" else selection
