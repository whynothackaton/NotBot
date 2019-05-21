class Registrar (object):
    def __init__(self):
        self.commands = {}

    def add(self, *args, **kwargs):
        '''
        kwargs
            category[str]-Category
        '''
        print("ARGS1=",args,kwargs)
        def add(command):
            if kwargs['category'] in self.commands:
                self.commands[kwargs['category']].append(command)
            else:
                self.commands[kwargs['category']] = [command]

        return add

    def execute(self, *args, **kwargs):
        '''[summary]

        Keyword Arguments:
            category {[type]} -- [description] (default: {None})
        '''
        print("ARGS2=",args,kwargs)
        category = kwargs['category']
        for command in self.commands[category]:
            command(args, kwargs)
