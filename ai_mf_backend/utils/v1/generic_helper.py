class Singleton:
    """
    This class makes sure that the models are loaded into memory only once.
    Also, make sure no value is passed in the init else it will create a new instance everytime
    """

    _instances = {}

    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(
                class_
            )  # pylint:disable
        return class_._instances[class_]
