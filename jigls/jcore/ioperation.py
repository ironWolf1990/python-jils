import logging
from typing import Callable, Dict, List, Optional
from jigls.jcore.abstract import JAbstractOperation

from jigls.logger import logger

logger = logging.getLogger(__name__)


class OptionalArg(str):
    def __repr__(self):
        return 'OptionalArg("%s")' % self


class JOperation(JAbstractOperation):
    def __init__(
        self,
        name: str,
        inputs: List[str],
        outputs: List[str],
        params: Dict = {},
        fn: Callable = None,
    ):
        super().__init__(name=name, inputs=inputs, outputs=outputs, params=params)
        self.fn: Optional[Callable] = fn

    def Compute(self, inputDict, outputs=None):

        assert self.fn is not None

        inputs = [inputDict[d] for d in self.inputs if not isinstance(d, OptionalArg)]

        optionals = {n: inputDict[n] for n in self.inputs if isinstance(n, OptionalArg) and n in inputDict}

        kwargs = {k: v for d in (self.params, optionals) for k, v in d.items()}

        try:
            result = self.fn(*inputs, **kwargs)
        except:
            result = self.fn(*inputs)

        if len(self.outputs) == 1:
            result = [result]
        elif len(self.outputs) > 1:
            result = [result for _ in range(len(self.outputs))]

        result = zip(self.outputs, result)

        if outputs:
            result = filter(lambda kv: kv[0] in set(outputs), result)

        return dict(result)

    def __call__(self, *args, **kwargs):
        assert self.fn is not None
        return self.fn(*args, **kwargs)

    def __getstate__(self):
        return super().__getstate__().update({"fn": self.fn.__name__ if self.fn else "None"})

    def __repr__(self):
        func_name = self.fn and getattr(self.fn, "__name__", None)
        return "%s(name='%s', needs=%s, provides=%s, fn=%s)" % (
            self.__class__.__name__,
            self.name,
            self.inputs,
            self.outputs,
            func_name,
        )
