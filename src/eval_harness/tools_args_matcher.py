from collections.abc import Callable


# a callable that checks whether two dictionaries satisfy a condition
# expressed in a custom function.
class ToolArgsMatcher:
    def __init__(self, function: Callable[[dict, dict], bool]):
        self.function = function

    def __call__(self, output, reference_pattern):
        return self.function(output, reference_pattern)
