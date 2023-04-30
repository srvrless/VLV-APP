

# Custom Class for handle the exceptions. 



class EmptyDataError(Exception): # Класс ошики, которая возникает при недостатке данных, передаваемых в функцию
    def __init__(self,*args):
        if args:
            self.mmessage = args[0]
        else:
            self.mmessage = None
    
    def __str__(self):
        if self.message:
            return 'EmptyDataError, {0} '.format(self.message)
        else:
            return 'Important data missed. You should check the way of transmitting args to function'



