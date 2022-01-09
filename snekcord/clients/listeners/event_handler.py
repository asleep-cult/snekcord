import inspect

__all__ = ('EventHandler',)


class EventHandler:
    def __init_subclass__(cls):
        cls._event_handlers_ = []

        for name, func in inspect.getmembers(cls, inspect.isfunction):
            signature = inspect.signature(func, eval_str=True)
            for parameter in signature.parameters.values():
                if parameter.annotation is parameter.empty:
                    continue

                if (
                    inspect.isclass(parameter.annotation)
                    and hasattr(parameter.annotation, '_event_')
                ):
                    cls._event_handlers_.append((name, parameter.annotation))
                    break

    def register_callbacks(self, listener):
        for name, type in self._event_handlers_:
            listener.register_callback(type._event_, getattr(self, name))
