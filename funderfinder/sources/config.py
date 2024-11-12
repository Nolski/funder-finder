from .gsoc import GSOCFinder
from .numfocus import NumFocusFinder
from .opencollective import OpenCollectiveFinder
from .tidelift import TideliftFinder

PRODUCTION_FINDERS = [
    NumFocusFinder,
    OpenCollectiveFinder,
    TideliftFinder,
    GSOCFinder,
]


