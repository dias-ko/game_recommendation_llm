import pytest
import Levenshtein as lev
from ..comp import cmp_titles
from ..helpers import std
from ..config import *

#test linking by titles
@pytest.mark.parametrize(
    "titles1, titles2, output",
    [
        (
            [
                "Resident Evil 2",
                "Biohazard 2"
            ], 
            [
                "Resident Evil 2",
                "RE2"
            ], 1),
        (
            [
                "Resident Evil 2",
                "Biohazard 2"
            ], 
            [
                "Resident Evil",
                "RE"
            ], 1 - NUMBERING_WEIGHT),
        (
            [
                "FIFA 2015"
            ], 
            [
                "Fifa '16",
                "Fifa football 2016"
            ], 1 - NUMBERING_WEIGHT),
        (
            [
                "Resident Evil 2",
            ], 
            [
                "Resident Evil II",
            ], 1),
    ],    
)
def test_linking_by_titles(titles1, titles2, output):
    assert cmp_titles(titles1, titles2) == output